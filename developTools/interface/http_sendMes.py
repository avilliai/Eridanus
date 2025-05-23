from typing import Union

import httpx
import requests

from developTools.event.base import EventBase
from developTools.message.message_chain import MessageChain
from developTools.message.message_components import MessageComponent, Text, Reply, Node
from developTools.utils.logger import get_logger


class http_mailman:
    def __init__(self, http_server, access_token=""):
        self.http_server = http_server
        self.logger = get_logger()
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }
        try:
            self.info = self.get_login_info()
        except:
            self.info = None

    async def get_status(self):
        """
        获取服务状态
        :return:
        """
        url = f"{self.http_server}/get_status"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url)
            self.logger.info(f"状态: {r.json()}")

    """
    消息发送
    """

    async def send_group_forward_msg(self, group_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        """
        发送群消息
        :param group_id:
        :param components:
        :return:
        """
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
        else:
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message = MessageChain(components)
        data = {
            "group_id": group_id,
            "messages": message.to_dict(),
        }
        self.logger.info(f"发送消息: {data}")
        url = f"{self.http_server}/send_group_forward_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()

    async def send_private_forward_msg(self, user_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        """
        发送私聊合并转发消息
        :param user_id:
        :param components:
        :return:
        """
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
        else:
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message = MessageChain(components)
        data = {
            "user_id": user_id,
            "messages": message.to_dict(),
        }
        self.logger.info(f"发送消息: {data}")
        url = f"{self.http_server}/send_private_forward_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()

    async def send_to_server(self, event: EventBase, message: Union[MessageChain, dict]):
        """
        发送消息，可以接受 MessageChain 或原始字典格式的消息。
        """
        try:

            if hasattr(event, "group_id"):
                data = {
                    "group_id": event.group_id,
                    "message": message.to_dict(),
                }
                if isinstance(message[0], Node):
                    r = await self.send_group_forward_msg(event.group_id, message)
                    return r
                else:
                    url = f"{self.http_server}/send_group_msg"
            else:
                data = {
                    "user_id": event.user_id,
                    "message": message.to_dict(),
                }
                if isinstance(message[0], Node):
                    r = await self.send_private_forward_msg(event.user_id, message)
                    return r
                else:
                    url = f"{self.http_server}/send_private_msg"
            self.logger.info(f"发送消息: {data}")
            async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
                r = await client.post(url, json=data)  # 使用 `json=data` 代替 `data=data`
                #print(r.json())
                return r.json()
        except Exception as e:
            self.logger.error(f"发送消息时出现错误: {e}", exc_info=True)

    async def send(self, event: EventBase, components: Union[str, list[Union[MessageComponent, str]]],
                   Quote: bool = False):
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
        if Quote:
            components.append(Reply(id=event.message_id))  #消息引用
        else:
            # 将列表中的字符串转换为 Text 对象
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message_chain = MessageChain(components)
        return await self.send_to_server(event, message_chain)

    async def send_friend_message(self, user_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        """
        发送好友消息
        :param user_id:
        :param components:
        :return:
        """
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
        else:
            components = [
                Text(component) if isinstance(component, str) else component
                for component in components
            ]

        message = MessageChain(components)
        #self.logger.warning(message)
        #self.logger.warning(message.to_dict())
        data = {
            "user_id": user_id,
            "message": message.to_dict(),
        }
        self.logger.info(f"发送消息: {data}")
        url = f"{self.http_server}/send_private_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()
            #print(r.json())

    async def send_group_message(self, group_id: int, components: Union[str, list[Union[MessageComponent, str]]]):
        """
        发送群消息
        :param group_id:
        :param components:
        :return:
        """
        # 如果是字符串，将其包装为 [Text(str)]
        if isinstance(components, str):
            components = [Text(components)]
        if not isinstance(components, list):
            components = [components]
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
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json=data)  # 使用 `json=data`
            return r.json()
            #print(r.json())

    """
    撤回、禁言等群管类
    """

    async def recall(self, message_id: int):
        """
        撤回消息
        :param message_id:
        :return:
        """
        url = f"{self.http_server}/delete_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"message_id": message_id})  # 使用 `json=data`
            return r.json()

    async def send_like(self, user_id):
        """
        发送点赞
        :param user_id:
        :return:
        """
        url = f"{self.http_server}/send_like"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id, "times": 10})  # 使用 `json=data`
            return r.json()

    """
    私聊相关
    """

    async def get_friend_list(self):
        """
        获取好友列表
        :return:
        """
        url = f"{self.http_server}/get_friend_list"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, data={"no_cache": False})  # 使用 `json=data`
            return r.json()

    async def delete_friend(self, user_id):
        """
        删除好友
        :param user_id:
        :return:
        """
        #删好友
        url = f"{self.http_server}/delete_friend"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id})  # 使用 `json=data`
            return r.json()

    async def handle_friend_request(self, flag: str, approve: bool, remark: str):
        """
        处理好友请求
        :param flag:
        :param approve:
        :param remark:
        :return:
        """
        url = f"{self.http_server}/set_friend_add_request"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"flag": flag, "approve": approve, "remark": remark})  # 使用 `json=data`
            return r.json()

    async def set_friend_remark(self, user_id: int, remark: str):
        """
        设置好友备注
        :param user_id:
        :param remark:
        :return:
        """
        url = f"{self.http_server}/set_friend_remark"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id, "remark": remark})  # 使用 `json=data`
            return r.json()

    async def set_friend_category(self, user_id: int, category_id: int):
        """
        设置好友分组
        :param user_id:
        :param category_id:
        :return:
        """
        url = f"{self.http_server}/set_friend_category"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id, "category_id": category_id})  # 使用 `json=data`
            return r.json()

    async def get_stranger_info(self, user_id: int):
        """
        获取陌生人信息
        :param user_id:
        :return:
        """
        url = f"{self.http_server}/get_stranger_info"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id})  # 使用 `json=data`
            return r.json()

    async def set_qq_avatar(self, file: str):
        """
        设置QQ头像
        :param file:
        :return:
        """
        url = f"{self.http_server}/set_qq_avatar"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"file": file})  # 使用 `json=data`
            return r.json()

    async def friend_poke(self, user_id: int):
        url = f"{self.http_server}/friend_poke"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id})  # 使用 `json=data`
            return r.json()

    async def upload_private_file(self, user_id: int, file: str, name: str):
        """
        上传私聊文件
        :param user_id:
        :param file:
               "file": "https://www.yujn.cn/api/heisis.php",
                // 本地文件
                // "file": "file://d:\\1.mp4"

                // base64文件
                // "file": "base64://xxxxxxxxxxxxx"
        :param name:
        :return:
        """
        url = f"{self.http_server}/upload_private_file"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"user_id": user_id, "file": file, "name": name})  # 使用 `json=data`
            return r.json()

    """
    群聊相关
    """

    async def get_group_list(self):
        """
        获取群列表
        :return:
        """
        url = f"{self.http_server}/get_group_list"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"no_cache": False})  # 使用 `json=data`
            return r.json()

    async def get_group_info(self, group_id: int):
        """
        获取群信息
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_group_info"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def get_group_member_list(self, group_id: int):
        """
        获取群成员列表
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_group_member_list"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "no_cache": True})  # 使用 `json=data`
            return r.json()

    async def get_group_member_info(self, group_id: int, user_id: int):
        """
        获取群成员信息
        :param group_id:
        :param user_id:
        :return:
        """
        url = f"{self.http_server}/get_group_member_info"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id})  # 使用 `json=data`
            return r.json()

    async def group_poke(self, group_id: int, user_id: int):
        """
        群戳一戳
        :param group_id:
        :param user_id:
        :return:
        """
        url = f"{self.http_server}/group_poke"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id})  # 使用 `json=data`
            return r.json()

    async def set_group_add_request(self, flag: str, approve: bool, reason: str):
        """
        处理加群请求
        :param flag: 请求id
        :param approve:
        :param reason:
        :return:
        """
        url = f"{self.http_server}/set_group_add_request"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"flag": flag, "approve": approve, "reason": reason})  # 使用 `json=data`
            return r.json()

    async def quit(self, group_id: int):
        """
        退出群聊
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/set_group_leave"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def set_group_admin(self, group_id: int, user_id: int, enable: bool):
        """
        设置群管理员
        :param group_id:
        :param user_id:
        :param enable: 设置/取消
        :return:
        """
        url = f"{self.http_server}/set_group_admin"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url,
                                  json={"group_id": group_id, "user_id": user_id, "enable": enable})  # 使用 `json=data`
            return r.json()

    async def set_group_card(self, group_id: int, user_id: int, card: str):
        """
        设置群名片
        :param group_id:
        :param user_id:
        :param card:
        :return:
        """
        url = f"{self.http_server}/set_group_card"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id, "card": card})  # 使用 `json=data`
            return r.json()

    async def mute(self, group_id: int, user_id: int, duration: int):
        """
        禁言群成员
        :param group_id:
        :param user_id:
        :param duration: 秒，0为解除禁言
        :return:
        """
        url = f"{self.http_server}/set_group_ban"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id,
                                             "duration": duration})  # 使用 `json=data`
            return r.json()

    async def set_group_whole_ban(self, group_id: int, enable: bool):
        """
        设置全员禁言
        :param group_id:
        :param enable:
        :return:
        """
        url = f"{self.http_server}/set_group_whole_ban"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "enable": enable})  # 使用 `json=data`
            return r.json()

    async def set_group_name(self, group_id: int, group_name: str):
        """
        设置群名称
        :param group_id:
        :param group_name:
        :return:
        """
        url = f"{self.http_server}/set_group_name"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "group_name": group_name})  # 使用 `json=data`
            return r.json()

    async def set_group_special_title(self, group_id: int, user_id: int, special_title: str):
        """
        设置群头衔
        :param group_id:
        :param user_id:
        :param special_title:
        :return:
        """
        url = f"{self.http_server}/set_group_special_title"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id,
                                             "special_title": special_title})  # 使用 `json=data`
            return r.json()

    async def set_group_kick(self, group_id: int, user_id: int, reject_add_request: bool = True):
        """
        踢出群成员
        :param group_id:
        :param user_id:
        :param reject_add_request:
        :return:
        """
        url = f"{self.http_server}/set_group_kick"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "user_id": user_id,
                                             "reject_add_request": reject_add_request})  # 使用 `json=data`
            return r.json()

    async def get_group_honor_info(self, group_id: int):
        """
        获取群荣誉信息. 壁画王。
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_group_honor_info"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def get_essence_msg_list(self, group_id: int):
        """
        获取精华消息列表
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_essence_msg_list"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def set_essence_msg(self, message_id: int):
        """
        设置精华消息
        :param message_id:
        :return:
        """
        url = f"{self.http_server}/set_essence_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"message_id": message_id})  # 使用 `json=data`
            return r.json()

    async def delete_essence_msg(self, message_id: int):
        """
        删除精华消息
        :param message_id:
        :return:
        """
        url = f"{self.http_server}/delete_essence_msg"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"message_id": message_id})  # 使用 `json=data`
            return r.json()

    async def get_group_root_files(self, group_id: int):
        """
        获取群根目录文件列表，暂时看不出来有啥用
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_group_root_files"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def upload_group_file(self, group_id: int, file: str, name: str):
        """
        上传群文件。传好东西
        :param group_id:
        :param file:
        :param name:
        :return:
        """
        url = f"{self.http_server}/upload_group_file"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "file": file, "name": name})  # 使用 `json=data`
            return r.json()

    async def delete_group_file(self, group_id: int, file_id: str):
        """
        删除群文件。那个id是上传的时候给的
        :param group_id:
        :param file_id:
        :return:
        """
        url = f"{self.http_server}/delete_group_file"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "file_id": file_id})  # 使用 `json=data`
            return r.json()

    async def create_group_file_folder(self, group_id: int, name: str):
        """
        创建群文件夹
        :param group_id:
        :param name:
        :return:
        """
        url = f"{self.http_server}/create_group_file_folder"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "name": name})  # 使用 `json=data`
            return r.json()

    async def delete_group_folder(self, group_id: int, folder_id: str):
        """
        删除群文件夹
        :param group_id:
        :param folder_id:
        :return:
        """
        url = f"{self.http_server}/delete_group_folder"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id, "folder_id": folder_id})  # 使用 `json=data`
            return r.json()

    async def get_group_file_url(self, file_id: str):
        """
        获取群文件下载链接,估计不大好用
        :param file_id:
        :return:
        """
        url = f"{self.http_server}/get_group_file_url"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"file_id": file_id})  # 使用 `json=data`
            return r.json()

    async def _send_group_notice(self, group_id: int, content: str, image: str):
        """
        发送群公告
        :param group_id:
        :param content:
        :param image:  支持http://, file://, base64://
        :return:
        """
        url = f"{self.http_server}/_send_group_notice"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url,
                                  json={"group_id": group_id, "content": content, "image": image})  # 使用 `json=data`
            return r.json()

    async def _get_group_notice(self, group_id: int):
        """
        获取群公告
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/_get_group_notice"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def get_group_ignore_add_request(self, group_id: int):
        """
        获取群组忽略的加群请求
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/get_group_ignore_add_request"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    async def send_group_sign(self, group_id: int):
        """
        发送群签到
        :param group_id:
        :return:
        """
        url = f"{self.http_server}/send_group_sign"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"group_id": group_id})  # 使用 `json=data`
            return r.json()

    def get_login_info(self):
        """
        获取登录号信息
        :return:
        """
        url = f"{self.http_server}/get_login_info"
        r = requests.get(url, headers=self.headers)
        self.id = int(r.json()["data"]["user_id"])
        self.nickname = r.json()["data"]["nickname"]

    async def get_record(self, file: str, out_format="mp3"):
        url = f"{self.http_server}/get_record"
        async with httpx.AsyncClient(headers=self.headers, timeout=200) as client:
            r = await client.post(url, json={"file": file, "out_format": out_format})  # 使用 `json=data`
            return r.json()

    async def get_video(self, url: str, path: str):
        async with httpx.AsyncClient(timeout=200) as client:
            r = await client.get(url)
            with open(path, "wb") as f:
                f.write(r.content)
            return path
