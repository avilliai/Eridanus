#实现黑白名单判断，后续aiReplyCore的阻断也将在这里实现
import asyncio
import json
from typing import Union

import websockets

from developTools.adapters.websocket_adapter import WebSocketBot
from developTools.event.base import EventBase
from developTools.event.eventFactory import EventFactory
from developTools.message.message_components import MessageComponent, Reply, Text, Music, At, Poke, File


class ExtendBot(WebSocketBot):
    def __init__(self, uri: str, config, **kwargs):
        super().__init__(uri, **kwargs)
        self.config = config
        self.id = 1000000

    async def _receive(self):
        """
        接收服务端消息并分发处理。
        """
        try:
            async for response in self.websocket:
                data = json.loads(response)
                #self.logger.info(f"收到服务端响应: {data},{type(data)}")
                if 'heartbeat' not in str(data):
                    self.logger.info_msg(f"收到服务端响应: {data}")
                # 如果是响应消息
                if "status" in data and "echo" in data:
                    echo = data["echo"]
                    future = self.response_callbacks.pop(echo, None)
                    if future and not future.done():
                        future.set_result(data)
                elif "post_type" in data:
                    event_obj = EventFactory.create_event(data)
                    try:
                        if event_obj.post_type == "meta_event":

                            if event_obj.meta_event_type == "lifecycle":

                                self.id = int(event_obj.self_id)
                                self.logger.info(f"Bot ID: {self.id},{type(self.id)}")
                    except:
                        pass
                    if hasattr(event_obj, "group_id"):
                        if self.config.common_config.basic_config["group_handle_logic"] == "blacklist":
                            if event_obj.group_id not in self.config.common_config.censor_group["blacklist"]:
                                if hasattr(event_obj, "user_id"):
                                    if self.config.common_config.basic_config["user_handle_logic"] == "blacklist":
                                        if event_obj.user_id not in self.config.common_config.censor_user["blacklist"]:
                                            asyncio.create_task(self.event_bus.emit(event_obj))
                                        else:
                                            self.logger.info(f"用户{event_obj.user_id}在黑名单中，跳过处理。")
                                    elif self.config.common_config.basic_config["user_handle_logic"] == "whitelist":
                                        if event_obj.user_id in self.config.common_config.censor_user["whitelist"]:
                                            asyncio.create_task(self.event_bus.emit(event_obj))
                                        else:
                                            self.logger.info(f"用户{event_obj.user_id}不在白名单中，跳过处理。")
                                else:
                                    asyncio.create_task(self.event_bus.emit(event_obj))
                            else:
                                self.logger.info(f"群{event_obj.group_id}在黑名单中，跳过处理。")
                        elif self.config.common_config.basic_config["group_handle_logic"] == "whitelist":
                            if event_obj.group_id in self.config.common_config.censor_group["whitelist"]:
                                if hasattr(event_obj, "user_id"):
                                    if self.config.common_config.basic_config["user_handle_logic"] == "blacklist":
                                        if event_obj.user_id not in self.config.common_config.censor_user["blacklist"]:
                                            asyncio.create_task(self.event_bus.emit(event_obj))
                                        else:
                                            self.logger.info(f"用户{event_obj.user_id}在黑名单中，跳过处理。")
                                    elif self.config.common_config.basic_config["user_handle_logic"] == "whitelist":
                                        if event_obj.user_id in self.config.common_config.censor_user["whitelist"]:
                                            asyncio.create_task(self.event_bus.emit(event_obj))
                                        else:
                                            self.logger.info(f"用户{event_obj.user_id}不在白名单中，跳过处理。")
                                else:
                                    asyncio.create_task(self.event_bus.emit(event_obj))
                            else:
                                self.logger.info(f"群{event_obj.group_id}不在白名单中，跳过处理。")
                    elif hasattr(event_obj, "user_id"):
                        if self.config.common_config.basic_config["user_handle_logic"] == "blacklist":
                            if event_obj.user_id not in self.config.common_config.censor_user["blacklist"]:
                                asyncio.create_task(self.event_bus.emit(event_obj))
                            else:
                                self.logger.info(f"用户{event_obj.user_id}在黑名单中，跳过处理。")
                        elif self.config.common_config.basic_config["user_handle_logic"] == "whitelist":
                            if event_obj.user_id in self.config.common_config.censor_user["whitelist"]:
                                asyncio.create_task(self.event_bus.emit(event_obj))
                            else:
                                self.logger.info(f"用户{event_obj.user_id}不在白名单中，跳过处理。")
                    elif event_obj:
                        asyncio.create_task(self.event_bus.emit(event_obj))  #不能await，
                    else:
                        self.logger.warning(f"无法匹配的事件类型，请向开发群913122269反馈。源数据：{data}。")
                else:
                    self.logger.warning(f"收到未知消息格式，请向开发群913122269反馈。源数据：{data}。")
        except websockets.exceptions.ConnectionClosedError as e:
            self.logger.warning(f"WebSocket 连接关闭: {e}")
            self.logger.warning("5秒后尝试重连")
            await asyncio.sleep(5)
            await self._connect_and_run()
        except Exception as e:
            self.logger.error(f"接收消息时发生错误: {e}", exc_info=True)
        finally:
            # 取消所有未完成的 Future
            for future in self.response_callbacks.values():
                if not future.done():
                    future.cancel()
            self.response_callbacks.clear()
            self.receive_task = None

    async def send(self, event: EventBase, components: list[Union[MessageComponent, str]], Quote: bool = False):
        """
        构建并发送消息链。

        Args:
            components (list[Union[MessageComponent, str]]): 消息组件或字符串。
        """
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
        if self.config.common_config.basic_config["adapter"]["name"] == "Lagrange":
            if Quote:
                components.insert(0, Reply(id=str(event.message_id)))
            for index, item in enumerate(components):
                if isinstance(item, Music):
                    item.id=str(item.id)
                elif isinstance(item, At):
                    item.qq=str(item.qq)
                elif isinstance(item, Poke):
                    item.type=str(item.type)
                    item.id=str(item.id)
                elif isinstance(item,File):
                    item.file=item.file.replace("file://","")
                elif isinstance(item,Reply):
                    item.id=str(item.id)
                components[index] = item
            return await super().send(event, components)
        else:
            return await super().send(event, components, Quote)

