# AEGIS: Biomimetic Multi-Layer Financial Fraud & Mule Account Detection Platform

> **AEGIS**: *A Biomimetic Multi-Layer Framework for Explainable Mule-Account and Coordinated Financial Fraud Detection Using Temporal Anomaly Detection, Graph Correlation, Evidence-Grounded Explainability and Locally Hosted Intelligence.*

---

## 🌟 Overview

AEGIS is an enterprise-grade financial fraud detection and AML investigation platform engineered to uncover coordinated money-mule networks, multi-hop structuring rings, and rapid pass-through conduits that evade traditional siloed rules. 

Rather than relying on isolated volume thresholds, AEGIS implements a biomimetic multi-layer defense pipeline grounded in mathematical evidence fusion, neural sequence encoding, graph topology analysis, SHAP explainability, and formal database verification.

---

## 🏛️ System Architecture

AEGIS processes financial activity through nine tightly-coupled, verifiable pipeline stages:

```
                      ┌─────────────────────────────────────────┐
                      │        DATA QUALITY PREPROCESSING       │
                      │  Schema validation, duplicate filtering │
                      └────────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
         ▼                                 ▼                                 ▼
┌──────────────────┐             ┌──────────────────┐             ┌──────────────────┐
│ TEMPORAL ENGINE  │             │BEHAVIORAL ENGINE │             │   GRAPH ENGINE   │
│  Velocity Bursts │             │ Isolation Forest │             │ NetworkX Topology│
│ Neural Seq Trans │             │  8-feature vector│             │Fan-In/Out, Cycles│
└────────┬─────────┘             └────────┬─────────┘             └────────┬─────────┘
         │                                 │                                 │
         └─────────────────────────────────┼─────────────────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │         THREAT MEMORY RETRIEVAL         │
                      │ Cosine similarity against known syndicates│
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │          EVIDENCE FUSION ENGINE         │
                      │      R = w_T T + w_A A + w_G G + ...    │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │        SHAP EXPLAINABILITY ENGINE       │
                      │ TreeExplainer waterfall risk drivers    │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       FORMAL VERIFICATION ENGINE        │
                      │ Immutable database assertion checks     │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       LOCAL OLLAMA INTELLIGENCE         │
                      │ Grounded Llama 3 investigation briefing │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    VERIFIED CASE DOSSIER & DASHBOARD    │
                      └─────────────────────────────────────────┘
```

---

## 🔬 Core Components & Capabilities

### 1. Data Quality & Preprocessing ([`ml/preprocessing/pipeline.py`](ml/preprocessing/pipeline.py))
- Automated schema normalization and type casting.
- Strict duplicate transaction filtering on `transaction_id`.
- Missing value profiling, invalid amount isolation (e.g. negative balances), and ISO-8601 normalization.
- Emits standardized `PreprocessingReport` with data quality grade.

### 2. Temporal Analysis & Neural Transformer Sequence Modeling ([`ml/temporal/engine.py`](ml/temporal/engine.py), [`ml/temporal/transformer.py`](ml/temporal/transformer.py))
- **Rule Heuristics**: Detects velocity bursts, rapid pass-through conduit behavior, and structured sub-threshold payments.
- **PyTorch Transformer Sequence Model**: Multi-head attention sequence encoder with sinusoidal temporal/positional encoding measuring non-linear temporal sequence anomalies.

### 3. Behavioral Anomaly Detection ([`ml/behavioral/detector.py`](ml/behavioral/detector.py))
- Unsupervised `IsolationForest` profiling accounts across 8 behavioral dimensions:
  - Transaction velocity per day, unique counterparty dispersion, send/receive ratios, weekend transaction frequency, amount volatility, and max-to-mean amount ratios.

### 4. Graph Correlation & Topology Engine ([`ml/graph/engine.py`](ml/graph/engine.py))
- Directed graph analysis via `NetworkX` extracting:
  - **Fan-In Topology**: Structuring collection hubs converging funds from multiple feeders.
  - **Fan-Out Topology**: Rapid dispersal hubs distributing funds across mule cohorts.
  - **Pass-Through Conduits**: High in-degree and high out-degree bridging nodes.
  - **Circular Laundering Cycles**: Closed transaction loops ($A \rightarrow B \rightarrow C \rightarrow A$).
  - **Shared Device Clusters**: Co-located accounts sharing identical device identifiers.

### 5. Evidence Fusion Engine ([`ml/fusion/engine.py`](ml/fusion/engine.py))
- Extensible mathematical risk formula:
  $$R = w_T \cdot T + w_A \cdot A + w_G \cdot G + w_H \cdot H + w_C \cdot C$$
- Dynamic confidence factor calculation derived from signal agreement, evidence volume, verification status, and historical relevance.

### 6. SHAP-Based Explainability ([`ml/explainability/engine.py`](ml/explainability/engine.py))
- Generates exact feature attributions via `shap.TreeExplainer` on the Isolation Forest model.
- Identifies primary risk drivers with positive/negative directional impact and natural language narratives.

### 7. Rule-Based Formal Verification Engine ([`ml/verification/engine.py`](ml/verification/engine.py))
- Absolute anti-hallucination guardrail verifying every claim, transaction citation, amount, and account provenance directly against the database ledger.
- Flags and rejects any uncorroborated statement or fabricated transaction ID.

### 8. Vectorized Threat Memory ([`ml/threat_memory/store.py`](ml/threat_memory/store.py))
- Persistent storage for verified fraud syndicates, mule patterns, and analyst resolution feedback.
- Sub-millisecond cosine vector similarity matching over behavioral signatures.

### 9. Locally Hosted Intelligence ([`ml/llm/client.py`](ml/llm/client.py))
- Local Ollama (`llama3`) narrative synthesizer operating completely on-premise without external data leakage.
- Strict prompt constraints enforcing evidence citations with immediate deterministic fallback.

---

## 📊 Empirical Evaluation & Benchmarks

Full benchmark metrics are documented in [`docs/EVALUATION.md`](docs/EVALUATION.md).

| Metric | Traditional Siloed Baseline | AEGIS Multi-Layer Framework | Performance Impact |
| :--- | :--- | :--- | :--- |
| **Detection Recall** | `52.00%` | **`76.00%`** | **+24.00% higher fraud catch rate** |
| **False Negative Rate** | `48.00%` | **`24.00%`** | **-50.00% reduction in missed mules** |
| **Average Full Latency** | `0.91 ms` | **`65.38 ms` (p50)** | **Real-time sub-100ms investigation** |
| **Anti-Hallucination Rate** | N/A | **`100.0%`** | **Zero ungrounded claims permitted** |

---

## 🚀 Running the Platform

### Option 1: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) [Ollama](https://ollama.ai) with `llama3` for local narrative generation

#### 1. Backend API:
```bash
cd apps/api
# Set PYTHONPATH to include project root
set PYTHONPATH=.;../../
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Pipeline Health: [http://localhost:8000/api/v1/system/pipeline-health](http://localhost:8000/api/v1/system/pipeline-health)

#### 2. Frontend Web Console:
```bash
cd apps/web
npm install
npm run dev
```
- Web Application: [http://localhost:3000](http://localhost:3000)
- Case Investigation Console: [http://localhost:3000/cases](http://localhost:3000/cases)

### Option 2: Docker Compose

```bash
docker compose up --build
```

---

## 🧪 Testing & Verification

Run the comprehensive test suite verifying all 9 core subsystems:

```bash
python -m pytest tests/test_aegis_pipeline.py -v
```

Run the benchmark evaluation harness:

```bash
python scripts/evaluate_pipeline.py
```

---

## 📑 Documentation

- [Implementation Gap Matrix](docs/AEGIS_IMPLEMENTATION_GAP.md)
- [Empirical Evaluation & Benchmarking Report](docs/EVALUATION.md)
- [Final Architectural Implementation Report](docs/AEGIS_FINAL_IMPLEMENTATION_REPORT.md)
