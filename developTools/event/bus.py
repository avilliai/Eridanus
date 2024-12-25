import asyncio
from typing import Callable, Coroutine

from developTools.utils import logger


class EventBus:
    def __init__(self) -> None:
        self.handlers: dict[str, set[Callable[..., Coroutine[None, None, None]]]] = {}

    def subscribe(self, event: str, handler: Callable[..., Coroutine[None, None, None]]) -> None:
        if event not in self.handlers:
            self.handlers[event] = set()
        self.handlers[event].add(handler)

    def on(self, event: str):
        def decorator(func: Callable[..., Coroutine[None, None, None]]) -> Callable[..., Coroutine[None, None, None]]:
            self.subscribe(event, func)
            return func
        return decorator

    def emit(self, event, *args, **kwargs) -> bool:
        print(f"触发事件: {event}")  # 调试信息
        if self.handlers.get(event, None) is None:
            print(f"找不到事件 {event} 的响应器")
            return False

        for h in self.handlers[event]:
            asyncio.create_task(h(*args, **kwargs))
        return True