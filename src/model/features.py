import pandas as pd
from src.api.schemas import PredictRequest

def build_features(req: PredictRequest) -> pd.DataFrame:
    """Convert PredictRequest to a DataFrame suitable for model input."""

    txn = req.transaction

    features = {
        "amount": txn.amount,
        "currency": txn.currency,
        "country": txn.country,
        "merchant_category": txn.merchant_category,
        "device_type": txn.device_type,
    }

    df = pd.DataFrame([features])

    return df