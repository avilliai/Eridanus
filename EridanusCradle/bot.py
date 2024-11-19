from typing import Callable, List, Dict, Type, Any

from EridanusCradle.events import MessageEvent,GroupMessage, FriendMessage


class Bot:
    def __init__(self):
        self.listeners: Dict[Type[MessageEvent], List[Callable[[MessageEvent], None]]] = {}
        self.event_mapping: Dict[str, Type[MessageEvent]] = {
            'group': GroupMessage,
            'private': FriendMessage,
            # 可以在这里添加其他消息事件类型的映射
        }

    def on(self, event_type: Type[MessageEvent]) -> Callable[[Callable[[MessageEvent], None]], Callable[[MessageEvent], None]]:
        def decorator(func: Callable[[MessageEvent], None]) -> Callable[[MessageEvent], None]:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(func)
            return func
        return decorator

    async def dispatch_event(self, event: MessageEvent):
        for listener in self.listeners.get(type(event), []):
            await listener(event)

    async def handle_event(self, data: Dict[str, Any]):
        message_type = data.get('message_type')
        event_class = self.event_mapping.get(message_type)

        if event_class:
            event = event_class(**data)  # 使用解包将 data 传递给事件类
            await self.dispatch_event(event)  # 分发事件
        else:
            print(f"未知的消息类型: {message_type}")

    async def send(self, content: str, user_id: int):
        # 在这里实现发送消息的逻辑
        print(f"发送消息给用户 {user_id}: {content}")
        return