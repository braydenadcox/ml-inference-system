from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from datetime import datetime, timezone
from src.api.logging_config import logger
from src.api.schemas import PredictRequest, PredictResponse, ErrorResponse, FieldError
from src.api.metrics import (
    requests_total,
    responses_total,
    invalid_requests_total,
    inference_failures_total,
    latency_ms,
    model_loaded
)
from src.model.loader import ModelLoader
from src.model.normalize import normalize_request
from src.model.features import build_features
from src.model.decision import map_decision
import logging
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

logger = logging.getLogger("ml_inference_system")
logging.basicConfig(level=logging.INFO)

# Global model loader instance
model_loader = ModelLoader()

@app.on_event("startup")
async def startup_event():
    """Event handler for application startup to load the active model."""
    global model_loader
    model_loader = ModelLoader()

    try:
        model_loader.load_active_model()
        logger.info(f"Model loaded successfully at startup: {model_loader.metadata.get('model_version', 'unknown')}")
        model_loaded.set(1)
    except Exception as e:
        logger.error(f"Failed to load model at startup: {str(e)}")
        model_loaded.set(0)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/ready")
def ready():
    """Readiness check endpoint."""
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}
    
@app.get("/model")
def get_model_info():
    """Endpoint to get information about the loaded model."""
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return model_loader.metadata
    

@app.post("/predict",
          response_model=PredictResponse,
          responses={400: {
              "model": ErrorResponse,
              "description": "Validation error (bad request)"}
              }
            )
def predict(req: PredictRequest):
    start_time = time.time()
    
    # Count request
    requests_total.labels(endpoint="/predict", method="POST").inc()
    
    try:
        if not model_loader.is_loaded:
            logger.error(f"Model not loaded for request_id={req.request_id}")
            inference_failures_total.inc()
            responses_total.labels(endpoint="/predict", status_code="503").inc()
            raise HTTPException(status_code=503, detail="Model not loaded")

        req = normalize_request(req)
        features_df = build_features(req)

        try:
            risk_proba = model_loader.model.predict_proba(features_df)
            risk_score = float(risk_proba[0][1])

            if not (0.0 <= risk_score <= 1.0):
                raise ValueError(f"Predicted risk score is out of range: {risk_score}")
            
        except Exception as e:
            logger.error(
                f"Inference error for request_id={req.request_id}: {str(e)}",
                extra={
                    "request_id": req.request_id,
                    "transaction_id": req.transaction.transaction_id,
                    "error_type": type(e).__name__
                }
            )
            inference_failures_total.inc()
            responses_total.labels(endpoint="/predict", status_code="503").inc()
            raise HTTPException(status_code=503, detail=f"Inference failed: {str(e)}")
        
        decision = map_decision(risk_score)
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        # Log successful prediction
        logger.info(
            f"Prediction successful",
            extra={
                "request_id": req.request_id,
                "transaction_id": req.transaction.transaction_id,
                "model_version": model_loader.metadata.get("model_version"),
                "decision": decision,
                "risk_score": risk_score,
                "latency_ms": round(latency, 2)
            }
        )
        
        # Record metrics
        latency_ms.labels(endpoint="/predict").observe(latency)
        responses_total.labels(endpoint="/predict", status_code="200").inc()
        
        return PredictResponse(
            request_id=req.request_id,
            decision=decision,
            risk_score=risk_score,
            model_version=model_loader.metadata.get("model_version", "unknown"),
            processed_at=datetime.now(timezone.utc)
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (already logged above)
        raise
    except Exception as e:
        # Catch any unexpected errors
        logger.error(
            f"Unexpected error in /predict: {str(e)}",
            extra={"request_id": req.request_id if 'req' in locals() else "unknown"}
        )
        responses_total.labels(endpoint="/predict", status_code="500").inc()
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for request validation errors."""
    field_errors = []
    for error in exc.errors():
        loc = error.get('loc', [])
        field = ".".join(str(x) for x in loc if x != 'body')
        issue = error.get('msg', 'Invalid request')
        field_errors.append(FieldError(field=field, issue=issue))
        
        # Count invalid request by reason
        invalid_requests_total.labels(reason=field).inc()
    
    # Log validation error
    logger.warning(
        f"Validation error: {len(field_errors)} field(s) invalid",
        extra={"field_errors": field_errors}
    )
    
    # Count 400 response
    responses_total.labels(endpoint="/predict", status_code="400").inc()
    
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            code="validation_error",
            message="Invalid request",
            field_errors=field_errors
        ).model_dump()
    )