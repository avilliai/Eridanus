from typing import Any, Dict, List, Type, Union
from developTools.message.message_components import (
    MessageComponent, Text, Face, Image, Record, Video, At, Rps, Dice,
    Shake, Poke, Anonymous, Share, Contact, Location, Music, Reply,
    Forward, Node, Xml, Json, Contact_user, Contact_group, Mface
)

class MessageChain(list):
    """消息链，自动解析字典为对应的消息组件对象"""

    # 手动映射 type 到类
    _type_map: Dict[str, Type[MessageComponent]] = {
        "text": Text,
        "face": Face,
        "image": Image,
        "record": Record,
        "video": Video,
        "at": At,
        "rps": Rps,
        "dice": Dice,
        "shake": Shake,
        "poke": Poke,
        "anonymous": Anonymous,
        "share": Share,
        "contact": Contact,
        "location": Location,
        "music": Music,
        "reply": Reply,
        "forward": Forward,
        "node": Node,
        "xml": Xml,
        "json": Json,
        "contact_user": Contact_user,
        "contact_group": Contact_group,
        "mface": Mface,
    }

    def __init__(self, messages: List[Union[MessageComponent, Dict[str, Any], str]]):
        """
        初始化消息链，支持：
        - 直接传入 MessageComponent 对象列表（不会再解析）
        - 传入字典（需解析）
        - 传入字符串（自动转为 Text）
        """
        # 如果所有元素都是 MessageComponent，直接使用
        if self._is_all_components(messages):
            super().__init__(messages)
        else:
            #print(f"原始数据: {messages}")
            super().__init__(self._parse_messages(messages))

    def _is_all_components(self, messages: List[Any]) -> bool:
        """判断是否所有元素都是 MessageComponent"""
        return all(isinstance(item, MessageComponent) for item in messages)

    @classmethod
    def _parse_messages(cls, messages: List[Union[MessageComponent, Dict[str, Any], str]]) -> List[MessageComponent]:
        """解析传入的消息列表"""
        parsed_messages = []

        for msg in messages:
            if isinstance(msg, MessageComponent):
                # 直接是组件，直接添加
                parsed_messages.append(msg)
            elif isinstance(msg, str):
                # 字符串 -> 转换成 Text 组件
                parsed_messages.append(Text(msg))
            elif isinstance(msg, dict):
                # 字典 -> 解析成对应的组件
                msg_type = msg.get("type")
                msg_data = msg.get("data", {})

                component_class = cls._type_map.get(msg_type)
                if component_class:
                    #print(f"解析消息: {msg_type}, 原始数据: {msg_data}")
                    #print(str(msg_data))
                    parsed_messages.append(component_class(**msg_data))
                else:
                    print(f"未知消息类型: {msg_type}, 原始数据: {msg}")  # 记录未识别的消息
                    parsed_messages.append(Text(str(msg)))
            else:
                raise TypeError(f"无效的消息格式: {msg}")

        return parsed_messages
    def to_dict(self) -> list[dict[str, Any]]:
        return [x.to_dict() for x in self]

    def has(self, component_type: Type[MessageComponent]) -> bool:
        """检查消息链中是否包含指定类型的消息组件"""
        return any(isinstance(component, component_type) for component in self)

    def __contains__(self, obj: Any) -> bool:
        return self.has(obj)

    def get(self, component_type: Type[MessageComponent]) -> List[MessageComponent]:
        """
        获取所有指定类型的消息组件。

        :param component_type: 要筛选的消息组件类型，例如 `Text`, `Image` 等。
        :return: 所有匹配的组件列表。
        """
        return [component for component in self if isinstance(component, component_type)]
    def fetch_text(self) -> str:
        if self.has(Text) and not self.has(At):
            return self.get(Text)[0].text.strip()
        else:
            return ""