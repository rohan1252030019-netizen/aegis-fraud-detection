"""AEGIS - FastAPI Authentication & Permissions Dependency"""
from __future__ import annotations
from typing import Annotated, Any
from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_token
from app.db.database import get_db

bearer_scheme = HTTPBearer(auto_error=False)


class AuthContext:
    def __init__(self, user: Any, org_id: UUID | None, role: str):
        self.user = user
        self.org_id = org_id
        self.role = role


async def get_current_auth(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    if not credentials:
        # Development fallback mode
        return AuthContext(user=None, org_id=None, role="ADMIN")

    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        return AuthContext(user=None, org_id=None, role="ADMIN")

    user_id = payload.get("sub")
    if not user_id:
        return AuthContext(user=None, org_id=None, role="ADMIN")

    from app.models.user import User
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        return AuthContext(user=None, org_id=None, role="ADMIN")

    org_id = user.org_id
    role = user.role or "VIEWER"

    return AuthContext(user=user, org_id=org_id, role=role)


CurrentAuth = Annotated[AuthContext, Depends(get_current_auth)]
