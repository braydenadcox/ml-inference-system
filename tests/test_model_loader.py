"""
Unit tests for model loading logic.

These tests verify that the Model Loader loads valid models, fails properly when anything is
missing, and correctly reports metadata.
"""

import pytest
from pathlib import Path
from src.model.loader import ModelLoader


def test_load_valid_model():
    """Test that a valid model loads correctly."""
    loader = ModelLoader()
    loader.load_active_model()

    assert loader.is_loaded == True
    assert loader.model is not None
    assert loader.metadata is not None
    assert loader.metadata.get("model_version") == 'v1'


def test_model_loader_fails_when_active_config_missing(tmp_path):
    """Test that the model loader fails when the active model config is missing."""
    loader = ModelLoader(models_dir="models", config_dir=str(tmp_path))

    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_active_model()

    assert "Active model configuration file not found" in str(exc_info.value)


def test_model_loader_fails_when_model_file_missing(tmp_path):
    """Test that the model loader fails when the model file is missing."""
    # Create an active model config that points to a non-existent model file
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    config_file = config_dir / "active_model.json"
    config_file.write_text('{"active_model_version": "missing"}')

    loader = ModelLoader(models_dir="models", config_dir=str(config_dir))

    with pytest.raises(FileNotFoundError) as exc_info:
        loader.load_active_model()

    assert "not found" in str(exc_info.value).lower()


def test_model_loader_metadata_accessible():
    """Test that model metadata is accessible after loading."""
    loader = ModelLoader()
    loader.load_active_model()
    
    metadata = loader.get_metadata()
    assert metadata is not None
    assert "model_version" in metadata