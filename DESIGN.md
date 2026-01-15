# ML Inference Service - System Design Outline and Plan


## Goal
- Build a production-usable real-time ML inference backend that takes in requests, validates/cleans up data, runs a versioned model, gives back predictions, and stays reliable under failure. 


## Use Case
- Domain: Real-time fraud & risk scoring
- What client gives: One transaction event when a payment is attempted, which includes basic metadata such as the transaction amount, country, device type, and the category of merchant.
- What client gets: A decision (approve / review / decline) derived from a risk score between 0 and 1, plus metadata (model version, request ID, etc). 
- Why does this matter: The system has to decide right there whether to approve, challenge, or decline a transaction before it is processed. If the response is slow, the transaction will either time out or continue without protection, which makes the prediction useless.


## API Contract

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


## Validation and Cleaning Rules

Reject with Error 400 if:
- request_id missing or not UUID
- event_time not parseable
- amount <= 0  or amount > MAX_AMOUNT
- currency not parseable (3-letter code)
- country not parseable  (2-letter ISO code)

Accept but normalize if:
- merchant_category missing -> "unknown"
- device_type missing -> "unknown"
- strings have extra whitespace -> lowercase + trim

Service Failure (503) if:
- Model not loaded
- Inference exception or timeout

Decision Logic
- approve: risk_score < 0.30
- review: 0.30 <= risk_score < 0.70
- decline: 0.70 <= risk_score


## Model Versioning and Rollback

Goal
- Make sure all predictions can be traced to a specific model.
- Allow fast recovery if a new model version causes errors or unforseen issues.

Definitions
- model_version: version string for the model artifact (ex: v1, v2)
- active_model_version: version string for the model currently used by /predict

Storage Layout
- models/{model_version}/
  - model.pkl
  - meta.json

meta.json (required)
- model_version (string)
- feature_schema_version (string, ex. fs1)
- created_at(ISO-8601 timestamp)
- notes (string, optional)

Active Model Selection
- configs/active_model.json stores:
  - { "active_model_version": "v1" }
- Service loads the active model at startup (v1).

Runtime Behavior
- /ready:
  - true if the active model is loaded successfully
  - false if model load fails or active model config is invalid
- /predict:
  - returns 503 if model is not loaded
  - includes model_version and feature_schema_version on success

Rollback (V1)
- Manual rollback procedure
  1. Set configs/active_model.json to a previous known-good model_version
  2. Restart service
  3. Verify:
    - Get /model shows the expected model_version
    - New predictions include the rolled-back model_version in responses/logs

Model Introspection
- GET /model returns:
  - active model_version
  - feature_schema_version
  - created_at



## Observability

# Goal
- Make it obviosu when the service is healthy or broken
- Make failures debuggable using request_id, logs, and basic metrics.

Logging (structured)
Log one line per request or error. Include:
- request_id
- transaction_id
- model_version
- decision
- risk_score
- latency_ms
- status_code
- error_type (failures only)

Log levels
- INFO: Successful predictions
- WARN: requests that required normalization (ex. missing optional fields -> "unknown")
- ERROR: inference exceptions, timeouts, model not loaded, etc.

Metrics (minimum)
Expose counters/histograms for
- requests_total (by endpoint)
- latency_ms (histogram for /predict)
- responses_total (by status_code class: 2xx, 4xx, 5xx)
- invalid_requests_total (by reason)
- inference_failures_total
- model_loaded (gauge: 1 if model loaded, else 0)

Health Checks
- GET /health (liveness): returns 200 if the process is running
- GET /ready (readiness): returns 200 only if the active model is loaded and usable.

Debugging Workflow (simple)
- If 5xx increases:
  1. Check /ready (model loaded?)
  2. Check logs filtered by request_id or error_type
  3. If model-related, rollback to previous active_model_version and restart


# Testing Strategy

Unit Tests
- validation: required fields rejected (400) with correct reason
- normalization: mising optional fields become "unknown"
- decision mapping: score thresholds -> approve/review/decline
- model loader: fails cleanly when model/meta missing

Integration Tests
- /health returns 200
- /ready returns 503 when model not loaded and 200 when loaded
- /predict happy path returns 200 and includes request_id + model_version
- /predict invalid input returns 400
- /predict when model missing returns 503


# Runbook (V1)

Start Service
- command to run server (filled in during implementation)

Rollback
1. set configs/active_model.json to previous model_version
2. restart service
3. verify GET /model shows expected version
4. verify new /predict responses include that model_version

If 5xx spikes
- check GET /ready
- check logs by error_type
- rollback if model-related

If 4xx spikes
- check invalid_requests_total by reason
-likely client sending bad payloads