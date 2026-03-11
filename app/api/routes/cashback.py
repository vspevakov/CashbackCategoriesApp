from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.cashback import CashbackCategoryPayload, CashbackSave
from app.services import data_store


router = APIRouter(prefix="/api", tags=["cashback"])


@router.post("/cashback")
async def save_cashback(payload: CashbackSave) -> dict[str, Any]:
    user_name = payload.user_name.strip()
    card_name = payload.card_name.strip()
    state = data_store.load_state()
    users = state["users"]
    categories = state["available_categories"]
    invalid_categories = set(payload.categories).difference(categories)

    if invalid_categories:
        raise HTTPException(status_code=400, detail="Переданы неизвестные категории")
    if user_name not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if card_name not in users[user_name]:
        users[user_name][card_name] = {}

    users[user_name][card_name] = {
        category: {
            "enabled": payload.categories.get(category, CashbackCategoryPayload()).enabled,
            "percent": payload.categories.get(category, CashbackCategoryPayload()).percent,
        }
        for category in categories
    }
    data_store.save_data(users)
    return {"message": "Категории сохранены", "users": users}
