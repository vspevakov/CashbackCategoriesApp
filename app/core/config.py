import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
TEST_DATA_DIR = os.getenv("TEST_DATA_DIR")
DATA_DIR = Path(TEST_DATA_DIR) if TEST_DATA_DIR else BASE_DIR / "data"
DATA_FILE = DATA_DIR / "cashback_data.json"
CATEGORY_FILE = DATA_DIR / "categories.json"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
NATS_URL = os.getenv("NATS_URL", "nats://127.0.0.1:4222")

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
