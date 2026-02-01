# ML Inference Service

A production-style machine learning inference API built with **FastAPI** and **Docker**.

This service validates incoming requests, constructs features, runs a versioned ML model, and returns a real-time risk decision.  
The focus is on **inference infrastructure**, not model training.

---

## Why This Project Exists

Most ML demos stop at model training.  
This project focuses on what *actually matters in production*:

- strict input validation
- deterministic inference behavior
- model versioning
- health and readiness checks
- fast, reproducible deployment

---

## Tech Stack

- **FastAPI** – API framework  
- **Pydantic** – request validation  
- **scikit-learn** – model inference  
- **Docker** – containerization  
- **Docker Compose** – one-command local run  

---

## Project Layout

```text
ml-inference-system/
├── src/
│   ├── api/              # API routes, logging, schemas
│   └── model/            # Feature building & model loading
├── models/
│   └── v1/               # Versioned model artifacts
├── configs/              # Active model configuration
├── scripts/
│   └── test_predict.ps1  # End-to-end smoke test
├── Dockerfile
├── docker-compose.yml
├── requirements.inference.txt
├── requirements.dev.txt
└── README.md
```

## Quick Start on Docker

### Requirements
- Docker
- Docker Compose

### Start the Service
```powershell
docker compose up -d --build
```

The API will be accessible at
```text
http://localhost:8000
```

Verify the services and endpoints with
```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
```

Inference Testing With Mock Request
```powershell
.\scripts\test_predict.ps1
```

How to Stop Service
```powershell
docker compose down
```






