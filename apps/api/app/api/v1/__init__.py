"""AEGIS - API v1 Router Aggregator"""
from fastapi import APIRouter
from app.api.v1 import auth, accounts_transactions, analytics_graph

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(accounts_transactions.router, tags=["Accounts & Transactions"])
api_router.include_router(analytics_graph.router, tags=["Analytics & Graph"])
