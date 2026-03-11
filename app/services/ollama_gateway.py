import json
from typing import Any

from fastapi import HTTPException

from app.core.nats_client import nats_manager
from shared.nats_subjects import CHAT_SUBJECT, MODELS_SUBJECT, PULL_STREAM_SUBJECT, PULL_SUBJECT


async def get_models() -> list[str]:
    payload = await nats_manager.request_json(MODELS_SUBJECT, {}, timeout=10)
    return payload.get("models", [])


async def ask_model(model: str, user_names: list[str], users_cards: dict[str, Any], question: str) -> str:
    payload = await nats_manager.request_json(
        CHAT_SUBJECT,
        {
            "model": model,
            "user_names": user_names,
            "users_cards": users_cards,
            "question": question,
        },
        timeout=120,
    )
    answer = payload.get("answer", "").strip()
    if not answer:
        raise HTTPException(status_code=502, detail="Пустой ответ от ollama worker")
    return answer


async def pull_model(model: str) -> dict[str, Any]:
    return await nats_manager.request_json(
        PULL_SUBJECT,
        {"model": model},
        timeout=600,
    )


async def stream_pull(model: str):
    subscription, queue = await nats_manager.subscribe_stream(
        PULL_STREAM_SUBJECT,
        {"model": model},
    )

    async def generate():
        try:
            while True:
                event = await queue.get()
                yield f"{json.dumps(event, ensure_ascii=False)}\n"
                if event.get("done"):
                    break
        finally:
            await subscription.unsubscribe()

    return generate()
