"""AEGIS - Analytics, Alerts & Graph API"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import CurrentAuth
from app.db.database import get_db
from app.models.transaction import Account, Transaction
from app.models.audit import Alert, Case
from app.models.enums import RiskLevel, AlertStatus

router = APIRouter()


@router.get("/analytics/overview")
async def get_overview(auth: CurrentAuth, db: AsyncSession = Depends(get_db)):
    q_acc = select(func.count(Account.id))
    q_high = select(func.count(Account.id)).where(Account.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
    q_alert = select(func.count(Alert.id)).where(Alert.status.in_([AlertStatus.NEW, AlertStatus.ACKNOWLEDGED]))
    q_case = select(func.count(Case.id)).where(Case.status == "OPEN")

    if auth.org_id:
        q_acc = q_acc.where(Account.org_id == auth.org_id)
        q_high = q_high.where(Account.org_id == auth.org_id)
        q_alert = q_alert.where(Alert.org_id == auth.org_id)
        q_case = q_case.where(Case.org_id == auth.org_id)

    total_accounts = (await db.execute(q_acc)).scalar_one() or 0
    high_risk_accounts = (await db.execute(q_high)).scalar_one() or 0
    active_alerts = (await db.execute(q_alert)).scalar_one() or 0
    open_cases = (await db.execute(q_case)).scalar_one() or 0

    return {
        "total_accounts": total_accounts,
        "high_risk_accounts": high_risk_accounts,
        "active_alerts": active_alerts,
        "open_cases": open_cases,
    }


@router.get("/alerts")
async def list_alerts(
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    q = select(Alert)
    if auth.org_id:
        q = q.where(Alert.org_id == auth.org_id)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    q = q.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(q)).scalars().all()

    return {
        "items": [
            {
                "id": str(a.id),
                "title": a.title,
                "severity": a.severity,
                "status": a.status,
                "alert_type": a.alert_type,
                "entity_id": a.entity_id,
                "risk_score": a.risk_score,
                "risk_level": a.risk_level,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/graph/subgraph/{account_id}")
async def get_subgraph(account_id: str, auth: CurrentAuth, db: AsyncSession = Depends(get_db)):
    q = select(Transaction).where(
        or_(
            Transaction.sender_account_id == account_id,
            Transaction.receiver_account_id == account_id,
        )
    )
    if auth.org_id:
        q = q.where(Transaction.org_id == auth.org_id)

    txs = (await db.execute(q.limit(100))).scalars().all()
    accounts_set = {account_id}
    edges = []

    for t in txs:
        accounts_set.add(t.sender_account_id)
        accounts_set.add(t.receiver_account_id)
        edges.append({
            "source": t.sender_account_id,
            "target": t.receiver_account_id,
            "amount": float(t.amount),
        })

    acc_q = select(Account).where(Account.account_id.in_(list(accounts_set)))
    if auth.org_id:
        acc_q = acc_q.where(Account.org_id == auth.org_id)

    accs = {a.account_id: a for a in (await db.execute(acc_q)).scalars().all()}

    nodes = [
        {
            "id": aid,
            "risk_level": accs[aid].risk_level if aid in accs else "LOW",
            "risk_score": accs[aid].composite_risk_score if aid in accs else 0.0,
        }
        for aid in accounts_set
    ]

    return {
        "nodes": nodes,
        "edges": edges,
        "center_account_id": account_id,
    }
