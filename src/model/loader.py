import json
import pickle
from pathlib import Path
from typing import Optional

class ModelLoader:
    """Loads and manages the active ML model."""

    def __init__(self, models_dir: str = "models", config_dir: str = "configs"):
        self.models_dir = Path(models_dir)
        self.config_dir = Path(config_dir)
        
        # These will hold the active model and its metadata
        self.model = None
        self.metadata = None
        self.is_loaded = False


    def load_active_model(self):
        """Loads the active model given in active_model.json"""
        active_config_path = self.config_dir / "active_model.json"
        if not active_config_path.exists():
            raise FileNotFoundError(f"Active model config not found at {active_config_path}")
        
        with open(active_config_path, 'r') as f:
            config = json.load(f)

        active_version = config.get("active_model_version")
        if not active_version:
            raise ValueError("Active version not specified in config")


    def predict(self, input_data):
        """Makes a prediction using the loaded model."""
        if not self.is_loaded:
            raise RuntimeError("No model is loaded")
        return self.model.predict(input_data)
