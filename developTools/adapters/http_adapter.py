import asyncio
import json
from typing import Type, Union

from fastapi import FastAPI, Request
import uvicorn

from developTools.event.base import EventBase
from developTools.event.eventFactory import EventFactory
from developTools.interface.http_sendMes import http_mailman

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
            tasks = [asyncio.create_task(handler(event_instance)) for handler in handlers]
            asyncio.gather(*tasks)
        else:
            pass
            #print(f"未找到处理 {event_type} 的监听器")

class HTTPBot(http_mailman):
    def __init__(self,http_sever,access_token="",host="0.0.0.0",port=8000):
        super().__init__(http_sever,access_token)
        self.logger = get_logger()
        self.event_bus = EventBus()
        self.host = host
        self.port = port
        self.echo_dict = {}
        self.app = FastAPI()
        self._register_routes()

    def _register_routes(self):
        @self.app.post("/")
        async def root(request: Request):
            """
            接收 HTTP 消息并传递给 HTTPBot
            """
            data = await request.json()
            await asyncio.create_task(self.receive(data))
            return {"status": "success"}

    def on(self, event: Type[EventBase]):
        return self.event_bus.on(event)

    async def receive(self, data: dict):
        """
        处理接收到的 HTTP 消息。
        """
        self.logger.info(f"收到消息: {data}")
        event_obj = EventFactory.create_event(data)
        #self.logger.info(event_obj)
        if event_obj:
            await self.event_bus.emit(event_obj)
        else:
            self.logger.warning("无法匹配事件类型，跳过处理。")

    def run(self):
        """
        启动 FastAPI 应用
        """
        startUp = {'time': 1735098202, 'self_id': 919467430, 'post_type': 'meta_event',
                       'meta_event_type': 'startUp', 'status': {'online': True, 'good': True}, 'interval': 30000}
        event_obj = EventFactory.create_event(startUp)
        asyncio.run(self.event_bus.emit(event_obj)) #伪造一个startUp

        uvicorn.run(self.app, host=self.host, port=self.port,log_level="warning")