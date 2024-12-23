from typing import Any, Dict, Optional, Type

from EridanusTools.event.base import EventBase
from EridanusTools.event.events import GroupUploadNoticeEvent, GroupMessageEvent, PrivateMessageEvent, \
    GroupAdminNoticeEvent, GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, GroupBanNoticeEvent, \
    FriendAddNoticeEvent, GroupRecallNoticeEvent, FriendRecallNoticeEvent, NotifyEvent, FriendRequestEvent, \
    GroupRequestEvent, LifecycleMetaEvent, HeartbeatMetaEvent


class EventFactory:
    """动态生成事件对象的工厂"""

    # 映射事件类型到类
    event_mapping: Dict[str, Type[EventBase]] = {
        "message": {
            "private": PrivateMessageEvent,
            "group": GroupMessageEvent,
        },
        "notice": {
            "group_upload": GroupUploadNoticeEvent,
            "group_admin": GroupAdminNoticeEvent,
            "group_decrease": GroupDecreaseNoticeEvent,
            "group_increase": GroupIncreaseNoticeEvent,
            "group_ban": GroupBanNoticeEvent,
            "friend_add": FriendAddNoticeEvent,
            "group_recall": GroupRecallNoticeEvent,
            "friend_recall": FriendRecallNoticeEvent,
            "notify": NotifyEvent,
        },
        "request": {
            "friend": FriendRequestEvent,
            "group": GroupRequestEvent,
        },
        "meta_event": {
            "lifecycle": LifecycleMetaEvent,
            "heartbeat": HeartbeatMetaEvent,
        },
    }

    @staticmethod
    def create_event(data: Dict[str, Any]) -> Optional[EventBase]:
        """根据 JSON 数据创建事件实例"""
        post_type = data.get("post_type")
        if not post_type:
            return None

        # 根据事件类型找到子类型
        sub_mapping = EventFactory.event_mapping.get(post_type)
        if not sub_mapping:
            return None

        # 进一步匹配子类型
        sub_type = data.get("message_type") or data.get("notice_type") or data.get("request_type") or data.get("meta_event_type")
        event_class = sub_mapping.get(sub_type)
        if not event_class:
            return None

        # 动态实例化事件对象
        return event_class(**data)
