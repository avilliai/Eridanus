from developTools.event.events import GroupMessageEvent, FriendRequestEvent, PrivateMessageEvent, startUpMetaEvent
from developTools.message.message_components import Record, Node, Text


def main(bot,config):
    global avatar
    avatar=False
    @bot.on(GroupMessageEvent)
    async def sendLike(event: GroupMessageEvent):
        if event.raw_message=="赞我":
            await bot.send_like(event.user_id)
            await bot.send(event, "已赞你！")
        if event.raw_message.startswith("叫我"):
            await bot.send(event, "已修改")
            remark = event.raw_message.split("叫我")[1].strip()
            await bot.set_friend_remark(event.user_id, remark)

    @bot.on(FriendRequestEvent)
    async def FriendRequestHandler(event: FriendRequestEvent):
        print(event)

    @bot.on(GroupMessageEvent)
    async def changeAvatar(event: GroupMessageEvent):
        global avatar
        #bot.logger.error(event.processed_message)
        #bot.logger.error(event.get("image"))
        if event.raw_message=="换头像" and event.sender.user_id==1840094972:
            await bot.send(event,"发来！")
            avatar=True
        if event.get("image") and avatar and event.sender.user_id==1840094972:
            bot.logger.error(event.get("image")[0]["url"])
            r=await bot.set_qq_avatar(event.get("image")[0]["url"])
            bot.logger.error(r)
            await bot.send(event,"已更换头像！")
            avatar=False
        if event.raw_message=="给我管理" and event.sender.user_id==1840094972:
            await bot.set_group_admin(event.group_id,event.sender.user_id,True)
            await bot.send(event, "给你了！")
        if event.raw_message=="取消管理" and event.sender.user_id==1840094972:
            await bot.set_group_admin(event.group_id,event.sender.user_id,False)
            await bot.send(event, "取消了！")
        if event.raw_message.startswith("我要头衔"):
            title=event.raw_message.split("我要头衔")[1].strip()
            await bot.set_group_special_title(event.group_id,event.sender.user_id,title)
            await bot.send(event, "已设置头衔！")
        if event.raw_message=="禁言我":
            await bot.mute(event.group_id,event.sender.user_id,60)
        if event.raw_message=="测试":
            r=Node(content=[Text("你好，我是机器人！")])
            await bot.send_group_forward_msg(event.group_id,r)
            await bot.send(event,Record(file="file://D:/python/Manyana/data/autoReply/voiceReply/a1axataxaWaQaia.wav"))
    @bot.on(PrivateMessageEvent)
    async def FriendMesHandler(event: PrivateMessageEvent):
        if event.raw_message=="戳我":
            await bot.friend_poke(event.sender.user_id)
    @bot.on(startUpMetaEvent)
    async def startUpHandler(event: startUpMetaEvent):
        bot.logger.error("启动成功！")
        #print(bot.id)