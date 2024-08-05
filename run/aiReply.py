# -*- coding: utf-8 -*-
import asyncio
import datetime
import os
import random

import threading
from asyncio import sleep

import yaml
from yiriob.event.events import GroupMessageEvent, PrivateMessageEvent
from yiriob.interface import SendGroupMessageInterface, SendGroupMessageParams
from yiriob.message import MessageChain, Text, At, Reply, Record

from plugins.aiReplyCore import modelReply, clearAllPrompts, tstt, clearsinglePrompt
from plugins.tookits import check_cq_atcode, extract_image_urls, CListen
from plugins.wReply.wontRep import wontrep

def main(bot, bus, logger):
    with open('config.yaml', 'r', encoding='utf-8') as f:
        conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    master=conf["master"]
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        resul = yaml.load(f.read(), Loader=yaml.FullLoader)
    global trustG
    trustG = resul.get("trustGroups")
    # 读取个性化角色设定
    with open('data/ChatCharacters.yaml', 'r', encoding='utf-8') as f:
        result2223 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global chatGLMCharacters
    chatGLMCharacters = result2223
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = resulttr.get("proxy")
    if proxy != "":
        os.environ["http_proxy"] = proxy

    with open('config/noResponse.yaml', 'r', encoding='utf-8') as f:
        noRes1 = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    friendsAndGroups = result.get("加群和好友")
    trustDays = friendsAndGroups.get("trustDays")
    glmReply = result.get("对话模型设置").get("glmReply")
    privateGlmReply = result.get("对话模型设置").get("privateGlmReply")
    nudgeornot = result.get("对话模型设置").get("nudgeReply")
    replyModel = result.get("对话模型设置").get("model")
    trustglmReply = result.get("对话模型设置").get("trustglmReply")
    allcharacters = result.get("对话模型设置").get("bot_info")
    allowUserSetModel = result.get("对话模型设置").get("allowUserSetModel")
    maxTextLen = result.get("对话模型设置").get("maxLen")
    voiceRate = result.get("对话模型设置").get("voiceRate")
    withText = result.get("对话模型设置").get("withText")
    
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    global userdict
    userdict = data
    trustUser = []
    for i in userdict.keys():
        data = userdict.get(i)
        try:
            times = int(str(data.get('签到次数')))
            if times > trustDays:
                trustUser.append(str(i))

        except Exception as e:
            logger.error(f"用户{i}的签到次数 数值出错，请打开data/userData.yaml检查，将其修改为正常数值")
    logger.info('chatglm部分已读取信任用户' + str(len(trustUser)) + '个')

    # 线程预备
    newLoop = asyncio.new_event_loop()
    listen = CListen(newLoop)
    listen.setDaemon(True)
    listen.start()
    global chattingUser
    chattingUser={} #无需艾特即可对话的用户列表
    timeout = datetime.timedelta(minutes=5) #5分钟没有对话则超时
    @bus.on(GroupMessageEvent)
    async def AddChatWithoutAt(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        if check_cq_atcode(event.raw_message,bot.id)=="开始对话" or check_cq_atcode(event.raw_message,bot.id)=="开始聊天":
            global chattingUser
            user = event.sender.user_id
            chattingUser[user] = datetime.datetime.now()
            await bot.adapter.call_api(
                SendGroupMessageInterface,
                SendGroupMessageParams(
                    group_id=event.group_id, message=MessageChain([Reply(str(event.message_id)),Text("发送 退出 可退出当前对话")])
                ),
            )
    @bus.on(GroupMessageEvent)
    async def removeChatWithoutAt(event:GroupMessageEvent):
        global chattingUser
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        if check_cq_atcode(event.raw_message,bot.id)=="退出" and event.sender.user_id in chattingUser:
            user = event.sender.user_id
            chattingUser.pop(user)
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)), Text("已结束当前对话")])


    '''@bot.on(NudgeEvent)
    async def NudgeReply(event: NudgeEvent):
        global trustUser
        #戳一戳使用ai回复的话，和这部分放在一起会更好。
        if event.target == bot.qq and nudgeornot:
            global chatGLMCharacters
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")

            text = random.choice(["戳你一下", "摸摸头", "戳戳你的头", "摸摸~"])
            if event.from_id in chatGLMCharacters:
                #print(chatGLMCharacters.get(event.target), type(chatGLMCharacters.get(event.target)))
                r = await modelReply("指挥", event.from_id, text,chatGLMCharacters.get(event.from_id))
            # 判断模型类型
            else:
                r= await modelReply("指挥", event.from_id, text)
            if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
                try:
                    voiceP = await tstt(r)
                    await bot.send_group_message(event.subject.id, Voice(path=voiceP))
                    if withText:
                        await bot.send_group_message(event.subject.id, r)
                except:
                    logger.error("语音合成调用失败")
                    await bot.send_group_message(event.subject.id, r)
            else:
                await bot.send_group_message(event.subject.id, r)'''

    # 私聊使用chatGLM,对信任用户或配置了apiKey的用户开启
    @bus.on(PrivateMessageEvent)
    async def GLMFriendChat(event: PrivateMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        global chatGLMCharacters, trustUser, userdict
        text = check_cq_atcode(event.raw_message,bot.id)
        if text == "/clear":
            return
        if event.sender.user_id == master:
            noresm = ["群列表", "/bl", "退群#", "/quit"]
            for saa in noresm:
                if text == saa or text.startswith(saa):
                    logger.warning("与屏蔽词匹配，不回复")
                    return
        if privateGlmReply or (trustglmReply and event.sender.user_id in trustUser):
            pass
        else:
            return
        text = check_cq_atcode(event.raw_message,bot.id)
        imgurl = extract_image_urls(event.raw_message)

        if event.sender.user_id in chatGLMCharacters:
            print(type(chatGLMCharacters.get(event.sender.user_id)), chatGLMCharacters.get(event.sender.user_id))
            r, firstRep = await modelReply(event.sender.nickname, event.sender.user_id, text,
                                           chatGLMCharacters.get(event.sender.user_id), trustUser, imgurl,checkIfRepFirstTime=True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.nickname, event.sender.user_id, text, replyModel, trustUser,imgurl,
                                           checkIfRepFirstTime=True)
        if firstRep:
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)), Text("如对话异常请发送 /clear 以清理对话")])
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
            try:
                voiceP = await tstt(r)
                await bot.send_group_message(event.group_id, [Record(file=voiceP, url="")])
                if withText:
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                                  Text(r)])
            except:
                logger.error("语音合成调用失败")
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                              Text(r)])
        else:
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                          Text(r)])

    # 私聊中chatGLM清除本地缓存
    @bus.on(PrivateMessageEvent)
    async def clearPrompt(event: PrivateMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id) == "/clear":
            reff = await clearsinglePrompt(event.sender.user_id)
            await bot.send_friend_message(event.sender.user_id, [Text(reff)])
        elif check_cq_atcode(event.raw_message,bot.id) == "/allclear" and event.sender.user_id == master:
            reff = await clearAllPrompts()
            await bot.send_friend_message(event.sender.user_id, [Text(reff)])

    # 私聊设置bot角色
    # print(trustUser)
    @bus.on(PrivateMessageEvent)
    async def showCharacter(event: PrivateMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id) == "可用角色模板" or "角色模板" in check_cq_atcode(event.raw_message,bot.id):
            st1 = ""
            for isa in allcharacters:
                st1 += isa + "\n"
            await bot.send_friend_message(event.sender.user_id, [Text("对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")])


    @bus.on(PrivateMessageEvent)
    async def setCharacter(event: PrivateMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        global chatGLMCharacters
        if check_cq_atcode(event.raw_message,bot.id).startswith("设定#"):
            if check_cq_atcode(event.raw_message,bot.id).split("#")[1] in allcharacters and allowUserSetModel:
                meta12 = check_cq_atcode(event.raw_message,bot.id).split("#")[1]

                chatGLMCharacters[event.sender.user_id] = meta12
                logger.info("当前：" + str(chatGLMCharacters))
                with open('data/ChatCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send_friend_message(event.sender.user_id,
                                              [Text("设定成功")])
            else:
                if allowUserSetModel:
                    await bot.send_friend_message(event.sender.user_id,[Text("不存在的角色")])
                    await bot.send(event, "不存在的角色")
                else:
                    await bot.send_friend_message(event.sender.user_id,[Text("禁止用户自行设定模型(可联系master修改配置)")])

    # print(trustUser)
    @bus.on(GroupMessageEvent)
    async def showCharacter(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id) == "可用角色模板" or (
                check_cq_atcode(event.raw_message,bot.id)!=False and "角色模板" in check_cq_atcode(event.raw_message,bot.id)):
            st1 = ""
            for isa in allcharacters:
                st1 += isa + "\n"
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                          Text("对话可用角色模板：\n" + st1 + "\n发送：设定#角色名 以设定角色")])


    @bus.on(GroupMessageEvent)
    async def setCharacter(event:GroupMessageEvent):
        global chatGLMCharacters, userdict
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        if check_cq_atcode(event.raw_message,bot.id).startswith("设定#"):
            if check_cq_atcode(event.raw_message,bot.id).split("#")[1] in allcharacters and allowUserSetModel:
                meta12 = check_cq_atcode(event.raw_message,bot.id).split("#")[1]

                chatGLMCharacters[event.sender.user_id] = meta12
                logger.info("当前：" + str(chatGLMCharacters))
                with open('data/ChatCharacters.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(chatGLMCharacters, file, allow_unicode=True)
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                              Text(
                                                                  "设定成功")])
            else:
                if allowUserSetModel:
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                                  Text(
                                                                      "不存在的角色")])
                else:
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                                  Text(
                                                                      "禁止用户自行设定模型(可联系master修改配置)")])

    '''@bus.on(Start)
    async def upDate(event: Startup):
        while True:
            await sleep(60)
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            global userdict
            userdict = data
            trustUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('签到次数')))
                if times > trustDays:
                    trustUser.append(str(i))
            #定时清理用户
            global chattingUser
            now = datetime.datetime.now()
            to_remove = [user for user, timestamp in chattingUser.items() if now - timestamp > timeout]
            for user in to_remove:
                del chattingUser[user]
                logger.info(f"Removed user {user} due to inactivity")'''
    @bus.on(GroupMessageEvent)
    async def upddd(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)==False:
            return
        if check_cq_atcode(event.raw_message,bot.id).startswith("授权") and event.sender.user_id == master:
            await sleep(15)
            with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                resul = yaml.load(f.read(), Loader=yaml.FullLoader)
            global trustG
            trustG = resul.get("trustGroups")
            with open('data/userData.yaml', 'r', encoding='utf-8') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
            global trustUser
            global userdict
            userdict = data
            trustUser = []
            for i in userdict.keys():
                data = userdict.get(i)
                times = int(str(data.get('签到次数')))
                if times > trustDays:
                    trustUser.append(str(i))
            logger.info('已读取信任用户' + str(len(trustUser)) + '个')

    # 群内chatGLM回复
    @bus.on(GroupMessageEvent)
    async def atReply(event:GroupMessageEvent):
        global trustUser, chatGLMCharacters, userdict,trustG,chattingUser
        if check_cq_atcode(event.raw_message,bot.id)!=False or event.sender.user_id in chattingUser:
            try:
                if not wontrep(noRes1, check_cq_atcode(event.raw_message,bot.id).replace(" ", ""),
                               logger):
                    return
            except Exception as e:
                logger.error(f"无法运行屏蔽词审核，请检查noResponse.yaml配置格式--{e}")
        if (check_cq_atcode(event.raw_message,bot.id)!=False or event.sender.user_id in chattingUser) and (glmReply or (trustglmReply and str(
                event.sender.user_id) in trustUser) or event.group.id in trustG):
            logger.info("ai聊天启动")
        else:
            return
        text = check_cq_atcode(event.raw_message,bot.id)
        imgurl = extract_image_urls(event.raw_message)
        if event.sender.user_id in chatGLMCharacters:
            print(type(chatGLMCharacters.get(event.sender.user_id)), chatGLMCharacters.get(event.sender.user_id))
            r, firstRep = await modelReply(event.sender.nickname, event.sender.user_id, text,
                                           chatGLMCharacters.get(event.sender.user_id), trustUser, imgurl,True)
        # 判断模型
        else:
            r, firstRep = await modelReply(event.sender.nickname, event.sender.user_id, text, replyModel, trustUser, imgurl,True)
        if firstRep:
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),
                                                          Text(
                                                              "如对话异常请发送 /clear")])
        #刷新时间
        user = event.sender.user_id
        if user in chattingUser:
            chattingUser[user] = datetime.datetime.now()
        if len(r) < maxTextLen and random.randint(0, 100) < voiceRate:
            try:
                voiceP = await tstt(r)
                await bot.send_group_message(event.group_id,[Record(file=voiceP,url="")])
                if withText:
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Text(r)])
            except Exception as e:
                logger.error(e)
                logger.error("语音合成失败")
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Text(r)])
        else:
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Text(r)])

    # 用于chatGLM清除本地缓存
    @bus.on(GroupMessageEvent)
    async def clearPrompt(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id) == "/clear":
            reff = await clearsinglePrompt(event.sender.user_id)
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)), Text(reff)])
        elif check_cq_atcode(event.raw_message,bot.id) == "/allclear" and event.sender.user_id == master:
            reff = await clearAllPrompts()
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)), Text(reff)])
