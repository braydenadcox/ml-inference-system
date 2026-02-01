$uuid = [guid]::NewGuid().ToString()

$body = @"
{
  "request_id": "$uuid",
  "event_time": "$(Get-Date -Format o)",
  "transaction": {
    "transaction_id": "txn_001",
    "user_id": "user_123",
    "amount": 100.0,
    "currency": "USD",
    "country": "US",
    "merchant_category": "ELECTRONICS",
    "device_type": "unknown"
  }
}
"@

# Write exact bytes (no extra newline) then have curl read from file
$path = Join-Path $PSScriptRoot "req.json"
$body | Out-File -Encoding utf8 -NoNewline $path

curl.exe -X POST "http://localhost:8000/predict" `
  -H "Content-Type: application/json" `
  --data-binary "@$path"
