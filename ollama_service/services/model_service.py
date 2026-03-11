from ollama_service.services.client import get_json


def fetch_models() -> list[str]:
    payload = get_json("/api/tags")
    models = payload.get("models", [])
    return [model["name"] for model in models if isinstance(model, dict) and model.get("name")]
