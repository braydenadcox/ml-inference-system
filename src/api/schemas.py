from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Literal
import uuid

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return v
    
    currency: str

    @field_validator("currency")
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")
        return v

    country: str

    @field_validator("country")
    def validate_country(cls, v):
        if len(v) != 2:
            raise ValueError("Country must be a 2-letter ISO code")
        return v
    merchant_category: str | None = "unknown"
    device_type: str | None = "unknown"

class PredictRequest(BaseModel):
    request_id: str

    @field_validator("request_id")
    def validate_request_id(cls, v):
        try:
            uuid.UUID(v)
        except ValueError:
            raise ValueError("request_id must be a valid UUID string")
        return v
    
    event_time: datetime
    transaction: Transaction

class PredictResponse(BaseModel):
    request_id: str
    decision: Literal["approve", "review", "decline"]
    risk_score: float

    @field_validator("risk_score")
    def validate_risk_score(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("Risk score must be between 0.0 and 1.0")
        return v
    
    model_version: str
    processed_at: datetime