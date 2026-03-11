from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    model: str = Field(min_length=1, max_length=200)
    user_names: list[str] = Field(min_length=1)
    users_cards: dict[str, dict[str, dict[str, dict[str, Any]]]]
    question: str = Field(min_length=1, max_length=2000)


class PullRequest(BaseModel):
    model: str = Field(min_length=1, max_length=200)
