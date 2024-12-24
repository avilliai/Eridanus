import json
from asyncio import sleep

from EridanusTools.event.events import GroupMessageEvent, PrivateMessageEvent, GroupRecallNoticeEvent
from EridanusTools.message.message_components import Image
from EridanusTools.AdapterAndBot import HTTPBot
from run import apiImplements

bot = HTTPBot(http_sever="http://127.0.0.1:3000",access_token="any_access_token")


@bot.on(PrivateMessageEvent)
async def handle_private_message(event: PrivateMessageEvent):
    print(f"收到私聊消息: {event.raw_message} 来自用户: {event.sender.nickname}")

    #await bot.send_friend_message(event.sender.user_id, "你好，我测你的码")


@bot.on(GroupMessageEvent)
async def handle_group_message(event: GroupMessageEvent):
    #print(event)
    print(f"收到群组消息: {event.processed_message}，来自群: {event.group_id}")
    #await bot.send_friend_message(1840094972, "你好，我是机器人")
    #r=await bot.send(event,["我测你的码",Image(file="file://D:\python\Eridanus\data\pictures\ccc.png")])
    #r=await bot.get_friend_list()
    #print(r)
    #await bot.recall(r["data"]["message_id"])
    #r=await bot.groupList() #还需要进一步修改，需要使用echo参数作为特定请求的返回值标识，目前还没有做
    #r=await bot.query_echo(r)
    #print(r)

    #print(r)
@bot.on(GroupRecallNoticeEvent)
async def handle_group_recall_notice(event: GroupRecallNoticeEvent):
    print(f"群组消息撤回: {event.message_id}，来自群: {event.group_id}")
    await bot.send_group_message(event.group_id, "撤回牛魔")
apiImplements.main(bot)

bot.run(host="0.0.0.0", port= 8080)

