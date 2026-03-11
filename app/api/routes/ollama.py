from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.cashback import OllamaChatRequest, OllamaPullRequest
from app.services import data_store, ollama_gateway


router = APIRouter(prefix="/api/ollama", tags=["ollama"])


@router.get("/models")
async def get_ollama_models() -> dict[str, list[str]]:
    return {"models": await ollama_gateway.get_models()}


@router.post("/chat")
async def chat_with_ollama(payload: OllamaChatRequest) -> dict[str, str]:
    user_names = [user_name.strip() for user_name in payload.user_names if user_name.strip()]
    if not user_names:
        raise HTTPException(status_code=400, detail="Нужно выбрать хотя бы одного пользователя")
    users_cards = data_store.get_multiple_users_cards(user_names)
    answer = await ollama_gateway.ask_model(
        model=payload.model.strip(),
        user_names=user_names,
        users_cards=users_cards,
        question=payload.question.strip(),
    )
    return {"answer": answer}


@router.post("/pull")
async def pull_model(payload: OllamaPullRequest) -> dict[str, Any]:
    return await ollama_gateway.pull_model(payload.model.strip())


@router.get("/pull-stream")
async def pull_model_stream(model: str) -> StreamingResponse:
    model_name = model.strip()
    if not model_name:
        raise HTTPException(status_code=400, detail="Нужно указать модель")
    return StreamingResponse(
        await ollama_gateway.stream_pull(model_name),
        media_type="application/x-ndjson",
    )
