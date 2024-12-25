from typing import Annotated, Any, Iterable

from pydantic import GetCoreSchemaHandler, WrapSerializer
from pydantic_core import CoreSchema, core_schema

from .message_components import MessageComponent, Text


class MessageChain(list[MessageComponent]):
    """消息链。

    构造消息链的方法：

    ```python
    chain = MessageChain([
        Text("hello"),
        Image(...)
    ])
    ```

    你也可以把 Text 省略，下面这种方法和上面是等价的：

    ```python
    chain = MessageChain([
        "hello",
        Image(...)
    ])
    ```

    你可以传入任何一个**可迭代**的对象，比如传入一个生成器：

    ```python
    def generator():
        # ...
        yield ...
        # ...

    chain = MessageChain(generator)
    ```

    ```python
    chain = MessageChain((x for x in ... if ...))  # 这是 Python 的生成器推导式写法
    ```

    使用 to_cqcode 方法将其转换为 CQ 码（一种用字符串表示消息链的方式）：

    ```python
    chain = MessageChain([Text("hello"), Text("world"), Face(id=1)])
    chain.to_cqcode()

    # > "Helloworld[CQ:face,id=1]"
    ```

    如果需要自定义消息组件（OneBot 里叫 MessageSegment，这里沿用 Mirai 的称呼），需要继承 `yiriob.message.message_components.MessageComponent`，然后指定 `comp_type` 类型：

    ```python
    class CustomComponent(MessageComponent):
        comp_type: str = "..."
        # ...
    ```

    由于 MessageChain 继承了 list[MessageComponent], 你可以像使用 list 一样使用它，比如：

    ```python
    chain: MessageChain = ...

    for comp in chain:
        ...

    if comp in chain:
        ...

    chain.append(comp)
    chain.extend(comps)
    len(chain)
    ```
    """

    def __init__(self, iterable: Iterable[MessageComponent | str], /) -> None:
        self.extend([Text(x) if isinstance(x, str) else x for x in iterable])

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, handler(list[MessageComponent])
        )

    def to_dict(self) -> list[dict[str, Any]]:
        return [x.to_dict() for x in self]

    def to_cqcode(self) -> str:
        """转换成 CQ 码。不保证完全正确，谨慎使用。如有问题，请提 Issue。

        Returns:
            CQ 码
        """
        return "".join([x.to_cqcode() for x in self])

    def has(self, obj: MessageComponent | str | object) -> bool:
        if isinstance(obj, str):
            return obj in self.to_cqcode()
        return obj in self

    def __contains__(self, obj: MessageComponent | str | object) -> bool:
        return self.has(obj)


__all__ = ["MessageChain"]