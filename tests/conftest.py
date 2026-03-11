import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.nats_client import nats_manager
from app.main import app
from app.services import data_store


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str):
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    data_file = data_dir / "cashback_data.json"
    category_file = data_dir / "categories.json"
    data_file.write_text(
        json.dumps(_load_fixture("cashback_data.json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    category_file.write_text(
        json.dumps(_load_fixture("categories.json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setattr(data_store, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_store, "DATA_FILE", data_file)
    monkeypatch.setattr(data_store, "CATEGORY_FILE", category_file)
    monkeypatch.setattr(
        data_store,
        "DEFAULT_CATEGORIES",
        _load_fixture("categories.json"),
    )
    return data_dir


@pytest.fixture
def client(isolated_data_dir):
    async def fake_connect():
        return None

    async def fake_close():
        return None

    nats_manager.connect = fake_connect
    nats_manager.close = fake_close
    return TestClient(app)
