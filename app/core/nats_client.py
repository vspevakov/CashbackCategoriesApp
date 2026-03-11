import asyncio
import json
from typing import Any

import nats
from fastapi import HTTPException

from app.core.config import NATS_URL


class NatsClientManager:
    def __init__(self) -> None:
        self._nc = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._lock:
            if self._nc is None or self._nc.is_closed:
                self._nc = await nats.connect(NATS_URL)

    async def close(self) -> None:
        async with self._lock:
            if self._nc is not None and not self._nc.is_closed:
                await self._nc.drain()
                await self._nc.close()
            self._nc = None

    @property
    def client(self):
        if self._nc is None:
            raise RuntimeError("NATS client is not connected")
        return self._nc

    async def request_json(
        self,
        subject: str,
        payload: dict[str, Any],
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        await self.connect()
        try:
            msg = await self.client.request(
                subject,
                json.dumps(payload).encode("utf-8"),
                timeout=timeout,
            )
        except Exception as exc:
            raise HTTPException(status_code=503, detail="NATS request failed") from exc
        response = json.loads(msg.data.decode("utf-8"))
        if "error" in response:
            raise HTTPException(status_code=502, detail=response["error"])
        return response

    async def subscribe_stream(self, subject: str, payload: dict[str, Any]):
        await self.connect()
        inbox = self.client.new_inbox()
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        async def handler(msg):
            await queue.put(json.loads(msg.data.decode("utf-8")))

        subscription = await self.client.subscribe(inbox, cb=handler)
        await self.client.publish(
            subject,
            json.dumps({**payload, "stream_subject": inbox}).encode("utf-8"),
        )
        await self.client.flush()
        return subscription, queue


nats_manager = NatsClientManager()
