# AEGIS: Financial Fraud & Mule Account Detection Platform

AEGIS is a biomimetic multi-layer framework for explainable mule-account and coordinated financial fraud detection using temporal anomaly detection, graph correlation, evidence-grounded explainability, and locally hosted intelligence.

## Architecture

- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL + pgvector, Redis, Celery
- **Frontend**: Next.js 14, Tailwind CSS, TypeScript, Axios
- **ML Layer**: Temporal Analysis, Isolation Forest Behavioral Anomaly Detection, Evidence Fusion Engine

## Running the Platform

### Option 1: Docker (Recommended)

```bash
docker compose up --build
```

- Web Dashboard: [http://localhost:3000](http://localhost:3000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option 2: Local Development

1. **Backend**:
```bash
cd apps/api
pip install -r requirements.txt # or poetry install
uvicorn app.main:app --reload --port 8000
```

2. **Frontend**:
```bash
cd apps/web
npm install
npm run dev
```
