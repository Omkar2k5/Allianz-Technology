"""
Placeholder routes for future implementation
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def placeholder():
    return {"message": "Policies endpoints - to be implemented"}
