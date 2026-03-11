from fastapi import HTTPException

from ollama_service.services.client import post_json
from ollama_service.services.prompt_loader import build_prompt


def ask_model(model: str, user_names: list[str], users_cards: dict, question: str) -> str:
    payload = post_json(
        "/api/generate",
        {
            "model": model,
            "prompt": build_prompt(user_names, users_cards, question),
            "stream": False,
        },
        timeout=120,
    )
    answer = payload.get("response", "").strip()
    if not answer:
        raise HTTPException(status_code=502, detail="Ollama вернула пустой ответ")
    return answer
