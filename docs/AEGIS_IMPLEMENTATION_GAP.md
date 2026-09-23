# AEGIS Implementation Gap Matrix

## Architecture Baseline
- **Document 1**: AEGIS Patent Information (Multi-Layer Biomimetic Detection, Temporal Anomaly, Behavioral Anomaly, Graph Correlation, Evidence Fusion, Formal Verification, Threat Memory, Explainability, Local Intelligence)
- **Document 2**: VIT FF No. 180 — Project Registration & Progress Review (Transformer sequence model, Isolation Forest, Graph correlation, Rule-based formal verification, Ollama local open-source LLM, Threat-memory retrieval, SHAP-based explainability, evaluation of FPR/FNR and turnaround time)

---

## Gap Analysis Matrix

| Requirement | Source | Existing File | Existing Function | Status | Integration | Tests | Action |
|-------------|--------|---------------|-------------------|--------|-------------|-------|--------|
| **Data Ingestion & Quality Preprocessing** | Patent & FF180 | `data_sources.py` / `generator.py` | upload handler | PARTIAL | Basic column check in upload route | None | Create full `ml/preprocessing/pipeline.py` with schema validation, timestamp normalization, duplicate detection, window generation, and structured quality artifacts |
| **Temporal Detection Engine (Rule/Pattern-Based)** | Patent Cl. 1 | `ml/temporal/engine.py` | `TemporalAnalysisEngine.analyze_account` | PARTIAL | Basic burst & pass-through rules | None | Expand temporal engine with time-gap, velocity, dormant activation, repeated small txs, and sequence windowing |
| **Transformer Sequence Modeling** | FF180 Core | None | None | MISSING | Not integrated | None | Implement PyTorch `TransformerSequenceModel` in `ml/temporal/transformer.py` with embedding, temporal encoding, encoder layers, training, checkpointing, and inference |
| **Unsupervised Behavioral Anomaly (Isolation Forest)** | Patent & FF180 | `ml/behavioral/` (dir only) | None | MISSING | Not integrated | None | Implement `BehavioralAnomalyDetector` in `ml/behavioral/detector.py` using scikit-learn Isolation Forest on multi-dimensional behavioral features |
| **Backend Graph Correlation Engine** | Patent & FF180 | `analytics_graph.py` | `get_subgraph` (DB tx fetch only) | PARTIAL | Only returns 1-hop txs for D3 | None | Implement `GraphCorrelationEngine` in `ml/graph/engine.py` with NetworkX to detect fan-in, fan-out, rapid pass-through, cycles, chains, shared devices/beneficiaries, and multi-hop risk propagation |
| **Multi-Layer Evidence Fusion** | Patent Cl. 4 | `ml/fusion/engine.py` | `EvidenceFusionEngine.fuse` | PARTIAL | Hardcoded 3-weight linear sum | None | Upgrade `ml/fusion/engine.py` to extensible formula $R = f(T, A, G, H, C)$ with confidence derivation and structured evidence emission |
| **Standardized Evidence Object Model** | Patent Cl. 3 | None | None | MISSING | Ad-hoc dicts in engines | None | Create `ml/fusion/evidence.py` defining standardized `EvidenceItem` and `UnifiedRiskProfile` schemas |
| **SHAP-Based Explainability** | FF180 Core | `ml/explainability/` (dir only) | None | MISSING | Not integrated | None | Implement `SHAPExplainer` in `ml/explainability/engine.py` with TreeExplainer on Isolation Forest and feature contribution breakdown |
| **Formal Verification Engine** | Patent & FF180 | `ml/verification/` (dir only) | None | MISSING | Not integrated | None | Implement `FormalVerificationEngine` in `ml/verification/engine.py` checking database ground truth, sender/receiver validity, amount matching, and claim verification |
| **Persistent Threat Memory** | Patent & FF180 | None | None | MISSING | Not integrated | None | Implement `ThreatMemoryStore` in `ml/threat_memory/store.py` with pattern fingerprinting, historical case matching, and vector similarity retrieval |
| **Vector Search / Embeddings** | Patent & FF180 | None | None | MISSING | None | None | Add vector embedding generation for threat memory patterns with cosine similarity and pgvector/local fallback |
| **Local Ollama Investigation Intelligence** | Patent & FF180 | `app/core/config.py` (settings only) | None | MISSING | Config present, no caller | None | Implement `OllamaIntelligenceClient` in `ml/llm/client.py` connecting to local `llama3` with anti-hallucination prompts and claim grounding |
| **LLM Hallucination Defense & Claim Verification** | Patent Cl. 6 | None | None | MISSING | Not integrated | None | Connect Formal Verifier to LLM output to verify all cited transaction IDs and amounts against real records |
| **Investigation Report Generator** | Patent Cl. 7 | None | None | MISSING | Not integrated | None | Implement `InvestigationReportGenerator` in `apps/api/app/services/report_generator.py` producing verified, auditable structured markdown/JSON reports |
| **Case Management & Analyst Feedback** | FF180 & Patent | `apps/api/app/models/audit.py` | `Case` model | PARTIAL | Model exists, no feedback API | None | Add case management endpoints (`/cases/{id}/feedback`, `/cases/{id}/report`, `/cases/{id}/timeline`, `/cases/{id}/what-if`) and feedback storage |
| **What-If Analysis Engine** | Patent Cl. 8 | None | None | MISSING | Not integrated | None | Implement `/api/v1/cases/{id}/what-if` simulating risk changes when specific evidence layers are ablated |
| **Risk Timeline & Evolution** | Patent & FF180 | None | None | MISSING | Not integrated | None | Implement `/api/v1/cases/{id}/timeline` tracking risk progression over time with transaction and alert overlays |
| **Model Registry & System Pipeline Health** | Architecture req | None | None | MISSING | None | None | Implement `ModelRegistry` in `ml/registry.py` and health endpoint `/api/v1/system/pipeline-health` |
| **Case Replay Engine** | Architecture req | None | None | MISSING | None | None | Implement replay endpoint `/api/v1/cases/{id}/replay` demonstrating complete pipeline execution step-by-step |
| **End-to-End Orchestrated Pipeline** | Architecture req | None | None | MISSING | Routes call engines ad-hoc | None | Implement unified `AegisPipelineOrchestrator` in `apps/api/app/services/pipeline_orchestrator.py` chaining Data -> Preprocessing -> T/B/G -> Fusion -> SHAP -> Verification -> Threat Memory -> LLM -> Report |
| **Frontend Investigation Views** | Architecture req | `apps/web/src/app` | Dashboard, Accounts, Tx, Alerts, Graph | PARTIAL | Core pages exist | None | Add Case Detail/Investigation page with Evidence Explorer, SHAP waterfall, Verification checkmarks, Threat Memory matches, and Timeline |
| **Automated Testing Suite** | Architecture req | `tests/` (dir only) | None | MISSING | No test files | None | Build comprehensive pytest suite in `tests/` covering unit, integration, adversarial scenarios, and pipeline verification |
| **Evaluation & Benchmarking Documentation** | FF180 req | None | None | MISSING | None | None | Create `docs/EVALUATION.md` measuring FPR, FNR, Precision, Recall, and latency benchmarks on synthetic datasets |
