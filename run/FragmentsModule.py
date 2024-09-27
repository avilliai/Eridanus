# -*- coding: utf-8 -*-
import datetime
import inspect
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
from yiriob.message import Text, Reply, Image, Node, Forward, Record

from plugins.FragmentsCore import chaijun, beCrazy, pic, setuGet, hisToday, querys, news, danxianglii, moyu, xingzuo, \
    get_joke, get_cp_mesg, arkOperator, sd, steamEpic, handwrite, minecraftSeverQuery, eganylist, solve, \
    search_and_download_image
from plugins.RandomDrawing import genshinDraw, qianCao, tarotChoice
from plugins.aiReplyCore import modelReply
from plugins.emojimixhandle import emojimix_handle
from plugins.gacha import arkGacha, starRailGacha, bbbgacha
from plugins.setuModerate import setuModerate
from plugins.tookits import check_cq_atcode, wash_cqCode, fileUrl, random_str, newLogger, validate_rule

logger=newLogger()
def main(bot, bus, logger):
    def load_command_rules(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    command_rules = load_command_rules('config/commands.yaml')['FragmentsModule']
    # 读取配置文件和API设置
    result=bot.api

    api_KEY = result.get("心知天气")
    proxy = result.get("proxy")
    nasa_api = result.get("nasa_api")

    with open("data/text/odes.json", encoding="utf-8") as fp:
        odes = json.loads(fp.read())
    with open("data/text/IChing.json", encoding="utf-8") as fp:
        IChing = json.loads(fp.read())

    global data
    with open('data/text/nasaTasks.yaml', 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    with open('data/userData.yaml', 'r', encoding='utf-8') as file:
        data1 = yaml.load(file, Loader=yaml.FullLoader)

    trustUser = [str(i) for i in data1 if data1[i].get('签到次数', 0) > 8]

    global picData
    picData = {}
    aiReplyCore=bot.settings["对话模型设置"]["aiReplyCore"]
    InternetMeme = bot.controller.get("图片相关").get("InternetMeme")
    #塔罗牌数据锁定
    with open('config/gachaSettings.yaml', 'r', encoding='utf-8') as f:
        resultp = yaml.load(f.read(), Loader=yaml.FullLoader)
    bbb = resultp.get("blueArchiveGacha")
    if bot.controller["运势&塔罗"]["lockLuck"]:
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
    async def handle_chaijun(event, message):
        logger.info("有楠桐调用了柴郡猫猫图")
        try:
            asffd = await chaijun()
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(asffd), type='flash', url="")])
        except:
            logger.error("获取柴郡.png失败")
            await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),
                                                          Reply(str(event.message_id))])


    async def handle_fabing(event, message):
        aim = message.replace("发病 ", "")
        logger.info("开始发病")
        try:
            asffd = await beCrazy(aim)
            await bot.send_group_message(event.group_id, [Text(asffd), Reply(str(event.message_id))])
        except:
            logger.error("调用接口失败")
            await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),
                                                          Reply(str(event.message_id))])


    async def handle_pic_request(event, message):
        # 处理图片请求逻辑
        pass


    async def handle_weather_query(event, message):
        current_function_name = inspect.currentframe().f_code.co_name
        rule=command_rules[current_function_name]["rules"][0]
        rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
        city = message.replace(rule_content, '')
        logger.info("查询 " + city + " 天气")
        wSult = await querys(city, api_KEY)
        await bot.send_group_message(event.group_id, [Text(wSult), Reply(str(event.message_id))])


    async def handle_news_today(event, message):
        logger.info("获取新闻")
        path = await news()
        await bot.send_group_message(event.group_id,
                                     [Image(file=fileUrl(path), type='flash', url=""), Reply(str(event.message_id))])


    async def handle_onedimensionli(event, message):
        logger.info("获取单向历")
        path = await danxianglii()
        await bot.send_group_message(event.group_id,
                                     [Image(file=fileUrl(path), type='flash', url=""), Reply(str(event.message_id))])


    async def handle_moyu_today(event, message):
        logger.info("获取摸鱼人日历")
        path = await moyu()
        await bot.send_group_message(event.group_id,
                                     [Image(file=fileUrl(path), type='flash', url=""), Reply(str(event.message_id))])


    async def handle_xingzuo_today(event, message):
        logger.info("获取星座运势")
        path = await xingzuo()
        await bot.send_group_message(event.group_id,
                                     [Image(file=fileUrl(path), type='flash', url=""), Reply(str(event.message_id))])
    async def emojimixer(event, message):
        r = list(wash_cqCode(event.raw_message))
        try:
            p = await emojimix_handle(r[0], r[1])
        except:
            return
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
                await bot.send_group_message(event.group_id,
                                             [Image(file=fileUrl(png_path), type='flash', url="")])
                os.remove(png_path)
            else:
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(p), type='flash', url="")])
                os.remove(p)
    async def handle_historyToday(event, message):
        logger.info("历史上的今天")
        try:
            dataBack = await hisToday()
            logger.info("获取历史上的今天")
            logger.info(str(dataBack))
            sendData = str(dataBack.get("result")).replace("[", " ").replace("{'year': '", "").replace("'}",
                                                                                                       "").replace("]",
                                                                                                                   "").replace(
                "', 'title': '", " ").replace(",", "\n")
            await bot.send_group_message(event.group_id, [Text(sendData), Reply(str(event.message_id))])
        except:
            logger.error("获取历史上的今天失败")
            await bot.send_group_message(event.group_id, [Text("获取失败，请检查网络连接"),
                                                Reply(str(event.message_id))])
    async def handle_makeJokes(event, message):
        x = wash_cqCode(event.raw_message).strip()[1:-2]
        joke = get_joke(x)
        await bot.send_group_message(event.group_id, [Text(joke), Reply(str(event.message_id))])
    async def handle_cpGenerate(event, message):
        logger.info("开始生成cp")
        x = wash_cqCode(event.raw_message)
        x = x.split(' ')
        if len(x) != 3:
            await bot.send(event, 'エラーが発生しました。再入力してください')
            return
        mesg = get_cp_mesg(x[1], x[2])
        await bot.send_group_message(event.group_id, [Text(mesg),
                                                      Reply(str(event.message_id))])
    async def handle_astronomy(event, message):
        if datetime.datetime.now().strftime('%Y-%m-%d') in data.keys():
            todayNasa = data.get(datetime.datetime.now().strftime('%Y-%m-%d'))
            path = todayNasa.get("path")
            txt = todayNasa.get("transTxt")
            try:
                await bot.send_group_message(event.group_id,
                                             [Image(file=fileUrl(path), type='flash', url=""), Text(txt),
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
                await bot.send_group_message(event.group_id,
                                             [Image(file=fileUrl(filename), type='flash', url=""), Text(txt),
                                              Reply(str(event.message_id))])
            except:
                logger.warning("获取每日天文图片失败")
                await bot.send(event, "获取失败，请联系master检查代理或api_key是否可用")
    async def handle_arkOperator(event, message):
        logger.info("又有皱皮了，生成干员信息中.....")
        o = arkOperator()
        o = o.replace("为生成", event.sender.nickname)
        await bot.send_group_message(event.group_id, [Text(o), Reply(str(event.message_id))])
    async def handle_genshinDraw(event, message):
        logger.info("有原皮！获取抽签信息中....")
        o = genshinDraw()
        logger.info("\n" + o)
        await bot.send_group_message(event.group_id, [Text(o), Reply(str(event.message_id))])
    async def handle_qianCao(event, message):
        logger.info("获取浅草百签")
        o = qianCao()
        logger.info(o)
        await bot.send_group_message(event.group_id, [Text(o), Reply(str(event.message_id))])
        if aiReplyCore:
            r = await modelReply(event.sender.nickname, event.sender.user_id, f"为我进行解签，下面是抽签的结果:{o}")
            await bot.send_group_message(event.group_id, [Text(r), Reply(str(event.message_id))])
    async def handle_tarotChoice(event, message):
        global luckList, tod
        logger.info("获取今日塔罗")
        if not bot.controller["运势&塔罗"]["lockLuck"]:
            txt, img = tarotChoice()

        else:
            if event.sender.user_id not in luckList.get(tod).get("塔罗"):
                txt, img = tarotChoice()
                luckList[str(tod)]["塔罗"][event.sender.user_id] = {"text": txt, "img": img}
                with open('data/text/lockLuck.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(luckList, file, allow_unicode=True)
            else:
                la = luckList.get(str(tod)).get("塔罗").get(event.sender.user_id)
                txt = la.get("text")
                img = la.get("img")

        await bot.send_group_message(event.group_id, [Text(txt),
                                                      Image(file=fileUrl(img), type='flash', url=""),
                                                      Reply(str(event.message_id))])
        if aiReplyCore:
            r = await modelReply(event.sender.nickname, event.sender.user_id,
                                 f"为我进行塔罗牌播报，下面是塔罗占卜的结果{txt}")
            await bot.send_group_message(event.group_id, [Text(r), Reply(str(event.message_id))])

    async def handle_yunshi(event, message):
        global luckList, tod
        logger.info("执行运势查询")
        if not bot.controller["运势&塔罗"]["lockLuck"]:
            la = os.listdir("data/pictures/amm")
            la = "data/pictures/amm/" + random.choice(la)
        else:
            if event.sender.user_id not in luckList.get(str(tod)).get("运势"):
                la = os.listdir("data/pictures/amm")
                la = "data/pictures/amm/" + random.choice(la)
                luckList[str(tod)]["运势"][event.sender.user_id] = la
                with open('data/text/lockLuck.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(luckList, file, allow_unicode=True)
            else:
                la = luckList.get(str(tod)).get("运势").get(event.sender.user_id)
        await bot.send_group_message(event.group_id, [Text(str(event.sender.nickname) + "今天的运势是"),
                                                      Image(file=fileUrl(la), type='flash', url=""),
                                                      Reply(str(event.message_id))])
    async def handle_bbbGacha(event, message):
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
    async def handle_arkGacha(event, message):
        logger.info("获取方舟抽卡结果")
        try:
            path = await arkGacha()
            logger.info("成功获取到抽卡结果")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),
                                                          Reply(str(event.message_id))])
        except:
            logger.error("皱皮衮")
            await bot.send_group_message(event.group_id, [Text("获取抽卡结果失败，请稍后再试"),
                                                          Reply(str(event.message_id))])
    async def handle_xingtieGacha(event, message):
        logger.info("获取星铁抽卡结果")
        try:
            path = await starRailGacha()
            logger.info("成功获取到星铁抽卡结果")
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),
                                                          Reply(str(event.message_id))])
        except Exception as e:
            logger.error(e)
            logger.error("穹批衮")
            await bot.send_group_message(event.group_id, [Text("获取抽卡结果失败，请稍后再试"),
                                                          Reply(str(event.message_id))])
    async def handle_addoneMore(event, message):
        logger.info("获取喜加一结果")
        try:
            path = await steamEpic()
            logger.info("获取喜加一结果")
            await bot.send_group_message(event.group_id, [Text(path),
                                                          Reply(str(event.message_id))])
        except:
            logger.error("获取喜加一结果失败，请稍后再试")
            await bot.send_group_message(event.group_id, [Text("获取喜加一结果失败，请稍后再试"),
                                                          Reply(str(event.message_id))])
    async def handle_littletail(event, message):
        current_function_name = inspect.currentframe().f_code.co_name
        rule = command_rules[current_function_name]["rules"][0]
        rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
        tail = wash_cqCode(event.raw_message).replace(rule_content, "")
        url = f"https://www.oexan.cn/API/ncwb.php?name=后缀：&wb={tail}"
        async with httpx.AsyncClient(timeout=40) as client:
            r1 = await client.get(url)
        await bot.send_group_message(event.group_id, [Text("请完整复制如下内容，否则无法使用"),
                                                      Reply(str(event.message_id))])
        await bot.send_group_message(event.group_id, [Text(r1.text.replace("后缀：", ""))])
    async def handle_zhifubao(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            numb = wash_cqCode(event.raw_message).replace(rule_content, "")
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
    async def handle_meme(event, message):
        if wash_cqCode(event.raw_message) == "meme" or (
                "meme" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message, bot.id) != False):
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
    async def handle_Poetry(event, message):
        logger.info("获取一篇诗经")
        ode = random.choice(odes.get("诗经"))
        logger.info("\n" + ode)
        await bot.send_group_message(event.group_id, [Text(ode), Reply(str(event.message_id))])
        if aiReplyCore:
            r = await modelReply(event.sender.nickname, event.sender.user_id,
                                 f"下面这首诗来自《诗经》，为我介绍它:{ode}")
            await bot.send_group_message(event.group_id, [Text(r), Reply(str(event.message_id))])
    async def handle_zhouyi(event, message):
        logger.info("获取卦象")
        IChing1 = random.choice(IChing.get("六十四卦"))
        logger.info("\n" + IChing1)
        await bot.send_group_message(event.group_id, [Text(IChing1), Reply(str(event.message_id))])
    async def handle_hanwriter(event, message):
        current_function_name = inspect.currentframe().f_code.co_name
        rule = command_rules[current_function_name]["rules"][0]
        rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
        msg = wash_cqCode(event.raw_message).replace(rule_content, "")

        logger.info("手写模拟:" + msg)
        try:
            path = await handwrite(msg)
            await bot.send_group_message(event.group_id,
                                         [Image(file=fileUrl(path), type='flash', url=""),
                                          Reply(str(event.message_id))])
        except:
            logger.error("调用手写模拟器失败")
            await bot.send_group_message(event.group_id, [Text("手写模拟失败，请稍后再试")])
    async def handle_prise(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            msg = wash_cqCode(event.raw_message).replace(rule_content, "")
            t = msg.split("#")
            url = "https://api.pearktrue.cn/api/certificate/?name=" + t[0] + "&title=" + t[1] + "&text=" + t[2]
            p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
            await bot.send_group_message(event.group_id,
                                         [Image(file=fileUrl(p), type='flash', url=""), Reply(str(event.message_id))])
            os.remove(p)
        except:
            await bot.send_group_message(event.group_id, [
                Text("出错\n格式请按照/奖状 name#title#text\n例子\n/奖状 牢大#耐摔王#康师傅冰红茶"),
                Reply(str(event.message_id))])
    async def handle_balogo(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            msg = wash_cqCode(event.raw_message).replace(rule_content, "")
            t = msg.split("#")
            url = "https://oiapi.net/API/BlueArchive?startText=" + t[0] + "&endText=" + t[1]

            p = await sd(url, "data/pictures/cache/" + random_str() + ".png")
            await bot.send_group_message(event.group_id,
                                         [Image(file=fileUrl(p), type='flash', url=""), Reply(str(event.message_id))])
        except:
            await bot.send_group_message(event.group_id, [Text("出错，格式请按照/ba Blue#Archive"),
                                                          Reply(str(event.message_id))])
    async def handle_colorfulanime(event, message):
        logger.info("彩色小人，启动！")
        colorfulCharacterList = os.listdir("data/pictures/colorfulAnimeCharacter")
        c = random.choice(colorfulCharacterList)
        await bot.send_group_message(event.group_id, [
            Image(file=fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}"), type='flash', url=""),
            Reply(str(event.message_id))])
    async def handle_minecraftQuery(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            ip = wash_cqCode(event.raw_message).replace(rule_content, "")
            logger.info(f"查mc服务器{ip}")
            a, b, c = await minecraftSeverQuery(ip)
            await bot.send_group_message(event.group_id, [
                Image(file=a, type='flash', url=""),Text(b), Text(c),
                Reply(str(event.message_id))])
        except Exception as e:
            logger.error(e)
            logger.error("mc服务器查询失败")
            await bot.send_group_message(event.group_id, Text(f"mc服务器{ip}查询失败，请检查网络连接"))
    async def handle_grammaAnalysis(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            text = wash_cqCode(event.raw_message).replace(rule_content, "")
            logger.info(f"语法分析{text}")
            p = await eganylist(text, proxy)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(p), type='flash', url=""),Reply(str(event.message_id))])
        except Exception as e:
            logger.error(e)
            logger.error("语法分析结果查询失败")
            await bot.send_group_message(event.group_id, [Text(f"语法分析结果查询失败，请检查网络连接")])
    async def handle_steamQuery(event, message):
        try:
            current_function_name = inspect.currentframe().f_code.co_name
            rule = command_rules[current_function_name]["rules"][0]
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            keyword = wash_cqCode(event.raw_message).replace(rule_content, "")
            logger.info(f"查询游戏{keyword}")
            result_dict = await solve(keyword)
            if (result_dict is None):
                await bot.send(event, "没有找到哦，试试其他名字~")
                return
            logger.info(result_dict)
            text = "游戏："
            text = text + result_dict['name'] + f"({result_dict['name_cn']})" + "\n游戏id：" + str(result_dict[
                                                                                                      'app_id']) + "\n游戏描述：" + f"{result_dict['description']}\nSteamUrl：" + f"{result_dict['steam_url']}"
            logger.info(result_dict['path'])
            logger.info(text)
            await bot.send_group_message(event.group_id,[Image(file=fileUrl(result_dict['path']), type='flash', url=""), Text(text),Reply(str(event.message_id))])
        except Exception as e:
            logger.error(e)
            logger.exception("详细错误如下：")
            await bot.send_group_message(event.group_id, [Text("查询失败，请检查网络连接")])
    async def handle_kankan(event, message):
        current_function_name = inspect.currentframe().f_code.co_name
        rule = command_rules[current_function_name]["rules"][0]
        rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
        text = wash_cqCode(event.raw_message).replace(rule_content, "")
        try:
            baidupath = await search_and_download_image(text)
            logger.info("搜索图片开始" + text)
            print(baidupath)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(baidupath), type='flash', url="")])
            os.remove(baidupath)
        except:
            logger.error("搜索图片错误")
    '''async def handle_randomASMR(event, message):
        try:
            from plugins.youtube0 import ASMR_random, get_audio, get_img
        except:
            logger.error("导入失败，请检查youtube0依赖")
            return
        logger.info("奥术魔刃，启动！")
        logger.info("获取晚安ASMR")
        logger.info(proxies)
        athor, title, video_id, length = await ASMR_random(proxies)
        imgpath = await get_img(video_id, proxies)
        audiourl = await get_audio(video_id, proxies)

        logger.info("推送晚安ASMR")
        st1 = "今日ASMR:" + title + "\n"
        st1 += "频道：" + athor + "\n"
        st1 += f"时长：{length // 60}分{length % 60}秒\n"
        await bot.send(event, [st1, Image(path=imgpath)])
        await bot.send(event, MusicShare(kind="QQMusic",
                                         title=title,
                                         summary=athor,
                                         jump_url=f"https://www.amoyshare.com/player/?v={video_id}",
                                         picture_url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                                         music_url=audiourl,
                                         brief='ASMR'))'''
    command_map = {
        "handle_chaijun": handle_chaijun,
        "handle_fabing": handle_fabing,
        "handle_weather_query": handle_weather_query,
        "handle_news_today": handle_news_today,
        "handle_onedimensionli": handle_onedimensionli,
        "handle_moyu_today": handle_moyu_today,
        "handle_xingzuo_today": handle_xingzuo_today,
        "handle_historyToday": handle_historyToday,
        "handle_makeJokes": handle_makeJokes,
        "handle_cpGenerate": handle_cpGenerate,
        "handle_astronomy": handle_astronomy,
        "handle_arkOperator": handle_arkOperator,
        "handle_genshinDraw": handle_genshinDraw,
        "handle_qianCao": handle_qianCao,
        "handle_tarotChoice": handle_tarotChoice,
        "handle_bbbGacha": handle_bbbGacha,
        "handle_xingtieGacha": handle_xingtieGacha,
        "handle_addoneMore": handle_addoneMore,
        "handle_littletail": handle_littletail,
        "handle_zhifubao": handle_zhifubao,
        "handle_meme": handle_meme,
        "handle_yunshi": handle_yunshi,
        "handle_arkGacha": handle_arkGacha,
        "handle_Poetry": handle_Poetry,
        "handle_zhouyi": handle_zhouyi,
        "handle_hanwriter": handle_hanwriter,
        "handle_prise": handle_prise,
        "handle_balogo": handle_balogo,
        "handle_colorfulanime": handle_colorfulanime,
        "handle_minecraftQuery": handle_minecraftQuery,
        "handle_grammaAnalysis": handle_grammaAnalysis,
        "handle_steamQuery": handle_steamQuery,
        "handle_kankan": handle_kankan,
    }
    @bus.on(GroupMessageEvent)
    async def handle_command(event: GroupMessageEvent):
        message = wash_cqCode(event.raw_message)
        logger.info(f"收到群{event.group_id}消息：{message}")
        logger.info(f"发送者：{event.sender.nickname}({event.sender.user_id})")
        if len(wash_cqCode(event.raw_message)) == 2:  # 表情合成专用
            await emojimixer(event, message)
        for function_name, rules in command_rules.items():
            if rules['enable']:  # 检查功能是否启用
                for rule in rules['rules']:
                    if validate_rule(message, rule):
                        await command_map[function_name](event, message)  # 通过命令映射调用处理函数
                        return




