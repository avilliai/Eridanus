import asyncio
import json
from typing import Type, Union

from fastapi import FastAPI, Request
import uvicorn

from developTools.event.base import EventBase
from developTools.event.eventFactory import EventFactory
from developTools.interface.sendMes import MailMan

from developTools.utils.logger import get_logger


class EventBus:
    def __init__(self) -> None:
        self.handlers: dict[Type[EventBase], set] = {}

    def subscribe(self, event: Type[EventBase], handler):
        if event not in self.handlers:
            self.handlers[event] = set()
        self.handlers[event].add(handler)

    def on(self, event: Type[EventBase]):
        def decorator(func):
            self.subscribe(event, func)
            return func
        return decorator

    async def emit(self, event_instance: EventBase) -> None:
        event_type = type(event_instance)
        if handlers := self.handlers.get(event_type):
            for handler in handlers:
                await handler(event_instance)
        else:
            print(f"未找到处理 {event_type} 的监听器")


class HTTPBot(MailMan):
    def __init__(self,http_sever,access_token):
        super().__init__(http_sever,access_token)
        self.logger = get_logger()
        self.event_bus = EventBus()

        self.echo_dict = {}
        self.app = FastAPI()  # 内部创建 FastAPI 应用
        self._register_routes()  # 注册路由

    def _register_routes(self):
        @self.app.post("/")
        async def root(request: Request):
            """
            接收 HTTP 消息并传递给 HTTPBot
            """
            data = await request.json()  # 获取事件数据
            await self.receive(data)  # 将消息传递给 HTTPBot 的 receive 方法
            return {"status": "success"}

    def on(self, event: Type[EventBase]):
        return self.event_bus.on(event)

    async def receive(self, data: dict):
        """
        处理接收到的 HTTP 消息。
        """
        self.logger.info(f"收到消息: {data}")
        event_obj = EventFactory.create_event(data)
        if event_obj:
            await self.event_bus.emit(event_obj)
        else:
            self.logger.warning("无法匹配事件类型，跳过处理。")





    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """
        启动 FastAPI 应用
        """
        uvicorn.run(self.app, host=host, port=port)


# 示例用法

