from EridanusTools.event.events import GroupMessageEvent, FriendRequestEvent


def main(bot):
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