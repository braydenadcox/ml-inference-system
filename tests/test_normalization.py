"""
Unit tests for normalization functions.

These tests make sure the nromalize_request function behaves as expected. This includes:
Removing whitespace and change casing for string fields and 
filling missing optional fields with default values.
"""

from src.api.schemas import PredictRequest
from src.model.normalize import normalize_request

def test_normalize_currency_uppercase():
    """Test that currency codes are normalized to uppercase."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "txn_001",
            "user_id": "user_123",
            "amount": 100.0,
            "currency": "usd", # Lowercase, should highlight this
            "country": "us" # Lowercase, should highlight this
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.currency == "USD"
    assert normalized.transaction.country == "US"



def test_normalize_merchant_category_lowercase():
    """Test that merchant category is normalized to lowercase."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "txn_002",
            "user_id": "user_456",
            "amount": 200.0,
            "currency": "EUR",
            "country": "DE",
            "merchant_category": " ELECTRONICS " # Uppercase with spaces
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.merchant_category == "electronics"


def test_normalize_device_type_lowercase():
    """Test that device type is normalized to lowercase."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "txn_003",
            "user_id": "user_789",
            "amount": 300.0,
            "currency": "GBP",
            "country": "UK",
            "device_type": " DESKTOP " # Uppercase with spaces
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.device_type == "desktop"


def test_empty_device_type_becomes_unknown():
    """Test that empty device type is set to 'unknown'."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "txn_004",
            "user_id": "user_101",
            "amount": 400.0,
            "currency": "CAD",
            "country": "CA",
            "device_type": "   " # Empty after stripping spaces
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.device_type == "unknown"


def test_normalize_strips_transaction_id():
    """Test that transaction_id is stripped of whitespace."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "  txn_005  ", # Leading and trailing spaces
            "user_id": "user_112",
            "amount": 500.0,
            "currency": "AUD",
            "country": "AU"
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.transaction_id == "txn_005"



def test_normalize_strips_user_id():
    """Test that user_id is stripped of whitespace."""
    request = PredictRequest(
        request_id="123e4567-e89b-12d3-a456-426614174000",
        event_time="2026-01-30T10:00:00Z",
        transaction={
            "transaction_id": "txn_006",
            "user_id": "  user_113  ", # Leading and trailing spaces
            "amount": 600.0,
            "currency": "NZD",
            "country": "NZ"
            }
        )
    
    normalized = normalize_request(request)
    assert normalized.transaction.user_id == "user_113"