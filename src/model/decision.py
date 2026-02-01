from typing import Literal

def map_decision(risk_score: float) -> Literal["approve", "review", "decline"]:
    """Map a risk score to a decision category.

    Args:
        risk_score (float): The risk score between 0.0 and 1.0.

    Returns:
        Literal["approve", "review", "decline"]: The decision category.
    """
    if not (0.0 <= risk_score <= 1.0):
        raise ValueError(f"Risk score must be between 0.0 and 1.0, got {risk_score}")

    if risk_score < 0.3:
        return "approve"
    elif risk_score < 0.7:
        return "review"
    else:
        return "decline"