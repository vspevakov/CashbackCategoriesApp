from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.cashback import CategoryCreate
from app.services import data_store


router = APIRouter(prefix="/api", tags=["categories"])


@router.post("/categories")
async def create_category(payload: CategoryCreate) -> dict[str, Any]:
    category_name = payload.name.strip()
    state = data_store.load_state()
    users = state["users"]
    categories = state["available_categories"]

    if category_name in categories:
        raise HTTPException(status_code=400, detail="Категория уже существует")

    categories.append(category_name)
    normalized = data_store.normalize_data(users, categories)
    data_store.save_categories(categories)
    data_store.save_data(normalized)
    return {
        "message": "Категория добавлена",
        "users": normalized,
        "available_categories": categories,
    }
