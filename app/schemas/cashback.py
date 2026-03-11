from pydantic import BaseModel, Field


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


class OllamaChatRequest(BaseModel):
    user_names: list[str] = Field(min_length=1)
    model: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1, max_length=2000)


class OllamaPullRequest(BaseModel):
    model: str = Field(min_length=1, max_length=200)
