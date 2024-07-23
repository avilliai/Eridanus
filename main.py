from yiriob.adapters import ReverseWebsocketAdapter
from yiriob.bot import Bot
from yiriob.event import EventBus
from yiriob.event.events import GroupMessageEvent

bus = EventBus()
bot = Bot(
    adapter=ReverseWebsocketAdapter(
        host="ws://127.0.0.1", port=3003, access_token="fasfsdf", bus=bus
    ),
    self_id=919467430,
)
