# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
from io import BytesIO

import httpx
import requests
import yaml
from yiriob.event.events import GroupMessageEvent
from PIL import Image as Image1
from yiriob.message import MessageChain, Text, At, Reply, Record, Image,Node,Forward

from plugins.FragmentsCore import chaijun, beCrazy, pic, setuGet, hisToday, querys, news, danxianglii, moyu, xingzuo, \
    get_joke, get_cp_mesg, arkOperator, sd, steamEpic
from plugins.RandomDrawing import genshinDraw, qianCao, tarotChoice
from plugins.aiReplyCore import modelReply
from plugins.emojimixhandle import emojimix_handle
from plugins.gacha import arkGacha, starRailGacha, bbbgacha
from plugins.setuModerate import setuModerate
from plugins.toolkits import check_cq_atcode, wash_cqCode, fileUrl, random_str


'''
此部分为过去的extraParts.py。功能集合。同时Fragments与plugins中各函数一一对应。
可用指令：
柴郡  发病 xxx   emoji合成  历史上的今天  查询xxxx（即天气查询）  新闻  单向历  摸鱼  星座  /xx笑话
/cp 1 2     @bot 天文   干员生成   抽签    @bot 诗经     @bot 周易
/奖状 name#title#text 例子:/奖状 牢大#耐摔王#康师傅冰红茶
/ba Blue#Archive
小尾巴 xxxx
meme   运势   今日塔罗   彩色小人

不可用指令
@bot 5图
@bot 5张xxxx
手写 xxxx
方舟十连
星铁十连
ba十连
喜加一
'''

def main(bot,bus,logger):
    # 读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    api_KEY = result.get("心知天气")
    proxy = result.get("proxy")
    moderateK = result.get("moderate")
    nasa_api = result.get("nasa_api")
    proxy = result.get("proxy")

    logger.info("Fragments loaded")
    with open("data/text/odes.json", encoding="utf-8") as fp:
        odes = json.loads(fp.read())
    with open("data/text/IChing.json", encoding="utf-8") as fp:
        IChing = json.loads(fp.read())
    global data
    with open('data/text/nasaTasks.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data1 = yaml.load(file, Loader=yaml.FullLoader)
    global trustUser
    userdict = data1
    trustUser = []
    for i in userdict.keys():
        data2 = userdict.get(i)
        times = int(str(data2.get('签到次数')))
        if times > 8:
            trustUser.append(str(i))
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result1 = yaml.load(f.read(), Loader=yaml.FullLoader)
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controllerResult = yaml.load(f.read(), Loader=yaml.FullLoader)
    r18 = controllerResult.get("图片相关").get("r18Pic")
    onlyTrustUserR18 = controllerResult.get("图片相关").get("onlyTrustUserR18")
    withPic = controllerResult.get("图片相关").get("withPic")
    grayPic = controllerResult.get("图片相关").get("grayPic")
    allowPic = controllerResult.get("图片相关").get("allowPic")
    selfsensor = result1.get("moderate").get("selfsensor")
    selfthreshold = result1.get("moderate").get("selfthreshold")
    aiReplyCore = result1.get("对话模型设置").get("aiReplyCore")



    global picData
    picData = {}




    @bus.on(GroupMessageEvent)
    async def handle_group_message(event:GroupMessageEvent):
        # if wash_cqCode(event.raw_message) == '/pic':
        if check_cq_atcode(event.raw_message,bot.id)!=False:
            if '/pic' in wash_cqCode(event.raw_message):
                picNum = int((wash_cqCode(event.raw_message))[4:])
            elif str(bot.id) not in wash_cqCode(event.raw_message) and len(wash_cqCode(event.raw_message)) < 6:
                if get_number(wash_cqCode(event.raw_message)) is None:
                    return
                else:
                    picNum = int(get_number(wash_cqCode(event.raw_message)))

            else:
                return
            logger.info("图片获取指令....数量：" + str(picNum))
            if 10 > picNum > -1:
                for i in range(picNum):
                    logger.info("获取壁纸")
                    a = await pic()
                    await bot.send_group_message(event.group_id, [Image(file=fileUrl(a), type='flash', url="")])
            elif picNum == '':
                a = await pic()
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(a), type='flash', url="")])
            else:
                await bot.send_group_message(event.group_id, [Text("数字超出限制"),
                                                              Reply(str(event.message_id))])
            logger.info("图片获取完成")

    # 整点正则
    pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

    # 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
    def get_number(string):
        # 使用re.match方法，返回匹配的结果对象
        match = re.match(pattern, string)
        # 如果结果对象不为空，返回捕获的数字，否则返回None
        if match:
            # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
            if match.group(2):
                return match.group(2)
            else:
                return match.group(3)
        else:
            return None

    @bus.on(GroupMessageEvent)
    async def setuHelper(event:GroupMessageEvent):
        pattern1 = r'(\d+)张(\w+)'
        global picData
        if check_cq_atcode(event.raw_message,bot.id)!=False:
            text1 = wash_cqCode(event.raw_message).replace("壁纸", "").replace("涩图", "").replace("色图", "").replace("图",
                                                                                                                 "").replace(
                "r18", "")
            match1 = re.search(pattern1, text1)
            if match1:
                if not allowPic:
                    await bot.send_group_message(event.group_id, [Text("发图功能已关闭，可使用 5图 指令使用备用发图功能")])
                    return
                logger.info("提取图片关键字。 数量: " + str(match1.group(1)) + " 关键字: " + match1.group(2))
                data = {"tag": ""}
                if "r18" in wash_cqCode(event.raw_message) or "色图" in wash_cqCode(event.raw_message) or "涩图" in str(
                        wash_cqCode(event.raw_message)):
                    if (str(event.sender.user_id) in trustUser and onlyTrustUserR18) or r18:
                        data["r18"] = 1
                    else:
                        await bot.send_group_message(event.group_id, [Text("r18模式已关闭")])
                picData[event.sender.user_id] = []
                data["tag"] = match1.group(2)
                data["size"] = "regular"
                logger.info("组装数据完成：" + str(data))
                a = int(match1.group(1))
                if int(match1.group(1)) > 6:
                    a = 5
                    await bot.send_group_message(event.group_id, [Text("api访问限制，修改获取张数为 5")])
                fordMes = []
                for i in range(a):
                    try:
                        url, path = await setuGet(data, withPic, grayPic)
                    except Exception as e:
                        logger.error(e)
                        logger.error("涩图请求出错")
                        # await bot.send(event,"请求出错，请稍后再试")
                        continue
                    logger.info(f"获取到图片: {url} {path}")

                    if selfsensor:
                        try:
                            thurs = await setuModerate(url, moderateK)
                            logger.info(f"获取到审核结果： adult- {thurs}")
                            if int(thurs) > selfthreshold:
                                logger.warning(f"不安全的图片，自我审核过滤")
                                await bot.send(event, ["nsfw内容已过滤", Image(
                                    path="data/pictures/colorfulAnimeCharacter/" + random.choice(
                                        os.listdir("data/pictures/colorfulAnimeCharacter")))])
                                continue
                        except Exception as e:
                            logger.error(e)
                            logger.error("无法进行自我审核，错误的网络环境或apikey")
                            await bot.send(event, ["审核策略失效，为确保安全，不显示本图片", Image(
                                path="data/pictures/colorfulAnimeCharacter/" + random.choice(
                                    os.listdir("data/pictures/colorfulAnimeCharacter")))])
                            continue
                    if withPic:
                        fordMes.append(Node(nickname="Eridanus",content=[Text(url),Image(file=fileUrl(path), type='flash', url="")]))
                        '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([url, Image(path=path)]))'''
                        #await bot.send_group_message(event.group_id, [Text(url),Image(file=fileUrl(path), type='flash', url="")])
                    else:
                        fordMes.append(Node(nickname="Eridanus", content=[Text(url)]))
                        '''b1 = ForwardMessageNode(sender_id=bot.qq, sender_name="Manyana",
                                                message_chain=MessageChain([url]))'''
                    #fordMes.append(b1)
                    # await bot.send(event, Image(url=path))'''

                    logger.info("图片获取成功")
                try:
                    await bot.send(event, Forward(fordMes))
                except Exception as e:
                    logger.error(e)
                    await bot.send(event, "出错，请稍后再试")



    @bus.on(GroupMessageEvent)
    async def NasaHelper(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)!=False and "诗经" in wash_cqCode(event.raw_message):


    @bus.on(GroupMessageEvent)
    async def NasaHelper(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)!=False and "周易" in wash_cqCode(event.raw_message):


    @bus.on(GroupMessageEvent)
    async def handwrite(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("手写 "):


    @bus.on(GroupMessageEvent)
    async def jiangzhuang(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("/奖状") or wash_cqCode(event.raw_message).startswith("/证书"):
            try:
                t = wash_cqCode(event.raw_message)[3:].split("#")
                if wash_cqCode(event.raw_message).startswith("/奖状"):
                    url = "https://api.pearktrue.cn/api/certcommend/?name=" + t[0] + "&title=" + t[1] + "&classname=" + \
                          t[2]
                else:
                    url = "https://api.pearktrue.cn/api/certificate/?name=" + t[0] + "&title=" + t[1] + "&text=" + t[2]
                p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
                await bot.send_group_message(event.group_id,[Image(file=fileUrl(p), type='flash', url=""), Reply(str(event.message_id))])
                os.remove(p)
            except:
                await bot.send_group_message(event.group_id,[Text("出错\n格式请按照/奖状 name#title#text\n例子\n/奖状 牢大#耐摔王#康师傅冰红茶"),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def jiangzhuang(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("/ba ") and "#" in wash_cqCode(event.raw_message):



    @bus.on(GroupMessageEvent)
    async def tarotToday(event:GroupMessageEvent):

        if ("今日塔罗" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "今日塔罗":


    @bus.on(GroupMessageEvent)
    async def tarotToday(event:GroupMessageEvent):
        if ("彩色小人" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "彩色小人":
            logger.info("彩色小人，启动！")
            c = random.choice(colorfulCharacterList)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}"), type='flash', url=""),Reply(str(event.message_id))])
