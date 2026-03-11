import json
from typing import Any

from fastapi import HTTPException

from app.core.config import CATEGORY_FILE, DATA_DIR, DATA_FILE, DEFAULT_CATEGORIES


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")
    if not CATEGORY_FILE.exists():
        CATEGORY_FILE.write_text(
            json.dumps(DEFAULT_CATEGORIES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_raw_data() -> dict[str, dict[str, dict[str, Any]]]:
    ensure_data_files()
    raw = DATA_FILE.read_text(encoding="utf-8").strip() or "{}"
    loaded = json.loads(raw)
    if not isinstance(loaded, dict):
        raise ValueError("Data file must contain a JSON object")
    return loaded


def load_categories() -> list[str]:
    ensure_data_files()
    raw = CATEGORY_FILE.read_text(encoding="utf-8").strip() or "[]"
    loaded = json.loads(raw)
    if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
        raise ValueError("Category file must contain a JSON array of strings")
    return loaded


def save_data(data: dict[str, Any]) -> None:
    ensure_data_files()
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_categories(categories: list[str]) -> None:
    ensure_data_files()
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


def load_state() -> dict[str, Any]:
    categories = load_categories()
    data = normalize_data(load_raw_data(), categories)
    save_data(data)
    return {
        "users": data,
        "available_categories": categories,
    }


def get_user_cards(user_name: str) -> dict[str, dict[str, dict[str, Any]]]:
    state = load_state()
    user_cards = state["users"].get(user_name)
    if user_cards is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user_cards


def get_multiple_users_cards(user_names: list[str]) -> dict[str, dict[str, dict[str, dict[str, Any]]]]:
    state = load_state()
    users = state["users"]
    result: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    missing: list[str] = []

    for user_name in user_names:
        normalized_name = user_name.strip()
        user_cards = users.get(normalized_name)
        if user_cards is None:
            missing.append(normalized_name)
        else:
            result[normalized_name] = user_cards

    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Пользователи не найдены: {', '.join(missing)}",
        )
    return result
