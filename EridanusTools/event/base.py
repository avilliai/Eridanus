from abc import ABC
from typing import (Any, Literal, Optional, Type, Unpack, final, get_args,
                    get_origin)

from pydantic import BaseModel, ConfigDict, Field




class EventBase(BaseModel, ABC):
    """事件类

    Attributes:
        time: 事件发生时间
        self_id: 收到事件的机器人 id
        post_type: 事件类型
    """

    @final
    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]):
        if cls.model_fields["auto_register"].default is True and cls.__name__ not in [
            "EventBase",
            "MessageEvent",
            "NoticeEvent",
            "RequestEvent",
            "MetaEvent",
        ]:
            events_list.append(cls)

        return super().__init_subclass__(**kwargs)

    time: int
    self_id: int
    post_type: Literal["message", "notice", "request", "meta_event"] | str
    auto_register: bool = Field(
        default=True,
        description="是否自动注册到 event_list 中，如果你的类是一个基类，则不要开启该选项。",
    )
    model_config = ConfigDict(extra="allow")


def get_key_from_event(event: Type[EventBase]) -> str:
    post_key: Literal["message", "notice", "request", "meta_event"] = get_args(
        event.model_fields["post_type"].annotation
    )[0]

    sub_key: Optional[str] = get_args(
        event.model_fields[f"{post_key}_type"].annotation
    )[0]

    key = f"{post_key}:{sub_key}"
    # logger.debug(f"from event: {event} -> {key}")

    return key


def get_key_from_dict(data: dict[str, Any]) -> str:
    post_key = data.get("post_type", None)
    sub_key = data.get(f"{post_key}_type", None)

    key = f"{post_key}:{sub_key}"
    # logger.debug(f"from dict: {data} -> {key}")
    return key


events_list: list[Type[EventBase]] = []

__all__ = ["EventBase"]