import asyncio
import threading
import uuid

from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from typing import Type, Union, Dict

import websockets
import json
from collections.abc import Callable, Coroutine

from developTools.event.base import EventBase
from developTools.event.eventFactory import EventFactory
from developTools.message.message_chain import MessageChain
from developTools.message.message_components import MessageComponent, Text
from developTools.utils.logger import get_logger


# 引入 EventBus
class EventBus:
    def __init__(self) -> None:
        # 将事件类作为关键字
        self.handlers: dict[Type[EventBase], set[Callable[..., Coroutine[None, None, None]]]] = {}

    def subscribe(self, event: Type[EventBase], handler: Callable[..., Coroutine[None, None, None]]) -> None:
        if event not in self.handlers:
            self.handlers[event] = set()
        self.handlers[event].add(handler)

    def on(self, event: Type[EventBase]):
        """
        装饰器，用于注册事件监听器。
        """
        def decorator(func: Callable[..., Coroutine[None, None, None]]) -> Callable[..., Coroutine[None, None, None]]:
            self.subscribe(event, func)
            return func

        return decorator

    async def emit(self, event_instance: EventBase) -> None:
        """
        触发事件，将实例分发给已注册的处理函数。
        """
        event_type = type(event_instance)
        if handlers := self.handlers.get(event_type):
            for handler in handlers:
                await handler(event_instance)
        else:
            print(f"未找到处理 {event_type} 的监听器")

# WebSocketBot 集成 EventBus

class WebSocketBot:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.logger = get_logger()
        self.event_bus = EventBus()
        self.response_callbacks: Dict[str, asyncio.Future] = {}  # 存储 echo 和对应的 Future

    async def _receive(self):
        """
        接收服务端消息并分发处理。
        """
        while True:
            response = await self.websocket.recv()
            data = json.loads(response)
            self.logger.info(f"收到服务端响应: {data}")

            # 如果是响应消息
            if "status" in data and "echo" in data:
                echo = data["echo"]
                future = self.response_callbacks.pop(echo, None)
                if future and not future.done():
                    future.set_result(data)
            # 如果是事件消息
            elif "post_type" in data:
                event_obj = EventFactory.create_event(data)
                if event_obj:
                    await self.event_bus.emit(event_obj)
                else:
                    self.logger.warning("无法匹配事件类型，跳过处理。")
            else:
                self.logger.warning("收到未知消息格式，已忽略。")

    async def _connect_and_run(self):
        """
        建立 WebSocket 连接并开始接收消息。
        """
        await self._connect()
        if self.websocket:
            await self._receive()

    async def _connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info("WebSocket 连接已建立")
        except Exception as e:
            self.logger.error(f"WebSocket 连接出现错误: {e}")

    async def _call_api(self, action: str, params: dict, timeout: int = 20) -> dict:
        """
        发送请求并异步等待响应。
        """
        if self.websocket is None:
            self.logger.warning("WebSocket 未连接，无法调用 API。")
            return {"status": "failed", "retcode": -1, "data": None, "echo": str(uuid.uuid4())}

        echo = str(uuid.uuid4())
        message = {"action": action, "params": params, "echo": echo}

        # 创建一个 Future，用于等待响应
        future = asyncio.Future()
        self.response_callbacks[echo] = future

        await self.websocket.send(json.dumps(message))
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.error(f"调用 API 超时: {action}")
            raise TimeoutError(f"调用 API 超时: {action}")

    async def groupList(self):
        """
        获取群列表。
        """
        return await self._call_api("get_group_list", {})

    def run(self):
        asyncio.run(self._connect_and_run())

    def on(self, event: Type[EventBase]):
        """
        保留 on 装饰器，用于订阅事件。
        """
        return self.event_bus.on(event)

    """
    以下为消息发送相关函数
    """
    async def send_to_sever(self, event: EventBase, message: Union[MessageChain, dict]):
        """
        发送消息，可以接受 MessageChain 或原始字典格式的消息。

        Args:
            message (Union[MessageChain, dict]): 消息链或字典。
        """
        try:
            if self.websocket:

                #self.logger.info(f"发送的消息: {message}")
                if event.message_type=="group":
                    data={
                        "action": "send_group_msg",
                        "params": {
                            "group_id": event.group_id,
                            "message": message.to_dict()
                        },
                        "echo": "reply_to_group"
                    }
                elif event.message_type=="private":
                    data={
                        "action": "send_private_msg",
                        "params": {
                            "user_id": event.user_id,
                            "message": message.to_dict()
                        },
                        "echo": "reply_to_private"
                    }

                await self.websocket.send(json.dumps(data))

            else:
                self.logger.warning("WebSocket 未连接，无法发送消息")
        except Exception as e:
            self.logger.error(f"发送消息时出现错误: {e}", exc_info=True)

    async def send(self, event: EventBase, components: list[Union[MessageComponent, str]]):
        """
        构建并发送消息链。

        Args:
            components (list[Union[MessageComponent, str]]): 消息组件或字符串。
        """
        try:
            # 将字符串自动转换为 Text 对象
            processed_components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

            message_chain = MessageChain(processed_components)
            await self.send_to_sever(event, message_chain)
        except Exception as e:
            self.logger.error(f"发送消息时出现错误: {e}", exc_info=True)
    async def send_friend_message(self, user_id: int, components: list[Union[MessageComponent, str]]):

        processed_components = [
            Text(component) if isinstance(component, str) else component
            for component in components
        ]

        message = MessageChain(processed_components)
        data = {
            "action": "send_private_msg",
            "params": {
                "user_id": user_id,
                "message": message.to_dict()
            },
            "echo": "reply_to_private"
        }

        await self.websocket.send(json.dumps(data))
    async def send_group_message(self, group_id: int, components: list[Union[MessageComponent, str]]):
        processed_components = [
            Text(component) if isinstance(component, str) else component
            for component in components
        ]

        message = MessageChain(processed_components)
        data = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": message.to_dict()
            },
            "echo": "reply_to_group"
        }

        await self.websocket.send(json.dumps(data))

