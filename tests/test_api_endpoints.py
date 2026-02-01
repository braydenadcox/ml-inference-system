"""
Integration tests for API endpoints.

These tests verify that all endpoints behave correctly:
- /health always returns 200
- /ready returns correct status based on model state
- /model returns model metadata
- /predict handles valid/invalid requests correctly
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, model_loader

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_module():
    """Load the model before running tests."""
    model_loader.load_active_model()
    yield
    

def test_health_endpoint_gives_200():
    """Test that the /health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_gives_200_when_model_loaded():
    """Test that the /ready endpoint returns 200 OK when model is loaded."""
    model_loader.is_loaded = True  # Simulate model loaded
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_model_endpoint_returns_metadata():
    """Test that the /model endpoint returns model metadata."""
    valid_request = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "event_time": "2026-01-31T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 100.0,
            "currency": "USD",
            "country": "US",
            "merchant_category": "electronics",
            "device_type": "mobile"
        }
    }

    response = client.get("/model")
    assert response.status_code == 200

    data = response.json()
    assert "model_version" in data
    assert data["model_version"] == "v1"


def test_predict_invalid_uuid_returns_400():
    """Test that /predict returns 400 for invalid UUID in request_id."""
    invalid_request = {
        "request_id": "invalid-uuid",
        "event_time": "2026-01-31T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 100.0,
            "currency": "USD",
            "country": "US",
            "merchant_category": "electronics",
            "device_type": "mobile"
        }
    }

    response = client.post("/predict", json=invalid_request)
    assert response.status_code == 400
    
    data = response.json()
    assert data["code"] == "validation_error"
    assert "field_errors" in data


def test_predict_negative_amount_returns_400():
    """Test that /predict returns 400 for negative transaction amount."""
    invalid_request = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "event_time": "2026-01-31T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": -50.0,  # Invalid negative amount
            "currency": "USD",
            "country": "US",
            "merchant_category": "electronics",
            "device_type": "mobile"
        }
    }

    response = client.post("/predict", json=invalid_request)
    assert response.status_code == 400


def test_predict_normalizes_input():
    """Test that /predict normalizes input data correctly."""
    request = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "event_time": "2026-01-31T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 100.0,
            "currency": "usd",  # Expected to get to "USD"
            "country": "us",    # Expected to get to "US"
            "merchant_category": "Electronics",  # Expected to get to 'electronics'
            "device_type": "", # Expected to get to 'unknown'
        }
    }

    response = client.post("/predict", json=request)
    assert response.status_code == 200


def test_metrics_endpoint_returns_prometheus_format():
    """Test that the /metrics endpoint returns Prometheus formatted metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200

    content = response.text
    assert "# HELP" in content
    assert "# TYPE" in content
    assert "model_loaded" in content