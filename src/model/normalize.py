from src.api.schemas import PredictRequest

def normalize_request(req: PredictRequest) -> PredictRequest:
    """Normalize the PredictRequest data.

    Arguments:
        currency: strip + uppercase
        country: strip + uppercase
        merchant_category: strip + lowercase or set to "unknown" if None
        device_type: strip + lowercase or set to "unknown" if None
        transaction_id, user_id: strip
    """
    normalized_transaction = req.transaction.model_copy(
        update={
            "currency": req.transaction.transaction_id.strip(),
            "user_id": req.transaction.user_id.strip(),
            "currency": req.transaction.currency.strip().upper(),
            "country": req.transaction.country.strip().upper(),
            "merchant_category": normalize_optional_string(req.transaction.merchant_category),
            "device_type": normalize_optional_string(req.transaction.device_type),
        }
    )

    return req.model_copy(update={"transaction": normalized_transaction})

def normalize_optional_string(value: str | None) -> str:
    """Normalize optional string fields by stripping whitespace and converting to lowercase.
    If the value is None or empty after stripping, return 'unknown'.
    """
    if value is None or value.strip() == "":
        return "unknown"
    return value.strip().lower()