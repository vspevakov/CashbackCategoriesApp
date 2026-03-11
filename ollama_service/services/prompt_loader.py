import json
from pathlib import Path


PROMPT_FILE = Path(__file__).resolve().parents[2] / "SKILLS" / "cashback_manager.md"


def load_system_prompt() -> str:
    return PROMPT_FILE.read_text(encoding="utf-8").strip()


def build_prompt(user_names: list[str], users_cards: dict, question: str) -> str:
    cards_json = json.dumps(users_cards, ensure_ascii=False, indent=2)
    system_prompt = load_system_prompt()
    return f"""
{system_prompt}

Выбранные пользователи: {", ".join(user_names)}

Карты и категории пользователей:
{cards_json}

Вопрос:
{question}
""".strip()
