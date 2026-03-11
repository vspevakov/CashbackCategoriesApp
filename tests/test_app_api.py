from app.services import ollama_gateway


def test_get_state_returns_users_and_categories(client):
    response = client.get("/api/state")

    assert response.status_code == 200
    payload = response.json()
    assert "users" in payload
    assert "available_categories" in payload
    assert "Иван" in payload["users"]
    assert "Супермаркеты" in payload["available_categories"]


def test_create_user_adds_new_user(client):
    response = client.post("/api/users", json={"name": "Ольга"})

    assert response.status_code == 200
    payload = response.json()
    assert "Ольга" in payload["users"]
    assert payload["users"]["Ольга"] == {}


def test_create_card_adds_card_with_all_categories(client):
    response = client.post(
        "/api/cards",
        json={"user_name": "Иван", "card_name": "Газпромбанк Premium"},
    )

    assert response.status_code == 200
    payload = response.json()
    card = payload["users"]["Иван"]["Газпромбанк Premium"]
    assert set(card) == {"Супермаркеты", "Рестораны и кафе", "Такси", "АЗС"}
    assert card["АЗС"] == {"enabled": False, "percent": 0.0}


def test_save_cashback_updates_percent_and_enabled(client):
    response = client.post(
        "/api/cashback",
        json={
            "user_name": "Иван",
            "card_name": "Tinkoff Black",
            "categories": {
                "Супермаркеты": {"enabled": True, "percent": 10},
                "Рестораны и кафе": {"enabled": False, "percent": 0},
                "Такси": {"enabled": True, "percent": 3},
                "АЗС": {"enabled": False, "percent": 0},
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    updated = payload["users"]["Иван"]["Tinkoff Black"]
    assert updated["Супермаркеты"] == {"enabled": True, "percent": 10.0}
    assert updated["Такси"] == {"enabled": True, "percent": 3.0}


def test_ollama_chat_uses_gateway(client, monkeypatch):
    async def fake_ask_model(model, user_names, users_cards, question):
        assert model == "llama3.1:8b"
        assert user_names == ["Иван", "Мария", "Алексей"]
        assert "Иван" in users_cards
        assert "Мария" in users_cards
        assert "Алексей" in users_cards
        assert "купить продукты" in question
        return "Лучший вариант: Иван — Tinkoff Black"

    monkeypatch.setattr(ollama_gateway, "ask_model", fake_ask_model)

    response = client.post(
        "/api/ollama/chat",
        json={
            "user_names": ["Иван", "Мария", "Алексей"],
            "model": "llama3.1:8b",
            "question": "По какой карте лучше купить продукты?",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Лучший вариант: Иван — Tinkoff Black"
