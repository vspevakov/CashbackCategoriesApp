from typing import Any

from fastapi import APIRouter

from app.services import data_store


router = APIRouter(prefix="/api", tags=["state"])


@router.get("/state")
async def get_state() -> dict[str, Any]:
    return data_store.load_state()
