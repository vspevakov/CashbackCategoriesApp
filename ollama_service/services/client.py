import json
from urllib import error, request as urllib_request

from fastapi import HTTPException

from ollama_service.core.config import OLLAMA_BASE_URL


def get_json(path: str, timeout: int = 10) -> dict:
    req = urllib_request.Request(f"{OLLAMA_BASE_URL}{path}", method="GET")
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=502,
            detail=f"Ollama вернула ошибку: {detail or exc.reason}",
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama недоступна по адресу {OLLAMA_BASE_URL}",
        ) from exc


def post_json(path: str, payload: dict, timeout: int) -> dict:
    req = urllib_request.Request(
        f"{OLLAMA_BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=502,
            detail=f"Ollama вернула ошибку: {detail or exc.reason}",
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama недоступна по адресу {OLLAMA_BASE_URL}",
        ) from exc


def stream_post(path: str, payload: dict, timeout: int):
    req = urllib_request.Request(
        f"{OLLAMA_BASE_URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        response = urllib_request.urlopen(req, timeout=timeout)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise HTTPException(
            status_code=502,
            detail=f"Ollama вернула ошибку: {detail or exc.reason}",
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama недоступна по адресу {OLLAMA_BASE_URL}",
        ) from exc

    def generate():
        with response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if line:
                    yield f"{line}\n"

    return generate()
