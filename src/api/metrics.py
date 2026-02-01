from prometheus_client import Counter, Histogram, Gauge

requests_total = Counter(
    'requests_total',
    'Total number of requests received',
    ['endpoint', 'method']
)

responses_total = Counter(
    'responses_total',
    'Total number of responses sent',
    ['endpoint', 'status_code']
)

invalid_requests_total = Counter(
    'invalid_requests_total',
    'Total number of invalid requests received',
    ['reason']
)

inference_failures_total = Counter(
    'inference_failures_total',
    'Total number of inference failures',
)

latency_ms = Histogram(
    'latency_ms',
    'Latency of requests in milliseconds',
    ['endpoint']
)

model_loaded = Gauge(
    'model_loaded',
    'Indicates if the model is loaded (1 for loaded, 0 for not loaded)'
)