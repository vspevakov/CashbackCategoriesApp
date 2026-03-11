from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.cashback import CardCreate
from app.services import data_store


router = APIRouter(prefix="/api", tags=["cards"])


@router.post("/cards")
async def create_card(payload: CardCreate) -> dict[str, Any]:
    user_name = payload.user_name.strip()
    card_name = payload.card_name.strip()
    state = data_store.load_state()
    users = state["users"]
    categories = state["available_categories"]

    if user_name not in users:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if card_name in users[user_name]:
        raise HTTPException(status_code=400, detail="Карта уже существует")

    users[user_name][card_name] = {
        category: {"enabled": False, "percent": 0.0} for category in categories
    }
    data_store.save_data(users)
    return {"message": "Карта создана", "users": users}
