import random

from developTools.event.events import GroupMessageEvent, FriendRequestEvent, PrivateMessageEvent, startUpMetaEvent, \
    ProfileLikeEvent, PokeNotifyEvent, GroupRequestEvent,GroupBanNoticeEvent
from developTools.message.message_components import Record, Node, Text, Image, File, Video
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import update_user, add_user, get_user


def main(bot,config):
    master=config.basic_config["master"]["id"]

    global avatar
    avatar=False

    @bot.on(GroupMessageEvent)
    async def sendLike(event: GroupMessageEvent):
        if "😅" in event.pure_text:
            await bot.mute(event.group_id,event.sender.user_id,60)
        if event.pure_text=="赞我":
            user_info = await get_user(event.user_id)

            if user_info[6] >=config.controller["api_implement"]["send_like"]:
                await bot.send_like(event.user_id)
                await bot.send(event, "已赞你！")
        if event.pure_text.startswith("改备注"):
            await bot.send(event, "已修改")
            remark = event.pure_text.split("改备注")[1].strip()
            await bot.set_friend_remark(event.user_id, remark)
    @bot.on(GroupBanNoticeEvent)
    async def _(event: GroupBanNoticeEvent):
        if event.user_id==bot.id and event.duration!=0:
            await bot.send_friend_message(config.basic_config["master"]['id'], f"bot在群{event.group_id}被禁言了{event.duration}秒\n操作者id:{event.operator_id}\n建议拉黑该群和该用户")


    @bot.on(GroupMessageEvent)
    async def changeAvatar(event: GroupMessageEvent):
        global avatar
        #bot.logger.info(event.processed_message)
        #bot.logger.error(event.get("image"))
        if event.pure_text=="换头像" and event.sender.user_id==master:
            await bot.send(event,"发来！")
            avatar=True
        if event.get("image") and avatar and event.sender.user_id==master:
            bot.logger.error(event.get("image")[0]["url"])
            r=await bot.set_qq_avatar(event.get("image")[0]["url"])
            bot.logger.error(r)
            await bot.send(event,"已更换头像！")
            avatar=False
        if event.get("mface"):
            pass
            #await bot.send(event,f"你的彩色小人gif在这里{event.get('mface')[0]['url']}")
        if event.pure_text=="给我管理" and event.sender.user_id==master:
            await bot.set_group_admin(event.group_id,event.sender.user_id,True)
            await bot.send(event, "给你了！")
        if event.pure_text=="取消管理" and event.sender.user_id==master:
            await bot.set_group_admin(event.group_id,event.sender.user_id,False)
            await bot.send(event, "取消了！")
        if event.pure_text.startswith("改群名") and event.sender.user_id==master:
            name=event.pure_text.split("改群名")[1].strip()
            await bot.set_group_name(event.group_id,name)
        if event.pure_text.startswith("我要头衔"):
            title=event.pure_text.split("我要头衔")[1].strip()
            await bot.set_group_special_title(event.group_id,event.sender.user_id,title)
            await bot.send(event, "已设置头衔！")
        if event.pure_text=="禁言我":
            await bot.mute(event.group_id,event.sender.user_id,60)
        if event.pure_text=="测试":
            r=Node(content=[Text("你好，我是机器人！")])
            await bot.send(event,r)
            await bot.send(event,Record(file="file://D:/python/Manyana/data/autoReply/voiceReply/a1axataxaWaQaia.wav"))
    @bot.on(PrivateMessageEvent)
    async def FriendMesHandler(event: PrivateMessageEvent):
        if event.pure_text=="戳我":
            await bot.friend_poke(event.sender.user_id)
    @bot.on(startUpMetaEvent)
    async def startUpHandler(event: startUpMetaEvent):
        bot.logger.info("启动成功！")
        bot_name=config.basic_config["bot"]["name"]
        bot.logger.info(f"Bot Name: {bot_name}")
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
        master_id = config.basic_config["master"]["id"]
        master_name = config.basic_config["master"]["name"]
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
        """
        戳一戳的功能实现，之所以这么复杂，是因为要获取戳一戳的具体内容。
        """
        if event.target_id==bot.id:
            if event.group_id:
                try:
                    data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                    user_name = data["data"]["nickname"]
                except:
                    user_name = ""
                bot_name=config.basic_config["bot"]["name"]
                user_info=await get_user(event.user_id,user_name)
                try:
                    text = f"{user_info[1]}{event.raw_info[2]['txt']}{bot_name}{event.raw_info[4]['txt']}"
                except:
                    bot.logger.error("获取不到戳一戳文本")
                    text="戳一戳你~"
                bot.logger.info(text)
                #print(text)
                if config.api["llm"]["aiReplyCore"]:
                    r = await aiReplyCore([{"text": text}], event.user_id, config,bot=bot)

                else:
                    reply_list=config.settings['api_implements']['nudge']['replylist']
                    r=random.choice(reply_list)
                await bot.send_group_message(event.group_id, r)
                if random.randint(1,100)<config.settings['api_implements']['nudge']['counter_probability']:
                    await bot.group_poke(event.group_id,event.user_id)
            else:
                bot_name = config.basic_config["bot"]["name"]
                user_info = await get_user(event.user_id)
                text = f"{user_info[1]}{event.raw_info[2]['txt']}{bot_name}{event.raw_info[4]['txt']}"
                bot.logger.info(text)
                if config.api["llm"]["aiReplyCore"]:
                    r = await aiReplyCore([{"text": text}], event.user_id, config,bot=bot)

                else:
                    reply_list = config.settings['api_implements']['nudge']['replylist']
                    r = random.choice(reply_list)
                await bot.send_friend_message(event.user_id, r)
                if random.randint(1,100)<config.settings['api_implements']['nudge']['counter_probability']:
                    await bot.friend_poke(event.user_id)
        #await bot.send_friend_message(event.user_id, "你戳我干啥？")
