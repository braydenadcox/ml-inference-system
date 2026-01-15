ML Inference Service - System Design Outline and Plan


Goal
- Build a production-usable real-time ML inference backend that takes in requests, validates/cleans up data, runs a versioned model, gives back predictions, and stays reliable under failure. 


Use Case
- Domain: Real-time fraud & risk scoring
- What client gives: One transaction event when a payment is attempted, which includes basic metadata such as the transaction amount, country, device type, and the category of merchant.
- What client gets: A risk score between 0 and 1 plus a risk label (low / medium / high), plus metadata (model version, request ID, etc.)
- Why does this matter: The system has to decide right there whether to approve, challenge, or decline a transaction before it is processed. If the response is slow, the transaction will either time out or continue without protection, which makes the prediction useless.


API Contract

Endpoint: POST /predict

Request JSON:
- request_id (string, UUID, required)
- event_time (ISO-8601 timestamp, required)
- transaction:
  - transaction_id (string, required)
  - user_id (string, required)
  - amount (float, required, > 0)
  - currency (string, 3-letter ISO)
  - country (string, 2-letter ISO)
  - merchant_category (string)
  - device_type (string)

Response JSON:
- request_id
- decision (approve | review | decline)
- risk_score (float 0–1)
- model_version
- processed_at (timestamp)

Error Responses:
- 400: invalid input (schema or value error)
- 503: model unavailable or inference failure


Validation and Cleaning Rules

Reject with Error 400 if:
- request_id missing or not UUID
- event_time not parseable
- amount <= 0  or amount > MAX_AMOUNT
- currency not parseable (3-letter code)
- country not parseable  (3-letter code)

Accept but normalize if:
- merchant_category missing -> "unknown"
- device_type missing -> "unknown"
- strings have extra whitespace -> lowercase + trim

503 if:
- Model not loaded
- Inference exception or timeout

Decision Logic
- approve: risk_score < 0.30
- review: 0.30 <= risk_score < 0.70
- decline: 0.70 <= risk_score


