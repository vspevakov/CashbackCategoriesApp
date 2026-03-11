import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "cashback_data.json"
CATEGORY_FILE = DATA_DIR / "categories.json"

DEFAULT_CATEGORIES = [
    "Супермаркеты",
    "Рестораны и кафе",
    "Такси",
    "АЗС",
    "Аптеки",
    "Путешествия",
    "Развлечения",
    "Онлайн-покупки",
]


def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")
    if not CATEGORY_FILE.exists():
        CATEGORY_FILE.write_text(
            json.dumps(DEFAULT_CATEGORIES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_data() -> dict[str, dict[str, dict[str, Any]]]:
    ensure_data_file()
    raw = DATA_FILE.read_text(encoding="utf-8").strip() or "{}"
    loaded = json.loads(raw)
    if not isinstance(loaded, dict):
        raise ValueError("Data file must contain a JSON object")
    return loaded


def load_categories() -> list[str]:
    ensure_data_file()
    raw = CATEGORY_FILE.read_text(encoding="utf-8").strip() or "[]"
    loaded = json.loads(raw)
    if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
        raise ValueError("Category file must contain a JSON array of strings")
    return loaded


def save_data(data: dict[str, Any]) -> None:
    ensure_data_file()
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_categories(categories: list[str]) -> None:
    ensure_data_file()
    CATEGORY_FILE.write_text(
        json.dumps(categories, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def normalize_category_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        enabled = bool(value.get("enabled", False))
        percent_raw = value.get("percent", 0)
        try:
            percent = float(percent_raw)
        except (TypeError, ValueError):
            percent = 0.0
        return {
            "enabled": enabled,
            "percent": max(percent, 0.0),
        }

    if isinstance(value, bool):
        return {
            "enabled": value,
            "percent": 0.0,
        }

    if isinstance(value, (int, float)):
        percent = max(float(value), 0.0)
        return {
            "enabled": percent > 0,
            "percent": percent,
        }

    return {
        "enabled": False,
        "percent": 0.0,
    }


def normalize_data(
    data: dict[str, dict[str, dict[str, Any]]],
    categories: list[str],
) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    normalized: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for user_name, cards in data.items():
        normalized[user_name] = {}
        for card_name, card_categories in cards.items():
            normalized[user_name][card_name] = {
                category: normalize_category_value(card_categories.get(category, False))
                for category in categories
            }
    return normalized


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CardCreate(BaseModel):
    user_name: str = Field(min_length=1, max_length=100)
    card_name: str = Field(min_length=1, max_length=100)


class CashbackCategoryPayload(BaseModel):
    enabled: bool = False
    percent: float = Field(default=0, ge=0, le=100)


class CashbackSave(BaseModel):
    user_name: str = Field(min_length=1, max_length=100)
    card_name: str = Field(min_length=1, max_length=100)
    categories: dict[str, CashbackCategoryPayload]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


app = FastAPI(title="Cashback Categories")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"categories": load_categories()},
    )


@app.get("/summary", response_class=HTMLResponse)
async def summary_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="summary.html",
        context={},
    )


@app.get("/api/state")
async def get_state() -> dict[str, Any]:
    categories = load_categories()
    data = normalize_data(load_data(), categories)
    save_data(data)
    return {
        "users": data,
        "available_categories": categories,
    }


@app.post("/api/users")
async def create_user(payload: UserCreate) -> dict[str, Any]:
    user_name = payload.name.strip()
    categories = load_categories()
    data = normalize_data(load_data(), categories)
    if user_name in data:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    data[user_name] = {}
    save_data(data)
    return {"message": "Пользователь создан", "users": data}


@app.post("/api/cards")
async def create_card(payload: CardCreate) -> dict[str, Any]:
    user_name = payload.user_name.strip()
    card_name = payload.card_name.strip()
    categories = load_categories()
    data = normalize_data(load_data(), categories)

    if user_name not in data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if card_name in data[user_name]:
        raise HTTPException(status_code=400, detail="Карта уже существует")

    data[user_name][card_name] = {
        category: {"enabled": False, "percent": 0.0} for category in categories
    }
    save_data(data)
    return {"message": "Карта создана", "users": data}


@app.post("/api/categories")
async def create_category(payload: CategoryCreate) -> dict[str, Any]:
    category_name = payload.name.strip()
    categories = load_categories()
    data = normalize_data(load_data(), categories)

    if category_name in categories:
        raise HTTPException(status_code=400, detail="Категория уже существует")

    categories.append(category_name)
    normalized = normalize_data(data, categories)
    save_categories(categories)
    save_data(normalized)
    return {
        "message": "Категория добавлена",
        "users": normalized,
        "available_categories": categories,
    }


@app.post("/api/cashback")
async def save_cashback(payload: CashbackSave) -> dict[str, Any]:
    user_name = payload.user_name.strip()
    card_name = payload.card_name.strip()
    categories = load_categories()
    invalid_categories = set(payload.categories).difference(categories)

    if invalid_categories:
        raise HTTPException(status_code=400, detail="Переданы неизвестные категории")

    data = normalize_data(load_data(), categories)
    if user_name not in data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if card_name not in data[user_name]:
        data[user_name][card_name] = {}

    data[user_name][card_name] = {
        category: {
            "enabled": payload.categories.get(category, CashbackCategoryPayload()).enabled,
            "percent": payload.categories.get(category, CashbackCategoryPayload()).percent,
        }
        for category in categories
    }
    save_data(data)
    return {"message": "Категории сохранены", "users": data}
