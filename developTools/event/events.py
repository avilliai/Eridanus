# pyright: reportIncompatibleVariableOverride=false
from typing import Literal, Optional, Dict, Union, List, Any

from pydantic import BaseModel, ConfigDict
from pydantic.v1 import validator

from developTools.event.base import EventBase
from developTools.message.message_chain import MessageChain
from developTools.utils.cq_code_handler import parse_message_with_cq_codes_to_list, parse_message_2processed_message


# Attention!
# All the code are from nonebot/adapter-onebot.
# We use and modify the code under MIT license.


class Sender(BaseModel):
    user_id: Optional[int] = None
    nickname: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    card: Optional[str] = None
    area: Optional[str] = None
    level: Optional[str] = None
    role: Optional[str] = None
    title: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class Reply(BaseModel):
    time: int
    message_type: str
    message_id: int
    real_id: int
    sender: Sender
    message: List[Dict[str, Any]]  # Change the type hint here

    model_config = ConfigDict(extra="allow")

    @validator("message", pre=True, always=True)
    def ensure_message_chain(cls, value):
        """确保 message 是 MessageChain 实例"""
        # No change needed here, as value is already a list of dicts
        return MessageChain(value)


class Anonymous(BaseModel):
    id: int
    name: str
    flag: str

    model_config = ConfigDict(extra="allow")


class File(BaseModel):
    id: str
    name: str
    size: int
    busid: int

    model_config = ConfigDict(extra="allow")


class Status(BaseModel):
    online: bool
    good: bool

    model_config = ConfigDict(extra="allow")

class LifecycleMetaEvent(BaseModel):
    time: int
    sender: int
    post_type: str
    meta_event_type: str
    sub_type: str
# Message Events
class MessageEvent(BaseModel):
    """消息事件"""

    post_type: Literal["message"]
    sub_type: str
    user_id: int
    message_type: str
    message_id: int
    message: List[Dict[str, Any]]  # Change the type hint here
    original_message: Optional[list] = None
    _raw_message: str
    font: int
    sender: Sender
    to_me: bool = False
    reply: Optional[Reply] = None

    processed_message: List[Dict[str, Union[str, Dict]]] = []

    message_chain: MessageChain=[]
    pure_text: str = ""

    model_config = ConfigDict(extra="allow",arbitrary_types_allowed=True)


    @property
    def raw_message(self):
        return self._raw_message

    @raw_message.setter
    def raw_message(self, value: str):
        self._raw_message = value
        if value == "":
            self.processed_message = parse_message_2processed_message(self.message)
        else:
            self.processed_message = parse_message_with_cq_codes_to_list(value)

    # 可选的，确保 processed_message 始终跟随 raw_message 更新
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果 raw_message 在初始化时已经赋值，确保 processed_message 被设置
        if hasattr(self, 'raw_message'):
            if self.raw_message == "":
                self.processed_message = parse_message_2processed_message(self.message)
            else:
                self.processed_message = parse_message_with_cq_codes_to_list(self.raw_message)
        self.message_chain=MessageChain(self.message)
        self.pure_text=self.message_chain.fetch_text()
    def get(self, message_type: str):
        """
        按指定类型获取 processed_message 中的消息。

        :param message_type: 要获取的消息类型，例如 'image', 'record' 等。
        :return: 包含该类型消息的列表，或者 None（如果没有该类型的消息）。
        """
        result = [msg[message_type] for msg in self.processed_message if message_type in msg]
        if result and message_type=="image" and "url" not in result[0]:
            result[0]["url"]=result[0]["file"]
        return result if result else None

class PrivateMessageEvent(MessageEvent):
    """私聊消息"""

    message_type: Literal["private"]


class GroupMessageEvent(MessageEvent):
    """群消息"""

    message_type: Literal["group"]
    group_id: int
    anonymous: Optional[Anonymous] = None


# Notice Events
class NoticeEvent(EventBase):
    """通知事件"""

    post_type: Literal["notice"]
    notice_type: str


class GroupUploadNoticeEvent(NoticeEvent):
    """群文件上传事件"""

    notice_type: Literal["group_upload"]
    user_id: int
    group_id: int
    file: File


class GroupAdminNoticeEvent(NoticeEvent):
    """群管理员变动"""

    notice_type: Literal["group_admin"]
    sub_type: str
    user_id: int
    group_id: int


class GroupDecreaseNoticeEvent(NoticeEvent):
    """群成员减少事件"""

    notice_type: Literal["group_decrease"]
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int


class GroupIncreaseNoticeEvent(NoticeEvent):
    """群成员增加事件"""

    notice_type: Literal["group_increase"]
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int


class GroupBanNoticeEvent(NoticeEvent):
    """群禁言事件"""

    notice_type: Literal["group_ban"]
    sub_type: str
    user_id: int
    group_id: int
    operator_id: int
    duration: int


class FriendAddNoticeEvent(NoticeEvent):
    """好友添加事件"""

    notice_type: Literal["friend_add"]
    user_id: int


class GroupRecallNoticeEvent(NoticeEvent):
    """群消息撤回事件"""

    notice_type: Literal["group_recall"]
    user_id: int
    group_id: int
    operator_id: int
    message_id: int


class FriendRecallNoticeEvent(NoticeEvent):
    """好友消息撤回事件"""

    notice_type: Literal["friend_recall"]
    user_id: int
    message_id: int


class NotifyEvent(NoticeEvent):
    """提醒事件"""

    notice_type: Literal["notify"]
    sub_type: str
    user_id: int=None
    group_id: int=None


class PokeNotifyEvent(NotifyEvent):
    """戳一戳提醒事件"""

    sub_type: Literal["poke"]
    target_id: int
    group_id: Optional[int] = None
    raw_info: list =None


class LuckyKingNotifyEvent(NotifyEvent):
    """群红包运气王提醒事件"""

    sub_type: Literal["lucky_king"]
    target_id: int

class ProfileLikeEvent(NotifyEvent):
    sub_type: Literal["profile_like"]
    operator_id: int
    operator_nick: str
    times: int
class HonorNotifyEvent(NotifyEvent):
    """群荣誉变更提醒事件"""

    sub_type: Literal["honor"]
    honor_type: str


# Request Events
class RequestEvent(EventBase):
    """请求事件"""

    post_type: Literal["request"]
    request_type: str


class FriendRequestEvent(RequestEvent):
    """加好友请求事件"""

    request_type: Literal["friend"]
    user_id: int
    flag: str
    comment: Optional[str] = None


class GroupRequestEvent(RequestEvent):
    """加群请求/邀请事件"""

    request_type: Literal["group"]
    sub_type: str
    group_id: int
    user_id: int
    flag: str
    comment: Optional[str] = None


# Meta Events
class MetaEvent(EventBase):
    """元事件"""

    post_type: Literal["meta_event"]
    meta_event_type: str


class LifecycleMetaEvent(MetaEvent):
    """生命周期元事件"""

    meta_event_type: Literal["lifecycle"]
    sub_type: str
class startUpMetaEvent(MetaEvent):
    meta_event_type: Literal["startUp"]


class HeartbeatMetaEvent(MetaEvent):
    """心跳元事件"""

    meta_event_type: Literal["heartbeat"]
    status: Status
    interval: int


__all__ = [
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
    "NoticeEvent",
    "GroupUploadNoticeEvent",
    "GroupAdminNoticeEvent",
    "GroupDecreaseNoticeEvent",
    "GroupIncreaseNoticeEvent",
    "GroupBanNoticeEvent",
    "FriendAddNoticeEvent",
    "GroupRecallNoticeEvent",
    "FriendRecallNoticeEvent",
    "NotifyEvent",
    "PokeNotifyEvent",
    "ProfileLikeEvent",
    "LuckyKingNotifyEvent",
    "HonorNotifyEvent",
    "RequestEvent",
    "FriendRequestEvent",
    "GroupRequestEvent",
    "MetaEvent",
    "LifecycleMetaEvent",
    "HeartbeatMetaEvent",
    "startUpMetaEvent"
]