from ollama_service.services.client import post_json, stream_post


def pull_model(model: str) -> dict:
    return post_json(
        "/api/pull",
        {
            "model": model,
            "stream": False,
        },
        timeout=600,
    )


def stream_pull(model: str):
    return stream_post(
        "/api/pull",
        {
            "model": model,
            "stream": True,
        },
        timeout=600,
    )
