"""
AEGIS - Background Investigation Job Manager
Provides asynchronous execution, cancellation, and real-time stage progress polling.
Strictly implements the 12 required AEGIS pipeline stages.
"""
from __future__ import annotations
import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
import pandas as pd
from app.services.pipeline_orchestrator import pipeline_orchestrator


STAGE_DEFINITIONS = [
    {"stage": "DATA_INGESTION", "label": "Data Ingestion", "desc": "Ingesting case and account transactions"},
    {"stage": "PREPROCESSING", "label": "Preprocessing", "desc": "Transaction validation and normalization"},
    {"stage": "TEMPORAL_ANALYSIS", "label": "Temporal Analysis", "desc": "Velocity and burst flow analysis"},
    {"stage": "TRANSFORMER_INFERENCE", "label": "Transformer Analysis", "desc": "Neural sequence model inference"},
    {"stage": "BEHAVIORAL_ANALYSIS", "label": "Behavioral Analysis", "desc": "Isolation Forest anomaly profiling"},
    {"stage": "GRAPH_CORRELATION", "label": "Graph Correlation", "desc": "Network topology and cycle detection"},
    {"stage": "EVIDENCE_FUSION", "label": "Evidence Fusion", "desc": "Multi-layer risk synthesis"},
    {"stage": "SHAP_EXPLANATION", "label": "SHAP Explainability", "desc": "Feature contribution attribution"},
    {"stage": "FORMAL_VERIFICATION", "label": "Formal Verification", "desc": "Evidence-grounded invariant checks"},
    {"stage": "THREAT_MEMORY", "label": "Threat Memory", "desc": "Historical pattern similarity matching"},
    {"stage": "OLLAMA_INVESTIGATION", "label": "Investigation Intelligence", "desc": "Local intelligence brief generation"},
    {"stage": "FINAL_DOSSIER", "label": "Final Dossier", "desc": "Packaging auditable compliance dossier"},
]


class InvestigationJob:
    def __init__(self, case_id: str, account_id: str):
        self.job_id = str(uuid.uuid4())
        self.case_id = case_id
        self.account_id = account_id
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
        self.current_stage = "DATA_INGESTION"
        self.current_stage_label = "Initializing investigation pipeline..."
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None
        self.elapsed_ms: float = 0.0
        self.start_monotonic = time.monotonic()
        self.stages: List[Dict[str, Any]] = [
            {
                "stage": s["stage"],
                "label": s["label"],
                "status": "PENDING",
                "started_at": None,
                "completed_at": None,
                "duration_ms": None,
                "input_count": None,
                "output_count": None,
                "error": None,
            }
            for s in STAGE_DEFINITIONS
        ]
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.failed_stage: Optional[str] = None
        self.is_cancelled: bool = False
        self._task: Optional[asyncio.Task] = None

    def _start_stage(self, stage_name: str, label: str):
        self.current_stage = stage_name
        self.current_stage_label = label
        now_iso = datetime.now(timezone.utc).isoformat()
        for s in self.stages:
            if s["stage"] == stage_name:
                s["status"] = "RUNNING"
                s["started_at"] = now_iso
                break

    def _complete_stage(
        self,
        stage_name: str,
        duration_ms: float,
        input_count: Optional[int] = None,
        output_count: Optional[int] = None,
    ):
        now_iso = datetime.now(timezone.utc).isoformat()
        for s in self.stages:
            if s["stage"] == stage_name:
                s["status"] = "COMPLETED"
                s["completed_at"] = now_iso
                s["duration_ms"] = duration_ms
                if input_count is not None:
                    s["input_count"] = input_count
                if output_count is not None:
                    s["output_count"] = output_count
                break

    def _fail_stage(self, stage_name: str, error_msg: str):
        self.failed_stage = stage_name
        now_iso = datetime.now(timezone.utc).isoformat()
        for s in self.stages:
            if s["stage"] == stage_name:
                s["status"] = "FAILED"
                s["completed_at"] = now_iso
                s["error"] = error_msg
                break

    def to_dict(self) -> Dict[str, Any]:
        now_mono = time.monotonic()
        elapsed = round((now_mono - self.start_monotonic) * 1000, 1) if self.status in ["RUNNING", "PENDING"] else self.elapsed_ms
        return {
            "job_id": self.job_id,
            "case_id": self.case_id,
            "account_id": self.account_id,
            "status": self.status,
            "current_stage": self.current_stage,
            "current_stage_label": self.current_stage_label,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "elapsed_ms": elapsed,
            "stages": self.stages,
            "error": self.error,
            "failed_stage": self.failed_stage,
            "result": self.result,
        }

    async def execute(self):
        self.status = "RUNNING"
        self.start_monotonic = time.monotonic()

        try:
            # Stage 1: DATA_INGESTION
            if self.is_cancelled:
                self.status = "CANCELLED"
                return

            self._start_stage("DATA_INGESTION", "Ingesting transaction data from database...")
            t0 = time.monotonic()
            
            from app.db.database import AsyncSessionLocal
            from app.models.transaction import Transaction
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                txs_res = await db.execute(select(Transaction).limit(2000))
                txs = txs_res.scalars().all()
                df = pd.DataFrame([
                    {
                        "transaction_id": t.transaction_id,
                        "sender_account_id": t.sender_account_id,
                        "receiver_account_id": t.receiver_account_id,
                        "amount": float(t.amount),
                        "currency": t.currency,
                        "transaction_type": t.transaction_type,
                        "timestamp": t.timestamp.isoformat() if t.timestamp else "",
                    }
                    for t in txs
                ])

            dur_ingest = round((time.monotonic() - t0) * 1000, 2)
            self._complete_stage("DATA_INGESTION", dur_ingest, input_count=len(df), output_count=len(df))

            if self.is_cancelled:
                self.status = "CANCELLED"
                return

            # Live progress callback forwarded from pipeline_orchestrator
            def stage_callback(stage_name: str, status: str, meta: Dict[str, Any]):
                if status == "RUNNING":
                    self._start_stage(stage_name, meta.get("label", f"Running {stage_name}..."))
                elif status == "COMPLETED":
                    self._complete_stage(
                        stage_name,
                        meta.get("duration_ms", 0.0),
                        input_count=meta.get("input_count"),
                        output_count=meta.get("output_count"),
                    )
                elif status == "FAILED":
                    self._fail_stage(stage_name, meta.get("error", "Stage execution failed"))

            # Execute ML & Detection Pipeline
            result = await asyncio.to_thread(
                pipeline_orchestrator.run_account_investigation,
                self.account_id,
                df,
                progress_callback=stage_callback,
                cancellation_check=lambda: self.is_cancelled,
            )

            if self.is_cancelled:
                self.status = "CANCELLED"
                return

            # Stage 12: FINAL_DOSSIER packaging
            self._start_stage("FINAL_DOSSIER", "Packaging final compliance audit dossier...")
            t0 = time.monotonic()
            result["case_id"] = self.case_id
            result["job_id"] = self.job_id

            # Incorporate DATA_INGESTION into pipeline_trace
            ingest_meta = {
                "stage": "DATA_INGESTION",
                "status": "COMPLETED",
                "duration_ms": dur_ingest,
                "input_count": len(df),
                "output_count": len(df),
                "error": None,
            }
            # Reorder trace to include all 12 stages in standard order
            final_trace = [ingest_meta] + result.get("pipeline_trace", [])
            dur_dossier = round((time.monotonic() - t0) * 1000, 2)
            dossier_meta = {
                "stage": "FINAL_DOSSIER",
                "status": "COMPLETED",
                "duration_ms": dur_dossier,
                "input_count": 1,
                "output_count": 1,
                "error": None,
            }
            final_trace.append(dossier_meta)
            self._complete_stage("FINAL_DOSSIER", dur_dossier, input_count=1, output_count=1)

            result["pipeline_trace"] = final_trace
            dur_total = round((time.monotonic() - self.start_monotonic) * 1000, 2)
            result["total_execution_ms"] = dur_total

            self.status = "COMPLETED"
            self.completed_at = datetime.now(timezone.utc).isoformat()
            self.elapsed_ms = dur_total
            self.result = result

        except asyncio.CancelledError:
            self.status = "CANCELLED"
            self.error = "Investigation was cancelled by investigator."
            self.completed_at = datetime.now(timezone.utc).isoformat()
            self.elapsed_ms = round((time.monotonic() - self.start_monotonic) * 1000, 1)
        except Exception as e:
            self.status = "FAILED"
            self.error = str(e)
            if not self.failed_stage:
                self.failed_stage = self.current_stage
            self._fail_stage(self.failed_stage, str(e))
            self.completed_at = datetime.now(timezone.utc).isoformat()
            self.elapsed_ms = round((time.monotonic() - self.start_monotonic) * 1000, 1)


class InvestigationJobManager:
    def __init__(self):
        self._jobs: Dict[str, InvestigationJob] = {}

    def create_and_start_job(
        self,
        case_id: str,
        account_id: str,
    ) -> InvestigationJob:
        job = InvestigationJob(case_id, account_id)
        self._jobs[job.job_id] = job
        # Launch non-blocking background task
        task = asyncio.create_task(job.execute())
        job._task = task
        return job

    def get_job(self, job_id: str) -> Optional[InvestigationJob]:
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job:
            return False
        job.is_cancelled = True
        if job._task and not job._task.done():
            job._task.cancel()
        job.status = "CANCELLED"
        job.error = "Investigation cancelled by user."
        return True


investigation_manager = InvestigationJobManager()
