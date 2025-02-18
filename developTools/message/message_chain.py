from typing import Any, Iterable

from developTools.message.message_components import Text


class MessageChain(list):
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

    def __init__(self, iterable: Iterable[Any], /) -> None:
        super().__init__()
        self.extend([Text(x) if isinstance(x, str) else x for x in iterable])

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source_type: Any, handler
    ) -> Any:
        return handler(list)

    def to_dict(self) -> list[dict[str, Any]]:
        return [x.to_dict() for x in self]

    def has(self, obj: Any) -> bool:
        if isinstance(obj, str):
            return any(isinstance(x, Text) and x.text == obj for x in self)
        return obj in self

    def __contains__(self, obj: Any) -> bool:
        return self.has(obj)


__all__ = ["MessageChain"]
