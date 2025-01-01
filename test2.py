from developTools.event.events import PrivateMessageEvent, GroupMessageEvent
from developTools.adapters.websocket_adapter import WebSocketBot

uri = "ws://127.0.0.1:3001"

bot = WebSocketBot(uri)


@bot.on(PrivateMessageEvent)
async def handle_private_message(event: PrivateMessageEvent):
    #print(f"收到私聊消息: {event.raw_message} 来自用户: {event.sender.nickname}")

    await bot.send_friend_message(event.sender.user_id, "你好，我测你的码")


@bot.on(GroupMessageEvent)
async def handle_group_message(event: GroupMessageEvent):
    #print(event)
    #print(f"收到群组消息: {event.raw_message}，来自群: {event.group_id}")
    #await bot.send_friend_message(1840094972, "你好，我是机器人")
    await bot.send(event,"我测你的码")
    r=await bot.groupList() #还需要进一步修改，需要使用echo参数作为特定请求的返回值标识，目前还没有做
    print("群列表")
    print(r)
    #print(r)
bot.run()
