import asyncio
from typing import Type, Union

import websockets
import json
from collections.abc import Callable, Coroutine

from EridanusTools.event.base import EventBase
from EridanusTools.event.eventFactory import EventFactory
from EridanusTools.message.message_chain import MessageChain
from EridanusTools.message.message_components import MessageComponent, Text
from EridanusTools.utils.logger import get_logger


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
        self.event_bus = EventBus()
        self.logger=get_logger()

    async def _receive(self):
        if 1:
            while True:
                response = await self.websocket.recv()
                data = json.loads(response)
                self.logger.info(f"收到服务端响应:{data}")

                # 使用 EventFactory 动态实例化事件对象
                event_obj = EventFactory.create_event(data)
                if event_obj:
                    await self.event_bus.emit(event_obj)
                else:
                    self.logger.warning("无法匹配事件类型，跳过处理。")


    async def _connect_and_run(self):
        await self._connect()
        if self.websocket:
            await self._receive()

    async def _connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info("WebSocket 连接已建立")
        except Exception as e:
            self.logger.error(f"WebSocket 连接出现错误:{e}")

    def run(self):
        asyncio.run(self._connect_and_run())

    def on(self, event: Type[EventBase]):
        return self.event_bus.on(event)
    """
    以下内容为特殊函数实现
    """
    async def groupList(self):
        #还需要进一步修改，需要使用echo参数判断专有返回值，目前还没有做
        r=await self.websocket.send(json.dumps({"action": "get_group_list"}))
        print(r)
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

