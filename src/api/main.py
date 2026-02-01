from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from src.api.schemas import PredictRequest, PredictResponse, ErrorResponse, FieldError
from src.model.loader import ModelLoader
from src.model.normalize import normalize_request
from src.model.features import build_features


app = FastAPI()

# Global model loader instance
model_loader = ModelLoader()

@app.on_event("startup")
def startup_event():
    """Event handler for application startup to load the active model."""
    try:
        model_loader.load_active_model()
        print("Model loaded successfully on startup.")
    except Exception as e:
        print(f"Error loading model on startup: {e}")

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

    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    req = normalize_request(req)

    features_df = build_features(req)
    print(features_df)
    print(features_df.dtypes)

    return PredictResponse(
        request_id=req.request_id,
        decision="review",
        risk_score=0.5,
        model_version=model_loader.metadata["model_version"],
        processed_at=datetime.now(timezone.utc),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for request validation errors."""
    field_errors = []
    for error in exc.errors():
        loc = error.get('loc', [])
        field = ".".join(str(x) for x in loc if x != 'body')
        issue = error.get('msg', 'Invalid request')
        field_errors.append(FieldError(field=field, issue=issue))

    payload = ErrorResponse(
        code="validation_error",
        message="Invalid request",
        field_errors=field_errors,
    )

    return JSONResponse(
        status_code=400,
        content=payload.model_dump(),
    )