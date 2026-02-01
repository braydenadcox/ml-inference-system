"""
Unit tests for decision mapping.

These verify that risk scores are correctly mapped to decisions. Outline is as follows:
approve: risk_score < 0.3
review: 0.3 <= risk_score < 0.7
decline: risk_score >= 0.7
"""

from src.model.decision import map_decision

def test_map_decision_approve():
    """Test that risk scores below 0.3 map to 'approve'."""
    assert map_decision(0.0) == "approve"
    assert map_decision(0.1) == "approve"
    assert map_decision(0.29) == "approve"


def test_map_decision_review():
    """Test that risk scores between 0.3 and 0.7 map to 'review'."""
    assert map_decision(0.3) == "review"
    assert map_decision(0.5) == "review"
    assert map_decision(0.69) == "review"


def test_map_decision_decline():
    """Test that risk scores 0.7 and above map to 'decline'."""
    assert map_decision(0.7) == "decline"
    assert map_decision(0.85) == "decline"
    assert map_decision(1.0) == "decline"


def test_map_decision_boundary_values():
    """Test boundary values for decision mapping."""
    assert map_decision(0.2999999) == "approve"
    assert map_decision(0.3) == "review"
    assert map_decision(0.6999999) == "review"
    assert map_decision(0.7) == "decline"