"""
Unit tests for validation request.

These tests verify that the Pydantic models are correctly rejecting invalid inputs
and accepting valid ones per DESIGN.md specifications.
"""
import pytest
from pydantic import ValidationError
from src.api.schemas import PredictRequest, Transaction

def test_valid_predict_request():
    """Test that a valid PredictRequest passes validation."""
    valid_request = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "event_time": "2026-01-30T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
            "merchant_category": "electronics",
            "device_type": "mobile",
        }
    }

    # Should not raise any ValidationError here.
    request = PredictRequest(**valid_request)
    assert request.request_id == "123e4567-e89b-12d3-a456-426614174000"
    assert request.transaction.amount == 150.0


def test_invalid_predict_request_missing_field():
    """Test a PredictRequest missing a UUID field."""
    invalid_request = {
        "request_id": "not-valid-uuid", # This is the invalid part. Not a real UUID.
        "event_time": "2026-01-30T10:00:00Z",
        "transaction": {
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 150.0,
            "currency": "USD",
            "country": "US",
        } 
    }

    with pytest.raises(ValidationError) as exc_info:
        PredictRequest(**invalid_request)

    errors = exc_info.value.errors()
    assert any("request_id" in str(e) for e in errors)


    def test_invalid_amount_transaction():
        """Test a Transaction with zero amount."""
        invalid_transaction = {
            "request_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_time": "2026-01-30T10:00:00Z",
            "transaction": {
                "transaction_id": "txn_002",
                "user_id": "user_456",
                "amount": 0.0,  # Invalid: Transaction amount should be greater than 0. 
                "currency": "USD",
                "country": "US",
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            Transaction(**invalid_transaction)

        errors = exc_info.value.errors()
        assert any("amount" in str(e) for e in errors)


    def test_invalid_country_code():
        """Test a Transaction with invalid country code."""
        invalid_transaction = {
            "request_id": "123e4567-e89b-12d3-a456-426614174000",
            "event_time": "2026-01-30T10:00:00Z",
            "transaction": {
                "transaction_id": "txn_003",
                "user_id": "user_789",
                "amount": 100.0,
                "currency": "USD",
                "country": "USA",  # Invalid country code
            }
        }

        with pytest.raises(ValidationError) as exc_info:
            Transaction(**invalid_transaction)

        errors = exc_info.value.errors()
        assert any("country" in str(e) for e in errors)