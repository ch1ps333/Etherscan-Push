from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from cachetools import TTLCache


class AntiFloodMiddleware(BaseMiddleware):

    def __init__(self, timeLimit: float=1.0):
        self.limit = TTLCache(maxsize=10_000, ttl=timeLimit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.chat.id in self.limit:
            return
        else:
            self.limit[event.chat.id] = None
        return await handler(event, data)