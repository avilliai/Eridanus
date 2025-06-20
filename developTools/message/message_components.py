import os
from abc import ABC
from typing import (Annotated, Any, Literal, Optional,
                    TypeVar)

from pydantic import BaseModel, Field, TypeAdapter, model_serializer, field_validator

OnlyReceive = TypeVar("OnlyReceive", bound=Any)
OnlySend = TypeVar("OnlySend", bound=Any)

class MessageComponent(BaseModel, ABC):
    """消息组件

    注意：带有 Annotated[..., OnlySend] 的是仅发送组件，带有 Annotated[..., OnlyReceive] 的是仅接收组件，不要搞混！

    Attributes:
        comp_type: 消息组件类型
        ...: 参见相关的 OneBot 11 标准文档
    """

    comp_type: str = "basic"

    @model_serializer
    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        data = {}
        for k, v in self:
            if k in [ "comp_type"]:
                continue

            field_info = self.model_fields[k]
            # 检查 OnlySend 是否在元数据中
            if any(arg is OnlySend for arg in field_info.metadata):
                continue

            data[k] = TypeAdapter(type(v)).dump_python(v, mode="json")

        return {"type": self.comp_type, "data": data}

class File(MessageComponent):
    comp_type: str = "file"
    file: str = Field(description="文件路径")
    name: str= Field(default="",description="文件名")
    url: Annotated[Optional[str], OnlySend] = Field(default="",description="文件 URL")
    file_id: Annotated[Optional[str],OnlySend] = Field(default="",description="图片类型")
    path: Annotated[Optional[str], OnlySend] = Field(default="",description="文件路径")
    file_size: Annotated[Optional[str], OnlySend] = Field(default="",description="文件大小")
    def __init__(self, **data):
        super().__init__(**data)
        if self.file and not (
                self.file.startswith("file://")
                or self.file.startswith("base64://")
        ):
            # 将相对路径转换为绝对路径并添加 file:// 前缀
            abs_path = os.path.abspath(self.file).replace("\\", "/")
            self.file = f"file://{abs_path}"
        file_name = os.path.basename(self.file)
        self.name = file_name
class Text(MessageComponent):
    comp_type: str = "text"
    text: str = Field(description="纯文本")

    def __init__(self, text: str) -> None:
        super().__init__(text=text)


class Face(MessageComponent):
    comp_type: str = "face"
    id: str = Field(description="QQ 表情 ID")

    def __init__(self, id: int | str) -> None:
        super().__init__(id=str(id))


class Image(MessageComponent):
    comp_type: str = "image"
    file: str

    url: Annotated[Optional[str], OnlySend] = Field(default="",description="图片 URL")
    type: Annotated[Optional[str],OnlySend] = Field(default="",description="图片类型")
    summary: Annotated[str, OnlySend] = Field(default="",description="表情包描述")
    def __init__(self, **data):
        super().__init__(**data)
        if self.file and not (
            self.file.startswith("http://")
            or self.file.startswith("file://")
            or self.file.startswith("base64://")
            or self.file.startswith("https://")
        ):
            # 将相对路径转换为绝对路径并添加 file:// 前缀
            abs_path = os.path.abspath(self.file).replace("\\", "/")
            self.file = f"file://{abs_path}"
        if not self.url:
            self.url = self.file

class Mface(MessageComponent):
    comp_type: str = "mface"
    summary: Annotated[str, OnlySend] = Field(description="表情包描述")
    url: Annotated[str, OnlySend] = Field(description="表情包 URL")
    emoji_id : Annotated[str, OnlySend] = Field(description="表情包 ID")
    emoji_package_id: Annotated[int|str, OnlySend] = Field(description="表情包包 ID")
    key: Annotated[str, OnlySend] = Field(description="表情包 Key")

class Record(MessageComponent):
    comp_type: str = "record"
    file: str = Field(description="语音文件路径")
    url: Annotated[Optional[str], OnlySend] = Field(default="",description="语音 URL")

    def __init__(self, **data):
        super().__init__(**data)
        if self.file and not (
            self.file.startswith("http://")
            or self.file.startswith("file://")
            or self.file.startswith("base64://")
            or self.file.startswith("https://")
        ):
            # 将相对路径转换为绝对路径并添加 file:// 前缀
            abs_path = os.path.abspath(self.file).replace("\\", "/")
            self.file = f"file://{abs_path}"



class Video(MessageComponent):
    comp_type: str = "video"
    file: str
    url: Annotated[Optional[str], OnlySend] = Field(default="",description="视频 URL")
    def __init__(self, **data):
        super().__init__(**data)
        if self.file and not (
                self.file.startswith("http://")
                or self.file.startswith("file://")
                or self.file.startswith("base64://")
                or self.file.startswith("https://")
        ):
            # 将相对路径转换为绝对路径并添加 file:// 前缀
            abs_path = os.path.abspath(self.file).replace("\\", "/")
            self.file = f"file://{abs_path}"



class At(MessageComponent):
    comp_type: str = "at"
    qq: int = Field(default=0,description="@的 QQ 号，all 表示全体成员")
    name: Annotated[Optional[str], OnlySend] = Field(default="",description="昵称")

    @field_validator("qq", mode="before")
    def convert_all_to_zero(cls, value):
        return 0 if value == "all" else value


class Rps(MessageComponent):
    comp_type: str = "rps"


class Dice(MessageComponent):
    comp_type: str = "dice"


class Shake(MessageComponent):
    comp_type: str = "shake"


class Poke(MessageComponent):
    comp_type: str = "poke"
    type: int = Field(description="类型")
    id: int = Field(description="ID")
    name: Annotated[Optional[str], OnlyReceive] = Field(description="表情名")


class Anonymous(MessageComponent):
    comp_type: str = "anonymous"
    ignore: Annotated[Optional[bool], OnlySend] = Field(
        default=None, description="可选，表示无法匿名时是否继续发送"
    )


class Share(MessageComponent):
    comp_type: str = "share"
    url: str = Field(default="", description="URL")
    title: str = Field(default="",description="标题")
    content: Optional[str] = Field(description="发送时可选，内容描述")
    image: Optional[str] = Field(description="发送时可选，图片 URL")


class Contact(MessageComponent):
    comp_type: str = "contact"
    type: Literal["qq", "group"] = Field(description="推荐类型")
    id: str = Field(description="被推荐人的 QQ 号或群号")


class Location(MessageComponent):
    comp_type: str = "location"
    lat: str = Field(description="纬度")
    lon: str = Field(description="经度")
    title: Optional[str] = Field(description="发送时可选，标题")
    content: Optional[str] = Field(description="发送时可选，内容描述")


class Music(MessageComponent):
    comp_type: str = "music"
    type: str
    id: int
class Card(MessageComponent):
    comp_type: str = "music"
    type: str="custom"
    url: str="https://music.qq.com"
    audio: str = Field(description="音频url")
    title: str= Field(description="音乐标题")
    image: str= Field(description="音乐封面url")

class Reply(MessageComponent):
    comp_type: str = "reply"
    id: int = Field(description="回复时引用的消息 ID")

class Markdown(MessageComponent):
    comp_type: str = "markdown"
    content: str = Field(default="",description="Markdown 内容")

class Forward(MessageComponent):
    comp_type: str = "forward"
    id: Annotated[str, OnlyReceive] = Field(description="合并转发 ID")

    def __init__(self, id: str) -> None:
        super().__init__(id=id)


class Node(MessageComponent):
    comp_type: str = "node"
    user_id: str = Field(default="",description="发送者 QQ 号")
    nickname: str = Field(default="",description="发送者昵称")
    content: str | list[MessageComponent] = Field(description="消息内容")


class Xml(MessageComponent):
    comp_type: str = "xml"
    data: str = Field(description="XML 内容")

    def __init__(self, data: str) -> None:
        super().__init__(data=data)


class Json(MessageComponent):
    comp_type: str = "json"
    data: str = Field(description="JSON 内容")

    def __init__(self, data: str) -> None:
        super().__init__(data=data)

class Contact_user(MessageComponent):
    comp_type: str = "contact"
    tpye: str = "qq"
    id: str = Field(description="被推荐人的 QQ 号")
class Contact_group(MessageComponent):
    comp_type: str = "contact"
    tpye: str = "group"
    id: str = Field(description="被推荐人的群号")
# Attention!
# All the code above the comment are generated by AI according OneBot 11 Standrad.
# The developer does not approve these code are all right.
# Please check them before you use them.


__all__ = [
    "Text",
    "Face",
    "Image",
    "Record",
    "Video",
    "At",
    "Rps",
    "Dice",
    "Shake",
    "Poke",
    "Anonymous",
    "Share",
    "Contact",
    "Location",
    "Music",
    "Reply",
    "Forward",
    "Node",
    "Xml",
    "Json",
    "Contact_user",
    "Contact_group",
]