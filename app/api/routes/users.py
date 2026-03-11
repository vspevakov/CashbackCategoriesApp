from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.cashback import UserCreate
from app.services import data_store


router = APIRouter(prefix="/api", tags=["users"])


@router.post("/users")
async def create_user(payload: UserCreate) -> dict[str, Any]:
    user_name = payload.name.strip()
    state = data_store.load_state()
    users = state["users"]
    if user_name in users:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    users[user_name] = {}
    data_store.save_data(users)
    return {"message": "Пользователь создан", "users": users}
