import asyncio
import json

import nats

from ollama_service.core.nats_config import NATS_URL
from ollama_service.services import ask_model, fetch_models, pull_model, stream_pull
from shared.nats_subjects import CHAT_SUBJECT, MODELS_SUBJECT, PULL_STREAM_SUBJECT, PULL_SUBJECT, WORKERS_QUEUE


async def _respond_json(msg, payload: dict):
    await msg.respond(json.dumps(payload, ensure_ascii=False).encode("utf-8"))


async def models_handler(msg):
    try:
        await _respond_json(msg, {"models": fetch_models()})
    except Exception as exc:
        await _respond_json(msg, {"error": str(exc)})


async def chat_handler(msg):
    try:
        payload = json.loads(msg.data.decode("utf-8"))
        answer = ask_model(
            model=payload["model"].strip(),
            user_names=payload["user_names"],
            users_cards=payload["users_cards"],
            question=payload["question"].strip(),
        )
        await _respond_json(msg, {"answer": answer})
    except Exception as exc:
        await _respond_json(msg, {"error": str(exc)})


async def pull_handler(msg):
    try:
        payload = json.loads(msg.data.decode("utf-8"))
        await _respond_json(msg, pull_model(payload["model"].strip()))
    except Exception as exc:
        await _respond_json(msg, {"error": str(exc)})


async def pull_stream_handler(nc, msg):
    payload = json.loads(msg.data.decode("utf-8"))
    model = payload["model"].strip()
    stream_subject = payload["stream_subject"]

    try:
        for event_line in stream_pull(model):
            await nc.publish(stream_subject, event_line.encode("utf-8"))
        await nc.publish(
            stream_subject,
            json.dumps({"done": True, "status": f"Модель {model} загружена"}, ensure_ascii=False).encode("utf-8"),
        )
    except Exception as exc:
        await nc.publish(
            stream_subject,
            json.dumps({"done": True, "error": str(exc)}, ensure_ascii=False).encode("utf-8"),
        )


async def run_worker():
    nc = await nats.connect(NATS_URL)

    async def pull_stream_callback(msg):
        await pull_stream_handler(nc, msg)

    await nc.subscribe(MODELS_SUBJECT, queue=WORKERS_QUEUE, cb=models_handler)
    await nc.subscribe(CHAT_SUBJECT, queue=WORKERS_QUEUE, cb=chat_handler)
    await nc.subscribe(PULL_SUBJECT, queue=WORKERS_QUEUE, cb=pull_handler)
    await nc.subscribe(
        PULL_STREAM_SUBJECT,
        queue=WORKERS_QUEUE,
        cb=pull_stream_callback,
    )

    print("ollama worker connected to NATS")
    await asyncio.Event().wait()


def main():
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
