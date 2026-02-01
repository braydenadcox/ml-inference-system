# ML Inference Service

Production-style real-time ML inference backend for fraud and risk scoring.

This service accepts a single transaction event, validates and normalizes input,
runs a versioned ML model, and returns a risk-based decision
(approve / review / decline) with strong failure isolation and observability.

## Features
- Strict request validation with consistent HTTP 400 semantics
- Versioned model loading with fast rollback
- Real-time inference with 503 isolation on model failure
- Structured logging and basic metrics
- Health and readiness endpoints for production use

## Architecture (High Level)
Request → Validation → Normalization → Feature Building → Model Inference →
Decision Mapping → Response

For full system design, tradeoffs, and failure handling, see:
**[DESIGN.md](DESIGN.md)**

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate  # or Windows equivalent
pip install -r requirements.txt
uvicorn src.api.main:app --reload
