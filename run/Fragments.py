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
from plugins.tookits import check_cq_atcode, wash_cqCode, fileUrl, random_str


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
    colorfulCharacterList = os.listdir("data/pictures/colorfulAnimeCharacter")
    lockResult = controllerResult.get("运势&塔罗").get("lockLuck")
    InternetMeme = controllerResult.get("图片相关").get("InternetMeme")

    global picData
    picData = {}
    with open('config/gachaSettings.yaml', 'r', encoding='utf-8') as f:
        resultp = yaml.load(f.read(), Loader=yaml.FullLoader)
    bbb = resultp.get("blueArchiveGacha")
    if lockResult:
        with open('data/text/lockLuck.yaml', 'r', encoding='utf-8') as f:
            result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global luckList
        global tod
        tod = str(datetime.date.today())
        if tod in result2:
            luckList = result2
        else:
            luckList = {str(tod): {"运势": {123: "", 456: ""}, "塔罗": {123: {"text": "hahaha", "path": ",,,"}}}}
            with open('data/text/lockLuck.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(luckList, file, allow_unicode=True)


    @bus.on(GroupMessageEvent)
    async def chaijunmaomao(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message) == "柴郡" or (
                check_cq_atcode(event.raw_message,bot.id)!=False and "柴郡" in wash_cqCode(event.raw_message)):
            try:
                logger.info("有楠桐调用了柴郡猫猫图")
                asffd = await chaijun()
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(asffd), type='flash', url="")])
                asffd = await chaijun()
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(asffd), type='flash', url="")])
            except:
                logger.error("获取柴郡.png失败")
                await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def fabing(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("发病 ") or (
                check_cq_atcode(event.raw_message,bot.id)!=False and "发病 " in wash_cqCode(event.raw_message)):
            try:
                logger.info("开始发病")
                aim = wash_cqCode(event.raw_message).replace("发病 ", "")
                asffd = await beCrazy(aim)
                logger.info(asffd)
                await bot.send_group_message(event.group_id, [Text(asffd),
                                                              Reply(str(event.message_id))])
            except:
                logger.error("调用接口失败")
                await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),
                                                              Reply(str(event.message_id))])

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
    async def emojiMix(event:GroupMessageEvent):
        if len(wash_cqCode(event.raw_message)) == 2:
            r = list(wash_cqCode(event.raw_message))
            try:
                p = await emojimix_handle(r[0], r[1])
            except:
                return
            #            if p!=None:
            #                logger.info(f"emoji合成：{r[0]} + {r[1]}")
            #                await bot.send(event,Image(path=p),True)
            if p == "not_emoji":
                return
            elif p == 'a':
                msg = f'不正确的参数：{r[0]}'
            elif p == 'b':
                msg = f'不正确的参数：{r[1]}'
            elif p is None:
                msg = '表情不支持，请重新选择'
            else:
                logger.info(f"emoji合成：{r[0]} + {r[1]}")
                if p.startswith('https://'):
                    png_path = "data/pictures/cache/" + random_str() + ".png"
                    async with httpx.AsyncClient(timeout=20) as client:
                        r = await client.get(p)
                        with open(png_path, "wb") as f:
                            f.write(r.content)  # 从二进制数据创建图片对象
                    # msg = MessageSegment.image(result)
                    await bot.send_group_message(event.group_id, [Image(file=fileUrl(png_path), type='flash', url="")])
                    os.remove(png_path)
                    #await bot.send(event, Image(path=png_path), True)
                else:
                    await bot.send_group_message(event.group_id, [Image(file=fileUrl(p), type='flash', url="")])
                    os.remove(p)
                    #await bot.send(event, Image(path=p), True)
                    # msg = MessageSegment.image('file://'+result)
            # await emojimix.send(msg)

    @bus.on(GroupMessageEvent)
    async def historyToday(event:GroupMessageEvent):
        pattern = r".*史.*今.*|.*今.*史.*"
        string = wash_cqCode(event.raw_message)
        match = re.search(pattern, string)
        if match:
            dataBack = await hisToday()
            logger.info("获取历史上的今天")
            logger.info(str(dataBack))
            sendData = str(dataBack.get("result")).replace("[", " ").replace("{'year': '", "").replace("'}",
                                                                                                       "").replace("]",
                                                                                                                   "").replace(
                "', 'title': '", " ").replace(",", "\n")
            await bot.send_group_message(event.group_id, [Text(sendData),Reply(str(event.message_id))])


    @bus.on(GroupMessageEvent)
    async def weather_query(event:GroupMessageEvent):
        # 从消息链中取出文本
        msg = str(event.raw_message)
        # 匹配指令
        m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
        if m:
            # 取出指令中的地名
            city = m.group(1)
            logger.info("查询 " + city + " 天气")
            wSult = await querys(city, api_KEY)
            # 发送天气消息
            if aiReplyCore:
                r = await modelReply(event.sender.nickname, event.sender.user_id,
                                     f"请你为我进行天气播报，下面是天气查询的结果：{wSult}")
                await bot.send_group_message(event.group_id, [Text(r), Reply(str(event.message_id))])
            else:
                await bot.send_group_message(event.group_id, [Text(wSult),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def newsToday(event:GroupMessageEvent):
        if ("新闻" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "新闻":
            logger.info("获取新闻")
            path = await news()
            logger.info("成功获取到今日新闻")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def onedimensionli(event:GroupMessageEvent):
        if ("单向历" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "单向历":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("成功获取到单向历")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("摸鱼" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "摸鱼":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("成功获取到摸鱼人日历")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("星座" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "星座":
            logger.info("获取星座运势")
            path = await xingzuo()
            logger.info("成功获取到星座运势")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def make_jokes(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith('/') and wash_cqCode(event.raw_message).endswith('笑话'):
            x = wash_cqCode(event.raw_message).strip()[1:-2]
            joke = get_joke(x)
            await bot.send_group_message(event.group_id, [Text(joke),
                                                          Reply(str(event.message_id))])

    # 凑个cp
    @bus.on(GroupMessageEvent)
    async def make_cp_mesg(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("/cp "):
            x = wash_cqCode(event.raw_message).replace('/cp ', '', 1)
            x = x.split(' ')
            if len(x) != 2:
                await bot.send(event, 'エラーが発生しました。再入力してください')
                return
            mesg = get_cp_mesg(x[0], x[1])
            await bot.send_group_message(event.group_id, [Text(mesg),
                                                          Reply(str(event.message_id))])


    @bus.on(GroupMessageEvent)
    async def NasaHelper(event:GroupMessageEvent):
        global data
        if check_cq_atcode(event.raw_message,bot.id)!=False and "天文" in wash_cqCode(event.raw_message):
            # logger.info(str(data.keys()))
            if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
                todayNasa = data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
                path = todayNasa.get("path")
                txt = todayNasa.get("transTxt")
                try:
                    await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Text(txt),
                                                                  Reply(str(event.message_id))])
                except:
                    await bot.send_group_message(event.group_id, [Text(txt),
                                                                  Reply(str(event.message_id))])
            else:
                proxies = {
                    "http://": proxy,
                    "https://": proxy
                }
                # Replace the key with your own
                dataa = {"api_key": nasa_api}
                logger.info("发起nasa请求")
                try:
                    # 拼接url和参数
                    url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                    async with httpx.AsyncClient(proxies=proxies) as client:
                        # 用get方法发送请求
                        response = await client.get(url=url)
                    # response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                    logger.info("获取到结果" + str(response.json()))
                    # logger.info("下载缩略图")
                    filename = "data/pictures/nasa/" + response.json().get("date") + ".png"
                    async with httpx.AsyncClient(proxies=proxies) as client:
                        # 用get方法发送请求
                        esp = await client.get(url=response.json().get("url"))
                        img = Image1.open(BytesIO(esp.content))  # 从二进制数据创建图片对象
                        img.save(filename)


                    txt = response.json().get("date") + "\n" + response.json().get(
                        "title") + "\n" + response.json().get("explanation")
                    if aiReplyCore:
                        txt = await modelReply(event.sender.nickname, event.sender.user_id,
                                               f"将下面这段内容翻译为中文:{txt}")
                    temp = {"path": "data/pictures/nasa/" + response.json().get("date") + ".png",
                            "oriTxt": response.json().get("explanation"), "transTxt": txt}

                    data[datetime.datetime.now().strftime('%Y-%m-%d')] = temp

                    with open('data/text/nasaTasks.yaml', 'w', encoding="utf-8") as file:
                        yaml.dump(data, file, allow_unicode=True)
                    await bot.send_group_message(event.group_id, [Image(file=fileUrl(filename), type='flash', url=""),Text(txt),Reply(str(event.message_id))])
                except:
                    logger.warning("获取每日天文图片失败")
                    await bot.send(event, "获取失败，请联系master检查代理或api_key是否可用")

    @bus.on(GroupMessageEvent)
    async def arkGene(event:GroupMessageEvent):
        if "干员" in wash_cqCode(event.raw_message) and "生成" in wash_cqCode(event.raw_message):
            logger.info("又有皱皮了，生成干员信息中.....")
            o = arkOperator()
            o = o.replace("为生成", event.sender.nickname)
            await bot.send_group_message(event.group_id, [Text(o),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def genshin1(event:GroupMessageEvent):
        if ("原神" in wash_cqCode(event.raw_message) and "启动" in wash_cqCode(event.raw_message)) or (
                "抽签" in wash_cqCode(event.raw_message) and "原" in wash_cqCode(event.raw_message)):
            logger.info("有原皮！获取抽签信息中....")
            o = genshinDraw()
            logger.info("\n" + o)
            await bot.send_group_message(event.group_id, [Text(o),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def genshin1(event:GroupMessageEvent):
        if ("抽签" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or "抽签" == str(
                wash_cqCode(event.raw_message)):
            logger.info("获取浅草百签")
            o = qianCao()
            logger.info(o)
            await bot.send_group_message(event.group_id, [Text(o),Reply(str(event.message_id))])
            if aiReplyCore:
                r = await modelReply(event.sender.nickname, event.sender.user_id, f"为我进行解签，下面是抽签的结果:{o}")
                await bot.send_group_message(event.group_id, [Text(r),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def NasaHelper(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)!=False and "诗经" in wash_cqCode(event.raw_message):
            logger.info("获取一篇诗经")
            ode = random.choice(odes.get("诗经"))
            logger.info("\n" + ode)
            await bot.send_group_message(event.group_id, [Text(ode),Reply(str(event.message_id))])
            if aiReplyCore:
                r = await modelReply(event.sender.nickname, event.sender.user_id,
                                     f"下面这首诗来自《诗经》，为我介绍它:{ode}")
                await bot.send_group_message(event.group_id, [Text(r),Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def NasaHelper(event:GroupMessageEvent):
        if check_cq_atcode(event.raw_message,bot.id)!=False and "周易" in wash_cqCode(event.raw_message):
            logger.info("获取卦象")
            IChing1 = random.choice(IChing.get("六十四卦"))
            logger.info("\n" + IChing1)
            await bot.send_group_message(event.group_id, [Text(IChing1), Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def handwrite(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("手写 "):
            msg = wash_cqCode(event.raw_message).replace("手写 ", "")
            logger.info("手写模拟:" + msg)
            try:
                path = await handwrite(msg)
                await bot.send_group_message(event.group_id,
                                             [Image(file=fileUrl(path), type='flash', url=""),
                                              Reply(str(event.message_id))])
            except:
                logger.error("调用手写模拟器失败")

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
            try:
                t = wash_cqCode(event.raw_message).replace("/ba ", "").split("#")
                url = "https://oiapi.net/API/BlueArchive?startText=" + t[0] + "&endText=" + t[1]

                p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
                await bot.send_group_message(event.group_id,[Image(file=fileUrl(p), type='flash', url=""), Reply(str(event.message_id))])
            except:
                await bot.send_group_message(event.group_id, [Text("出错，格式请按照/ba Blue#Archive"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("方舟十连" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "方舟十连":
            logger.info("获取方舟抽卡结果")
            try:
                path = await arkGacha()
                logger.info("成功获取到抽卡结果")
                await bot.send_group_message(event.group_id,[Image(file=fileUrl(path), type='flash', url=""), Reply(str(event.message_id))])
            except:
                logger.error("皱皮衮")
                await bot.send_group_message(event.group_id, [Text("获取抽卡结果失败，请稍后再试"),
                                                              Reply(str(event.message_id))])


    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("星铁十连" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "星铁十连":
            logger.info("获取星铁抽卡结果")
            try:
                path = await starRailGacha()
                logger.info("成功获取到星铁抽卡结果")
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),
                                                              Reply(str(event.message_id))])
            except:
                logger.error("穹批衮")
                await bot.send_group_message(event.group_id, [Text("获取抽卡结果失败，请稍后再试"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("ba十连" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "ba十连":
            logger.info("获取ba抽卡结果")
            try:
                path = await bbbgacha(bbb)
                logger.info("成功获取到ba抽卡结果")
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),
                                                              Reply(str(event.message_id))])
            except:
                logger.error("碧p衮")
                await bot.send_group_message(event.group_id, [Text("获取抽卡结果失败，请稍后再试"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def moyuToday(event:GroupMessageEvent):
        if ("喜加一" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "喜加一":
            logger.info("获取喜加一结果")
            try:
                path = await steamEpic()
                logger.info("获取喜加一结果")
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),
                                                              Reply(str(event.message_id))])
            except:
                logger.error("获取喜加一结果失败，请稍后再试")
                await bot.send_group_message(event.group_id, [Text("获取喜加一结果失败，请稍后再试"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def tail(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("小尾巴 "):
            tail = wash_cqCode(event.raw_message).replace("小尾巴", "")
            url = f"https://www.oexan.cn/API/ncwb.php?name=后缀：&wb={tail}"
            async with httpx.AsyncClient(timeout=40) as client:
                r1 = await client.get(url)
            await bot.send_group_message(event.group_id, [Text("请完整复制如下内容，否则无法使用"),
                                                          Reply(str(event.message_id))])
            await bot.send_group_message(event.group_id, [Text(r1.text.replace("后缀：", "")),
                                                          Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def zhifubao(event:GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("支付宝到账 "):
            try:
                numb = wash_cqCode(event.raw_message).replace("支付宝到账 ", "")
                url = f"https://free.wqwlkj.cn/wqwlapi/alipay_yy.php?money={str(numb)}"
                r = requests.get(url)
                p = "data/voices/" + random_str() + '.wav'
                logger.info(f"支付宝到账：{numb}")
                with open(p, "wb") as f:
                    f.write(r.content)
                await bot.send_group_message(event.group_id, [Record(file=fileUrl(p), url="")])
            except Exception as e:
                logger.error(e)
                await bot.send_group_message(event.group_id, [Text("生成失败，请检查数额"),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def meme(event:GroupMessageEvent):
        global memeData
        if wash_cqCode(event.raw_message) == "meme" or (
                "meme" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False):
            if InternetMeme:
                logger.info("使用网络meme")

                url = 'https://meme-api.com/gimme'
                proxies = {
                    "http://": proxy,
                    "https://": proxy
                }
                async with httpx.AsyncClient(timeout=20) as client:
                    r = await client.get(url)
                    logger.info(r.json().get("preview")[-1])
                    async with httpx.AsyncClient(timeout=20, proxies=proxies) as client:
                        r = await client.get(r.json().get("preview")[-1])
                        img = Image1.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                        path = "data/pictures/meme/" + random_str() + ".png"
                        img.save(path)  # 使用PIL库保存图片
                        await bot.send(event, Image(path=path))

            else:
                logger.warning("使用本地meme图")
                la = os.listdir("data/pictures/meme")
                la = "data/pictures/meme/" + random.choice(la)
                logger.info("掉落了一张meme图")
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(la), type='flash', url=""),
                                                              Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def yunshi(event:GroupMessageEvent):
        global memeData, luckList, tod
        if ("运势" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "运势":
            logger.info("执行运势查询")
            if not lockResult:
                la = os.listdir("data/pictures/amm")
                la = "data/pictures/amm/" + random.choice(la)
            else:
                if event.sender.user_id not in luckList.get(str(tod)).get("运势"):
                    la = os.listdir("data/pictures/amm")
                    la = "data/pictures/amm/" + random.choice(la)
                    luckList[str(tod)]["运势"][event.sender.user_id] = la
                else:
                    la = luckList.get(str(tod)).get("运势").get(event.sender.user_id)
                with open('data/text/lockLuck.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(luckList, file, allow_unicode=True)
            await bot.send_group_message(event.group_id, [Text(str(event.sender.nickname) + "今天的运势是"),Image(file=fileUrl(la), type='flash', url=""),
                                                          Reply(str(event.message_id))])

    @bus.on(GroupMessageEvent)
    async def tarotToday(event:GroupMessageEvent):
        global luckList, tod
        if ("今日塔罗" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "今日塔罗":
            logger.info("获取今日塔罗")
            if not lockResult:
                txt, img = tarotChoice()

            else:
                if event.sender.user_id not in luckList.get(tod).get("塔罗"):
                    txt, img = tarotChoice()
                    luckList[str(tod)]["塔罗"][event.sender.user_id] = {"text": txt, "img": img}
                else:
                    la = luckList.get(str(tod)).get("塔罗").get(event.sender.user_id)
                    txt=la.get("text")
                    img=la.get("img")
            await bot.send_group_message(event.group_id, [Text(txt),
                                                          Image(file=fileUrl(img), type='flash', url=""),
                                                          Reply(str(event.message_id))])
            if aiReplyCore:
                r = await modelReply(event.sender.nickname, event.sender.user_id,
                                     f"为我进行塔罗牌播报，下面是塔罗占卜的结果{txt}")
                await bot.send_group_message(event.group_id, [Text(r), Reply(str(event.message_id))])
            with open('data/text/lockLuck.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(luckList, file, allow_unicode=True)

    @bus.on(GroupMessageEvent)
    async def tarotToday(event:GroupMessageEvent):
        if ("彩色小人" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,bot.id)!=False) or str(
                wash_cqCode(event.raw_message)) == "彩色小人":
            logger.info("彩色小人，启动！")
            c = random.choice(colorfulCharacterList)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}"), type='flash', url=""),Reply(str(event.message_id))])
