"""AEGIS - Auth API router"""
from __future__ import annotations
import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from app.core.dependencies import CurrentAuth
from app.db.database import get_db
from app.models.user import User, Organization
from app.models.enums import UserRole

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    slug = re.sub(r"[^a-z0-9]+", "-", body.organization_name.lower()).strip("-")
    if not slug:
        slug = f"org-{uuid.uuid4().hex[:6]}"

    org = Organization(name=body.organization_name, slug=slug, is_active=True)
    db.add(org)
    await db.flush()

    user = User(
        org_id=org.id,
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.commit()

    return {"message": "Account created successfully", "user_id": str(user.id)}


@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled")

    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token_data = {"sub": str(user.id), "email": user.email, "org_id": str(user.org_id) if user.org_id else None, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        },
        "org_id": str(user.org_id) if user.org_id else None,
    }


@router.post("/refresh")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type for refresh")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token subject")

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or disabled")

    token_data = {"sub": str(user.id), "email": user.email, "org_id": str(user.org_id) if user.org_id else None, "role": user.role}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_current_user(auth: CurrentAuth):
    return {
        "id": str(auth.user.id),
        "email": auth.user.email,
        "full_name": auth.user.full_name,
        "role": auth.role,
        "org_id": str(auth.org_id) if auth.org_id else None,
    }
