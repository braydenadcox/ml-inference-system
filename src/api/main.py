from fastapi import FastAPI
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
    if model_loader.is_loaded:
        return {"status": "ready"}
    else:
        return {"status": "not ready"}, 503
    
@app.get("/model")
def get_model_info():
    """Endpoint to get information about the loaded model."""
    metadata = model_loader.metadata
    if metadata:
        return metadata
    else:
        return {"error": "No model loaded"}, 503
    
@app.post("/predict")
def predict():
    # PLACEHOLDER
    return {"message": "Prediction endpoint not implemented yet."}