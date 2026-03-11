from ollama_service.services import chat_service, model_service, pull_service
from ollama_service.services.prompt_loader import build_prompt, load_system_prompt


def test_model_service_returns_model_names(monkeypatch):
    monkeypatch.setattr(
        model_service,
        "get_json",
        lambda path: {
            "models": [{"name": "llama3.1:8b"}, {"name": "qwen2.5:7b"}]
        },
    )

    assert model_service.fetch_models() == ["llama3.1:8b", "qwen2.5:7b"]


def test_chat_service_uses_prompt_and_returns_answer(monkeypatch):
    monkeypatch.setattr(chat_service, "build_prompt", lambda *args, **kwargs: "prompt")
    monkeypatch.setattr(
        chat_service,
        "post_json",
        lambda path, payload, timeout: {"response": "Лучшая карта: Tinkoff Black"},
    )

    answer = chat_service.ask_model(
        model="llama3.1:8b",
        user_names=["Иван", "Мария"],
        users_cards={
            "Иван": {"Tinkoff Black": {"Супермаркеты": {"enabled": True, "percent": 5}}},
            "Мария": {"Sber Prime": {"Такси": {"enabled": True, "percent": 7}}},
        },
        question="По какой карте лучше купить продукты?",
    )

    assert answer == "Лучшая карта: Tinkoff Black"


def test_pull_service_returns_payload(monkeypatch):
    monkeypatch.setattr(
        pull_service,
        "post_json",
        lambda path, payload, timeout: {"status": f"pulled {payload['model']}"},
    )

    assert pull_service.pull_model("llama3.1:8b") == {"status": "pulled llama3.1:8b"}


def test_prompt_loader_reads_skill_file():
    prompt = load_system_prompt()
    built = build_prompt(
        user_names=["Иван", "Мария"],
        users_cards={
            "Иван": {"Tinkoff Black": {"Супермаркеты": {"enabled": True, "percent": 5}}},
            "Мария": {"Sber Prime": {"Такси": {"enabled": True, "percent": 7}}},
        },
        question="По какой карте лучше купить продукты?",
    )

    assert "Cashback Manager" in prompt
    assert "Выбранные пользователи: Иван, Мария" in built
    assert "По какой карте лучше купить продукты?" in built
