import random

from developTools.event.events import GroupMessageEvent, FriendRequestEvent, PrivateMessageEvent, startUpMetaEvent, \
    ProfileLikeEvent, PokeNotifyEvent
from developTools.message.message_components import Record, Node, Text
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import update_user, add_user, get_user


def main(bot,config):
    global avatar
    avatar=False
    @bot.on(GroupMessageEvent)
    async def sendLike(event: GroupMessageEvent):
        if event.raw_message=="赞我":
            await bot.send_like(event.user_id)
            await bot.send(event, "已赞你！")
        if event.raw_message.startswith("改备注"):
            await bot.send(event, "已修改")
            remark = event.raw_message.split("改备注")[1].strip()
            await bot.set_friend_remark(event.user_id, remark)

    @bot.on(FriendRequestEvent)
    async def FriendRequestHandler(event: FriendRequestEvent):
        print(event)

    @bot.on(GroupMessageEvent)
    async def changeAvatar(event: GroupMessageEvent):
        global avatar
        bot.logger.info(event.processed_message)
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
        if event.get("mface"):
            await bot.send(event,f"你的彩色小人gif在这里{event.get('mface')[0]['url']}")
        if event.raw_message=="给我管理" and event.sender.user_id==1840094972:
            await bot.set_group_admin(event.group_id,event.sender.user_id,True)
            await bot.send(event, "给你了！")
        if event.raw_message=="取消管理" and event.sender.user_id==1840094972:
            await bot.set_group_admin(event.group_id,event.sender.user_id,False)
            await bot.send(event, "取消了！")
        if event.raw_message.startswith("改群名") and event.sender.user_id==1840094972:
            name=event.raw_message.split("改群名")[1].strip()
            await bot.set_group_name(event.group_id,name)
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
        bot.logger.info("启动成功！")
        bot_name=config.basic_config["bot"]["name"]
        bot.logger.info(f"Bot ID: {bot.id}  Bot Name: {bot.nickname} | {bot_name}")
        master_id=config.basic_config["master"]["id"]
        master_name=config.basic_config["master"]["name"]
        bot.logger.info(f"Bot master ID: {master_id}  |  Bot master Name: {master_name}")
        group_list=await bot.get_group_list()
        group_list=group_list["data"]
        friend_list=await bot.get_friend_list()
        friend_list=friend_list["data"]
        bot.logger.info(f"读取群列表数量: {len(group_list)}")
        bot.logger.info(f"读取好友列表数量: {len(friend_list)}")
        #以防万一，给master添加权限
        await add_user(master_id,master_name,master_name)
        await update_user(master_id, permission=999,nickname=master_name)
        #r=await get_user(master_id)
        #print(r)
    @bot.on(ProfileLikeEvent)
    async def profileLikeHandler(event: ProfileLikeEvent):
        bot.logger.info(f"{event.operator_id} 赞了你！")
        await bot.send_friend_message(event.operator_id, "谢谢！")
    @bot.on(PokeNotifyEvent)
    async def pokeHandler(event: PokeNotifyEvent):
        if event.target_id==bot.id:
            if event.group_id:
                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                user_name = data["data"]["nickname"]
                bot_name=config.basic_config["bot"]["name"]
                user_info=await get_user(event.user_id,user_name)

                text = f"{user_info[1]}{event.raw_info[2]['txt']}{bot_name}{event.raw_info[4]['txt']}"
                bot.logger.info(text)
                #print(text)
                if config.api["llm"]["aiReplyCore"]:
                    r = await aiReplyCore([{"text": text}], event.user_id, config)
                else:
                    reply_list=config.settings['api_implements']['nudge']['replylist']
                    r=random.choice(reply_list)


                await bot.send_group_message(event.group_id, r)
            else:
                bot_name = config.basic_config["bot"]["name"]
                user_info = await get_user(event.user_id)
                text = f"{user_info[1]}{event.raw_info[2]['txt']}{bot_name}{event.raw_info[4]['txt']}"
                bot.logger.info(text)
                if config.api["llm"]["aiReplyCore"]:
                    r = await aiReplyCore([{"text": text}], event.user_id, config)
                else:
                    reply_list = config.settings['api_implements']['nudge']['replylist']
                    r = random.choice(reply_list)
                await bot.send_friend_message(event.user_id, r)
        #await bot.send_friend_message(event.user_id, "你戳我干啥？")