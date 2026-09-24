# AEGIS: Financial Fraud & Money Mule Detection System
## Comprehensive System Documentation & User Interface Guide

> **Live Deployment URL**: [https://aegis-edi.vercel.app](https://aegis-edi.vercel.app)  
> **Project**: AEGIS (Biomimetic Multi-Layer Anti-Money Laundering & Mule Account Detection Framework)  
> **Target Audience**: Evaluators, Faculty, AML Compliance Officers, and Technical Investigators.

---

## 1. Project Overview & Core Philosophy

### What is AEGIS?
**AEGIS** is a biomimetic financial intelligence platform engineered to detect coordinated money laundering, smurfing rings, and automated money mule networks. Unlike traditional banking systems that rely solely on static SQL rules or single machine-learning black boxes, AEGIS replicates the multi-tiered defense of a biological immune system:
1. **Innate Defense**: Instantaneous temporal velocity and regulatory threshold checks.
2. **Adaptive Defense**: Sequence Transformer models, unsupervised Isolation Forest anomaly detection, and NetworkX topological graph correlation.
3. **Formal Immune Memory**: Historical threat memory vector search, mathematical Z3 formal theorem verification, and on-premise local LLM intelligence briefings.

---

## 2. Screen-by-Screen Breakdown & Visual Elements

---

### SCREEN 1: Overview Dashboard (`/dashboard`)
*The central command console giving investigators an immediate bird's-eye view of financial health, threat velocity, and active risk.*

#### A. Top Header
* **Title**: `Security & Fraud Overview`
* **Subtitle**: Real-time multi-layer detection overview, account behavioral health, and anomaly velocity.
* **Sync Engine Button**: Clicking this triggers an instantaneous re-synchronization with the detection pipeline to pull the latest telemetry.
* **View Alerts Button**: Direct shortcut link taking the investigator straight to the prioritized alerts inbox.

#### B. Primary Stat Cards (Top KPI Row)
1. **Monitored Accounts (e.g., 1,959)**
   * *What it means*: The total pool of accounts currently ingested and actively tracked in the monitoring network.
   * *Badge*: `Active Pool` (indicates continuous telemetry tracking).
   * *Trend*: `+3.8% vs. last 30 days` (shows steady growth in monitored account population).
2. **Mule Candidates (e.g., 14)**
   * *What it means*: Accounts flagged with composite risk $\ge 70/100$, demonstrating coordinated layering, rapid fund disbursement, or pass-through behavior.
   * *Color*: High-visibility Rose/Red badge indicating critical priority for compliance review.
3. **Active Alerts (e.g., 23)**
   * *What it means*: Distinct anomalies currently open across Temporal, Behavioral, and Graph layers.
   * *Badge*: `Requires Review` (signifies events requiring investigation).
4. **Pending Dossiers (e.g., 8)**
   * *What it means*: Formal investigation cases created and assigned to compliance officers awaiting final disposition (SAR filing vs. false positive).

#### C. Visual Charts & Analytics Widgets
1. **Transaction Velocity & Anomaly Trends (Area Chart)**:
   * *X-Axis*: 24-hour time intervals (`00:00`, `04:00`, `08:00`, `12:00`, `16:00`, `20:00`, `23:59`).
   * *Cyan Area*: Total transaction volume flowing through the platform.
   * *Rose Area*: Volume of transactions specifically flagged as suspicious or structurable.
   * *Purpose*: Quickly detect coordinated timing bursts (e.g., automated midnight cash-out batches).
2. **Risk Distribution by Tier (Bar Chart)**:
   * *Green Bar (Low Risk)*: Benign everyday accounts ($\sim 95\%+$ of the population).
   * *Yellow Bar (Moderate)*: Accounts exhibiting minor variance from baseline.
   * *Orange Bar (Elevated)*: Accounts nearing velocity limits or with newly linked unverified devices.
   * *Red Bar (Critical/High)*: Active mule candidates with confirmed multi-layer evidence.
3. **Biomimetic Defense System Status Card**:
   * Visual indicators showing operational health of:
     * *Innate Immunity*: Operational (Rules & Velocity bounds).
     * *Adaptive Immunity*: Operational (Transformers & Isolation Forest).
     * *Network Topology*: Operational (Graph cycle and fan-in correlation).
     * *Formal Grounding*: Active (Immutable Z3 invariant proofs).

#### D. Recent High-Priority Alerts Feed
* Displays the 5 latest critical alerts with direct links, entity identifiers (`ACC00048599`), timestamps, and severity tags (`CRITICAL`, `HIGH`).

---

### SCREEN 2: Data Ingestion & Schema Validation (`/data-import`)
*The portal where raw banking transaction files (.CSV or .JSON) are ingested, rigorously validated, and processed through the detection pipeline.*

#### A. Upload Dropzone & Strict File Guard
* **Accepted Formats**: `.csv` (comma-separated values) or `.json` (structured record array).
* **Strict Size Limit**: Maximum batch size is hard-capped at **250 MB**. Files exceeding this limit are immediately rejected with an explicit byte-count error.
* **Instant Client-Side Schema Inspector**: The moment a file is dragged or selected, AEGIS inspects its header to verify the **6 Essential Canonical Fields**:
  1. `transaction_id`: Unique identifier per transaction event.
  2. `sender_account_id`: Source account number.
  3. `receiver_account_id`: Destination account number.
  4. `amount`: Financial amount (decimal/float).
  5. `currency`: Standard 3-letter currency code (`INR`, `USD`, `EUR`).
  6. `timestamp`: ISO-8601 standardized datetime.
* **Status Badges in Dropzone**:
  * *Green Check*: `Ready for Ingestion (AEGIS_CANONICAL)`.
  * *Red Ban*: `REJECTED — SCHEMA VALIDATION FAILED` (lists missing columns).
  * *Red Ban*: `REJECTED — FILE TOO LARGE (Max: 250 MB)`.

#### B. Pipeline Execution & Verification Cards
* **Run AEGIS Detection Pipeline Button**: Executes the ingestion worker. Shows a dynamic animated progress bar from 0% to 100%.
* **Dataset Validation Card**:
  * *Records Processed*: Total lines parsed (e.g., 663,373).
  * *Valid Records*: Records passing schema and type boundaries.
  * *Rejected Records*: Defective records (null IDs, negative amounts, malformed dates).
  * *Data Quality Score*: Calibrated percentage score with badge (`100% EXCELLENT`).
  * *View Validation Details Button*: Expands row-level error audit logs.
* **Pipeline Result Summary Card**:
  * Displays 6 key telemetry counters upon execution:
    * `Transactions Processed`
    * `Accounts Analyzed`
    * `Anomalies Detected`
    * `Suspicious Networks Identified`
    * `Verified Alerts Generated`
    * `Compliance Cases Created`

---

### SCREEN 3: Active AML Alerts Inbox (`/alerts`)
*The central review queue for compliance officers to inspect, prioritize, and filter anomalous events.*

#### A. Filters & Search Controls
* **Severity Tabs**: Filter alerts instantly by `ALL`, `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
* **Search Input**: Live keyword filtering by Account ID, Alert Title, or Entity.
* **Refresh Button**: Re-fetches the latest alerts.

#### B. Alert Table Columns
* **Alert ID**: Unique tracking code (e.g., `ALT-2026-0914-1`) with a one-click clipboard copy button.
* **Severity / Risk Badge**: Color-coded pill (`CRITICAL` in deep rose, `HIGH` in amber, etc.).
* **Alert Title & Summary**: Plain-English explanation (e.g., *"AEGIS Multi-Layer Alert: Rapid Disbursement Mule Ring"*).
* **Alert Type**: Canonical classification (e.g., `MULTI_LAYER_MULE_RISK`, `STRUCTURING_SMURFING`, `CYCLE_TOPOLOGY`, `IP_DEVICE_CLUSTER`).
* **Entity ID**: The target account or device identifier under scrutiny.
* **Risk Score**: Normalized numeric threat level (0.0 to 100.0).
* **Status**: Workflow state (`NEW`, `INVESTIGATING`, `ESCALATED`, `RESOLVED`).
* **Created At**: Timestamp of alert generation.

#### C. Detail Modal
* Clicking any alert row opens a flyout showing complete telemetry, triggered patterns, and a direct button to open the full investigation dossier.

---

### SCREEN 4: Monitored Accounts Directory (`/accounts`)
*Directory of all customer and corporate accounts monitored by AEGIS.*

#### A. Controls & Table
* **Risk Level Filter**: View accounts filtered by risk grade (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `ALL`).
* **Search Input**: Instant lookup by Account Number.
* **Columns**:
  * *Account ID*: Account identifier (e.g., `ACC00048599`).
  * *Risk Level & Score*: Formally calibrated score out of 100.
  * *Status*: Account state (`FLAGGED`, `UNDER_REVIEW`, `FROZEN`, `ACTIVE`).
  * *Total Transactions*: Cumulative transaction count.
  * *Total Sent / Received*: Complete ledger volume formatted in standard currency.
  * *Actions*: Direct links to visualize in the Graph Engine or trigger an investigation.

---

### SCREEN 5: Transaction Ledger (`/transactions`)
*Real-time audit log of all financial movements across the network.*

#### A. Filters & Table
* **Account Filter**: View only transactions involving a specific account.
* **Flagged Only Checkbox**: Toggle to instantly filter for only transactions that breached safety rules.
* **Columns**:
  * *Transaction ID*: Unique alphanumeric reference.
  * *Sender & Receiver Accounts*: Origin and destination endpoints.
  * *Amount & Currency*: Cleanly formatted financial value.
  * *Timestamp*: Exact transaction execution time.
  * *Status Indicator*: Green check for normal flow, Rose warning for flagged transactions.

---

### SCREEN 6: Case Management & 12-Stage Investigation Engine (`/cases`)
*The crown jewel of AEGIS — an end-to-end autonomous investigation workbench with formal verification proofs and local AI compliance briefings.*

#### A. Left Column: Active Cases Roster
* Displays open investigation cases (e.g., `CASE-20260914-8599`).
* Shows assigned investigator, priority (`CRITICAL`, `HIGH`), and current status (`OPEN`, `INVESTIGATING`, `RESOLVED`).

#### B. Primary Action: "Run Full AEGIS Investigation"
* Clicking this button executes the entire **12-Stage Detection & Grounding Pipeline**:
  1. *Data Ingestion*
  2. *Preprocessing & Data Quality Validation*
  3. *Temporal Velocity & Structuring Rules*
  4. *Transformer Sequence Inference* (PyTorch self-attention)
  5. *Behavioral Outlier Detection* (Isolation Forest)
  6. *Graph Correlation & Cycle Analysis* (NetworkX)
  7. *Multi-Layer Evidence Fusion* (Calibrated Bayesian fusion)
  8. *SHAP Feature Attribution* (TreeExplainer)
  9. *Formal Logic Verification* (Z3 invariant theorem proving)
  10. *Threat Memory Retrieval* (Vector cosine similarity)
  11. *Local Investigation Intelligence* (On-premise Ollama / Llama 3)
  12. *Final Compliance Dossier Compilation*

#### C. Live Pipeline Stepper
* Features a live monotonic timer measuring execution in seconds (`Elapsed: 1.8s`).
* Real-time animated status spinners showing each stage transition from `Pending` $\rightarrow$ `Running` $\rightarrow$ `Completed`.

#### D. Completed Compliance Dossier Components
1. **Target Account & Composite Score Card**:
   * Shows account number, risk level pill (`CRITICAL`), classification, and composite risk score out of 100 (`92.4 / 100`).
2. **Pipeline Execution Trace**:
   * Displays all 12 stages with exact duration in milliseconds (e.g., `Temporal: 110ms`, `Transformer: 220ms`, `SHAP: 240ms`).
3. **Formal Verification (Z3 Grounding) Card**:
   * *Status*: `VERIFIED_SOUND` (5/5 Passed).
   * Proves mathematically that fraud theorems hold true with zero counterexamples:
     * *RapidDisbursementTheorem*: Inflow rapidly extracted within 300 seconds.
     * *StructuringThresholdBarrier*: Transfers clustered under statutory limit.
     * *CircularTopologyGrounding*: Fund loop conservation verified within 2% margin.
     * *DormancyVelocitySpike*: Dormant >90 days prior to sudden volume explosion.
     * *MultiHopFanOutConservation*: Dispersal entropy verified.
4. **SHAP Explainability Card**:
   * Model: `XGBoost + SHAP TreeExplainer`.
   * Displays the exact mathematical risk drivers (e.g., `+0.38 fan_in_velocity_60m`, `+0.29 structuring_proximity_ratio`).
5. **Threat Memory Corroboration**:
   * Vector cosine matching against historical fraud syndicates (e.g., *93% similarity with August 2025 Cryptocurrency Funnel Ring*).
6. **Local LLM Investigation Brief**:
   * Plain-English executive compliance summary generated locally by Llama 3 without sending customer data to external cloud APIs.
7. **Compliance Resolution Action Bar**:
   * Compliance officers can click **"Confirm Mule (True Positive)"** to file a SAR, or **"Mark False Positive"**, which immediately updates the Threat Memory database for active learning.

---

### SCREEN 7: Interactive Financial Network Graph (`/graph`)
*Visual graph intelligence platform mapping fund transfers, laundering rings, and syndicate topologies.*

#### A. Controls & Search
* **Search Bar**: Center the visualization on any target account ID.
* **Zoom & Pan Controls**: Zoom In (`+`), Zoom Out (`-`), and Reset View (`⟲`).
* **Node Inspector Panel**: Displays centrality, total volume, risk score, and structural role upon clicking any node.

#### B. Node Roles & Visual Markers
* **Mule Aggregator (Red/Rose)**: High betweenness centrality, receives funds from many sources and aggregates them.
* **Smurfing Source (Amber/Orange)**: Disperses micro-transfers below statutory limits.
* **Offramp Gateway (Red Border)**: Cryptocurrency merchant or high-risk OTC broker cash-out point.
* **Directed Arrows**: Indicate real fund movement with thickness proportional to transfer amount.

---

## 3. Quick Reference: User Workflows

### How to Upload and Validate a New Dataset
1. Navigate to **Data Ingestion** (`/data-import`) from the sidebar.
2. Drag and drop your `.csv` file into the upload zone.
3. Observe the schema inspector:
   - If canonical fields are present, it marks the file `Ready for Ingestion`.
   - If columns are missing, it highlights the exact missing fields.
4. Click **Run AEGIS Detection Pipeline**.
5. Once complete, view the **Dataset Validation** score and verified telemetry summary.

### How to Run an Investigation on a Suspicious Account
1. Navigate to **Cases** (`/cases`).
2. Select a case from the roster (e.g., `CASE-20260914-8599`).
3. Click **Run Full AEGIS Investigation**.
4. Watch the 12 pipeline stages execute in real-time.
5. Review the resulting **Formal Verification Proofs**, **SHAP Drivers**, and **Ollama Intelligence Narrative**.
6. Click **Confirm Mule (True Positive)** to log the regulatory disposition.

---

## 4. Technical Architecture & Technology Stack

| Layer | Technologies Used | Purpose |
|---|---|---|
| **Frontend UI** | Next.js 14 (App Router), TailwindCSS, TypeScript, Lucide Icons, Recharts, D3.js | Interactive compliance dashboards, real-time monitors, and dynamic force-directed graphs. |
| **Backend API** | FastAPI (Python 3.13), Pydantic v2, SQLAlchemy 2.0 (Async), SQLite / PostgreSQL | High-concurrency REST endpoints, async job runners, and streaming upload parsers. |
| **Detection ML** | PyTorch (Sequence Transformer), Scikit-Learn (Isolation Forest), NetworkX | Temporal sequence attention, unsupervised behavioral profiling, and graph topology analysis. |
| **Trust & Verification**| SHAP (TreeExplainer), Formal First-Order Logic (Z3 Invariants) | Feature attribution and mathematical proofs preventing AI hallucinations. |
| **Memory & AI** | Cosine Vector Matching, Ollama (Llama 3 8B Local Daemon) | Historical pattern retrieval and local on-premise narrative generation. |
| **Live Hosting** | Vercel Serverless Edge (`https://aegis-edi.vercel.app`) | Global low-latency edge deployment with offline simulated fallback capability. |

---
*AEGIS Documentation — Prepared for EDI Project Evaluation, Dept. of CSE (AI & ML), VIT Pune.*
