"""AEGIS - Investigation Cases & Decision Management API"""
from __future__ import annotations
from datetime import datetime, timezone
import uuid
import pandas as pd
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import CurrentAuth
from app.db.database import get_db
from app.models.audit import Case, Alert
from app.models.transaction import Account, Transaction
from app.services.pipeline_orchestrator import AegisPipelineOrchestrator
from ml.threat_memory.store import ThreatMemoryStore, ThreatPatternRecord

router = APIRouter()
orchestrator = AegisPipelineOrchestrator()
threat_store = ThreatMemoryStore()


class FeedbackPayload(BaseModel):
    decision: str  # "TRUE_POSITIVE", "FALSE_POSITIVE", "NEEDS_REVIEW"
    notes: str = ""
    analyst_name: str = "Senior AML Investigator"


class WhatIfPayload(BaseModel):
    ablations: list[str]  # e.g., ["TEMPORAL", "BEHAVIORAL", "GRAPH", "THREAT_MEMORY"]


@router.get("/cases")
async def list_cases(
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
):
    q = select(Case)
    if auth.org_id:
        q = q.where(Case.org_id == auth.org_id)
    if status:
        q = q.where(Case.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.order_by(Case.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()

    return {
        "items": [
            {
                "id": str(c.id),
                "case_number": c.case_number,
                "title": c.title,
                "description": c.description,
                "status": c.status,
                "priority": c.priority,
                "final_decision": c.final_decision,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/cases/{case_id}")
async def get_case(case_id: str, auth: CurrentAuth, db: AsyncSession = Depends(get_db)):
    # Look up by case ID or case number
    q = select(Case).where((Case.case_number == case_id) | (Case.id == case_id))
    case = (await db.execute(q)).scalar_one_or_none()
    if not case:
        raise HTTPException(404, f"Case {case_id} not found")

    return {
        "id": str(case.id),
        "case_number": case.case_number,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "priority": case.priority,
        "final_decision": case.final_decision,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }


@router.get("/cases/{case_id}/investigate/{account_id}")
async def run_investigation(
    case_id: str,
    account_id: str,
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes the full end-to-end AEGIS pipeline on an account within a case context:
    Data -> Preprocess -> Temporal (Rule+Transformer) -> Behavioral (IForest) ->
    Graph (NetworkX) -> Fusion -> SHAP -> Verification -> Threat Memory -> Ollama -> Report
    """
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

    results = orchestrator.run_account_investigation(account_id, df)
    results["case_id"] = case_id
    return results


@router.post("/cases/{case_id}/feedback")
async def submit_case_feedback(
    case_id: str,
    payload: FeedbackPayload,
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
):
    """
    Records human investigator feedback (TRUE_POSITIVE, FALSE_POSITIVE, NEEDS_REVIEW)
    and updates the persistent Threat Memory store for active learning.
    """
    q = select(Case).where((Case.case_number == case_id) | (Case.id == case_id))
    case = (await db.execute(q)).scalar_one_or_none()
    if not case:
        raise HTTPException(404, f"Case {case_id} not found")

    case.final_decision = payload.decision
    case.status = "RESOLVED" if payload.decision in ["TRUE_POSITIVE", "FALSE_POSITIVE"] else "ESCALATED"
    await db.commit()

    # Record into Threat Memory store
    threat_store.add_threat_pattern(ThreatPatternRecord(
        pattern_id=f"TP_CASE_{case.case_number}",
        pattern_type="INVESTIGATOR_VALIDATED",
        account_id=case.title.split()[-1] if "ACC_" in case.title else "ACC_1025",
        risk_score=90.0 if payload.decision == "TRUE_POSITIVE" else 20.0,
        confirmed_status=payload.decision,
        feature_signature=[20.0, 5000.0, 1000.0, 1.0, 5.0, 10.0, 2.0, 0.3],
        topology_description=f"Analyst validated outcome for {case.case_number}: {payload.notes}",
        analyst_notes=payload.notes,
    ))

    return {
        "case_id": case_id,
        "decision": payload.decision,
        "status": case.status,
        "threat_memory_updated": True,
        "message": "Analyst feedback persisted to Threat Memory successfully.",
    }


@router.post("/cases/{case_id}/what-if")
async def run_what_if_analysis(
    case_id: str,
    account_id: str,
    payload: WhatIfPayload,
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
):
    """
    Simulates: 'What happens to the risk score if specific evidence layers are ablated?'
    """
    txs_res = await db.execute(select(Transaction).limit(1000))
    txs = txs_res.scalars().all()
    df = pd.DataFrame([
        {
            "transaction_id": t.transaction_id,
            "sender_account_id": t.sender_account_id,
            "receiver_account_id": t.receiver_account_id,
            "amount": float(t.amount),
            "currency": t.currency,
            "timestamp": t.timestamp.isoformat() if t.timestamp else "",
        }
        for t in txs
    ])

    base = orchestrator.run_account_investigation(account_id, df)
    base_score = base["risk_profile"]["composite_score"]

    # Compute counterfactual score by zeroing out ablated components
    t_val = 0.0 if "TEMPORAL" in payload.ablations else base["temporal_evidence"]["score"]
    a_val = 0.0 if "BEHAVIORAL" in payload.ablations else base["behavioral_evidence"]["score"]
    g_val = 0.0 if "GRAPH" in payload.ablations else base["graph_evidence"]["score"]

    fused_counterfactual = orchestrator.fusion_engine.fuse(
        account_id=account_id,
        temporal_score=t_val,
        behavioral_score=a_val,
        graph_score=g_val,
    )

    delta = round(fused_counterfactual.composite_score - base_score, 1)

    return {
        "account_id": account_id,
        "baseline_composite_score": base_score,
        "counterfactual_composite_score": fused_counterfactual.composite_score,
        "delta": delta,
        "ablations_applied": payload.ablations,
        "analysis": (
            f"Ablating {', '.join(payload.ablations)} changes composite risk from {base_score} "
            f"to {fused_counterfactual.composite_score} ({delta:+0.1f} pts)."
        ),
    }


@router.get("/cases/{case_id}/timeline")
async def get_risk_timeline(
    case_id: str,
    account_id: str,
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
):
    """
    Chronological progression of risk scores, transactions, and alert events.
    """
    txs_res = await db.execute(
        select(Transaction).where(
            (Transaction.sender_account_id == account_id) | (Transaction.receiver_account_id == account_id)
        ).order_by(Transaction.timestamp.asc()).limit(30)
    )
    txs = txs_res.scalars().all()

    timeline = []
    accumulated_risk = 10.0
    for idx, t in enumerate(txs):
        amt = float(t.amount)
        if amt > 5000.0:
            accumulated_risk = min(95.0, accumulated_risk + 18.0)
        else:
            accumulated_risk = min(95.0, accumulated_risk + 3.0)

        timeline.append({
            "timestamp": t.timestamp.isoformat() if t.timestamp else "",
            "transaction_id": t.transaction_id,
            "amount": amt,
            "is_outgoing": t.sender_account_id == account_id,
            "calculated_risk_at_step": round(accumulated_risk, 1),
            "event": f"Transfer of ${amt} {'to ' + t.receiver_account_id if t.sender_account_id == account_id else 'from ' + t.sender_account_id}",
        })

    return {
        "account_id": account_id,
        "timeline_events": timeline,
        "initial_risk": 10.0,
        "final_risk": round(accumulated_risk, 1),
    }
