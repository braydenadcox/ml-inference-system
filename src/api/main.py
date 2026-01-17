from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from src.api.schemas import PredictRequest, PredictResponse
from src.model.loader import ModelLoader

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
    
@app.post("/predict")
def predict(req: PredictRequest):
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return PredictResponse(
        request_id=req.request_id,
        decision="review",
        risk_score=0.5,
        model_version=model_loader.metadata["model_version"],
        processed_at=datetime.now(timezone.utc),
    )