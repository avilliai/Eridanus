from typing import Union

import httpx

from EridanusTools.event.base import EventBase
from EridanusTools.message.message_chain import MessageChain
from EridanusTools.message.message_components import MessageComponent, Text
from EridanusTools.utils.logger import get_logger


class MailMan:
    def __init__(self, http_server):
        self.http_server = http_server
        self.logger = get_logger()

    async def get_status(self):
        url = f"{self.http_server}/get_status"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url)
            self.logger.info(f"状态: {r.json()}")

    """
    消息发送
    """
    async def send_to_server(self, event: EventBase, message: Union[MessageChain, dict]):
        """
        发送消息，可以接受 MessageChain 或原始字典格式的消息。
        """
        try:
            if event.message_type == "group":
                data = {
                    "group_id": event.group_id,
                    "message": message.to_dict(),
                }
                url = f"{self.http_server}/send_group_msg"
            elif event.message_type == "private":
                data = {
                    "user_id": event.user_id,
                    "message": message.to_dict(),
                }
                url = f"{self.http_server}/send_private_msg"

            self.logger.info(f"发送消息: {data}")
            async with httpx.AsyncClient(timeout=200) as client:
                r = await client.post(url, json=data)  # 使用 `json=data` 代替 `data=data`
                #print(r.json())
                return r.json()
        except Exception as e:
            self.logger.error(f"发送消息时出现错误: {e}", exc_info=True)

    async def send(self, event: EventBase, components: Union[str, list[Union[MessageComponent, str]]]):
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        else:
            # 将列表中的字符串转换为 Text 对象
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message_chain = MessageChain(components)
        return await self.send_to_server(event, message_chain)

    async def send_friend_message(self, user_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        else:
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message = MessageChain(components)
        self.logger.warning(message)
        self.logger.warning(message.to_dict())
        data = {
            "user_id": user_id,
            "message": message.to_dict(),
        }
        self.logger.info(f"发送消息: {data}")
        url = f"{self.http_server}/send_private_msg"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()
            #print(r.json())
    async def send_group_message(self, group_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        else:
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message = MessageChain(components)
        data = {
            "group_id": group_id,
            "message": message.to_dict(),
        }
        self.logger.info(f"发送消息: {data}")
        url = f"{self.http_server}/send_group_msg"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()
            #print(r.json())
    """
    撤回、禁言等群管类
    """
    async def recall(self, message_id: int):
        url=f"{self.http_server}/delete_msg"
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.post(url, json={"message_id": message_id})  # 使用 `json=data`
            return r.json()
    """
    属性之类的玩意
    """

