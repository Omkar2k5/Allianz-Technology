"""
Placeholder routes for future implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login():
    return {"message": "Auth endpoints - to be implemented"}
