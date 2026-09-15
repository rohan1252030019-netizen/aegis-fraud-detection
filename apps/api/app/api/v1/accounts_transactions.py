"""AEGIS - Accounts and Transactions API"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import CurrentAuth
from app.db.database import get_db
from app.models.transaction import Account, Transaction

router = APIRouter()


@router.get("/accounts")
async def list_accounts(
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    risk_level: Optional[str] = None,
    classification: Optional[str] = None,
    search: Optional[str] = None,
):
    q = select(Account)
    if auth.org_id:
        q = q.where(Account.org_id == auth.org_id)
    if risk_level:
        q = q.where(Account.risk_level == risk_level)
    if classification:
        q = q.where(Account.classification == classification)
    if search:
        q = q.where(Account.account_id.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    q = q.order_by(Account.composite_risk_score.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(q)).scalars().all()

    return {
        "items": [
            {
                "id": str(a.id),
                "account_id": a.account_id,
                "classification": a.classification,
                "risk_level": a.risk_level,
                "composite_risk_score": a.composite_risk_score,
                "total_transactions": a.total_transactions,
                "total_sent": float(a.total_sent),
                "total_received": float(a.total_received),
                "is_watchlisted": a.is_watchlisted,
            }
            for a in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/accounts/{account_id}")
async def get_account(account_id: str, auth: CurrentAuth, db: AsyncSession = Depends(get_db)):
    q = select(Account).where(Account.account_id == account_id)
    if auth.org_id:
        q = q.where(Account.org_id == auth.org_id)
    acc = (await db.execute(q)).scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "id": str(acc.id),
        "account_id": acc.account_id,
        "classification": acc.classification,
        "risk_level": acc.risk_level,
        "individual_risk_score": acc.individual_risk_score,
        "network_risk_score": acc.network_risk_score,
        "composite_risk_score": acc.composite_risk_score,
        "total_transactions": acc.total_transactions,
        "total_sent": float(acc.total_sent),
        "total_received": float(acc.total_received),
        "first_seen": acc.first_seen.isoformat() if acc.first_seen else None,
        "last_seen": acc.last_seen.isoformat() if acc.last_seen else None,
        "is_watchlisted": acc.is_watchlisted,
    }


@router.get("/transactions")
async def list_transactions(
    auth: CurrentAuth,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    account_id: Optional[str] = None,
    is_flagged: Optional[bool] = None,
):
    q = select(Transaction)
    if auth.org_id:
        q = q.where(Transaction.org_id == auth.org_id)
    if account_id:
        q = q.where(
            or_(
                Transaction.sender_account_id == account_id,
                Transaction.receiver_account_id == account_id,
            )
        )
    if is_flagged is not None:
        q = q.where(Transaction.is_flagged == is_flagged)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    q = q.order_by(Transaction.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await db.execute(q)).scalars().all()

    return {
        "items": [
            {
                "id": str(t.id),
                "transaction_id": t.transaction_id,
                "sender_account_id": t.sender_account_id,
                "receiver_account_id": t.receiver_account_id,
                "amount": float(t.amount),
                "currency": t.currency,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                "is_flagged": t.is_flagged,
                "risk_score": t.risk_score,
                "risk_level": t.risk_level,
            }
            for t in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
