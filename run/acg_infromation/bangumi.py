import random
import os
import datetime
import aiosqlite
import asyncio
import httpx
import requests
import re
import json
from developTools.event.events import GroupMessageEvent, FriendRequestEvent, PrivateMessageEvent, startUpMetaEvent, \
    ProfileLikeEvent, PokeNotifyEvent
from developTools.message.message_components import Record, Node, Text, Image,At
from asyncio import sleep
from plugins.game_plugin.bangumisearch import banguimiList,bangumisearch,screenshot_to_pdf_and_png,run_async_task,daily_task
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


async def call_bangumi_search(bot,event,config,keywords,cat):
    try:
        dic={"番剧": 'all',"动画":2,"书籍":1,"游戏":4,"音乐":3,"三次元":6}
        url = f"https://bgm.tv/subject_search/{keywords}?cat={dic[cat]}"
        resu = await bangumisearch(url)
        subjectlist = resu[1]
        crtlist = resu[2]
        order = 1
        if str(event.raw_message).startswith("0") and order <= len(crtlist):
            crt = crtlist[order - 1].find("a")["href"]
            url = "https://bgm.tv" + crt
            bot.logger.info("正在获取" + crt + "详情")
            path = f"data/pictures/cache/search-{keywords}-0{order}.png"
            title = crtlist[order - 1].find("a").string
        elif 1 <= order <= len(subjectlist):
            subject = subjectlist[order - 1].find("a")["href"]
            url = "https://bgm.tv" + subject
            bot.logger.info("正在获取" + subject + "详情")
            path = f"data/pictures/cache/search-{keywords}-{order}.png"
            title = subjectlist[order - 1].find("a").string
        else:
            await bot.send(event, "查询失败！不规范的操作")
            searchtask.pop(event.sender.user_id)
            return
        try:
            bot.logger.info("正在获取" + title + "详情")
            await screenshot_to_pdf_and_png(url, path, 1080, 1750)
            await bot.send(event, [Text(f'查询结果：{title}'), Image(file=path)])
        except Exception as e:
            bot.logger.error(e)
            await bot.send(event, "查询失败，重新试试？")

    except Exception as e:
        bot.logger.error(e)
        await bot.send(event, "查询失败，重新试试？")
async def call_remen(bot,event,config):
    pass

def main(bot,config):
    global searchtask  # 变量提前，否则可能未定义
    searchtask = {}
    global switch
    switch=0
    global recall_id
    recall_id = None
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_async_task, trigger=CronTrigger(hour=0, minute=1))
    scheduler.start()
    bot.logger.info("Bangumi功能已启动")
    @bot.on(GroupMessageEvent)
    async def bangumi_search(event: GroupMessageEvent):
        if ("新番排行" in str(event.raw_message)) or ("新番top" in str(event.raw_message)) or (
                "本月新番" in str(event.raw_message)):
            year = datetime.datetime.now().strftime("%Y")  # 默认当前年份，修一个问题
            month = datetime.datetime.now().strftime("%m")  # 默认当前月份
        elif ("番剧排行" in str(event.raw_message)) or ("番剧top" in str(event.raw_message)) \
                or ("动画排行" in str(event.raw_message)) or ("动画top" in str(event.raw_message)):
            year = ""  # 默认空值,表示全部
            month = ""  # 默认空值,表示全部
        else:
            return
        if "年" in str(event.raw_message):
            year = str(event.raw_message).split("年")[0]  # 获取年份参数
            year = re.sub(r'[^\d]', '', year)[-4::]
        if "月" in str(event.raw_message):  # 获取月份参数
            try:
                month = str(event.raw_message).split("年")[1].split("月")[0]
            except:
                month = str(event.raw_message).split("月")[0]
            if len(month) < 2:
                month = "0" + month
        try:
            if "top" in str(event.raw_message):
                top = int(str(event.raw_message).split("top")[1])  # 获取top参数
            elif "排行" in str(event.raw_message):
                top = int(str(event.raw_message).split("排行")[1])

            elif "本月新番" in str(event.raw_message):
                top = 10
                month = datetime.datetime.now().strftime("%m")

        except:
            top = 24

        try:
            finalT, finalC, isbottom = await banguimiList(year, month, top)
            finalT, finalC, isbottom = await banguimiList(2024, 12, top)
            print(finalT, finalC, isbottom)

            title = year + "年" + month + "月 | Bangumi 番组计划\n"
            if year == "":
                title = "| Bangumi 番组计划\n"
            if month == "":
                title = title.replace("月", "")
            bottom = "到底啦~"
            combined_list = []
            rank = 1
            #print(len(finalT))
            times = len(finalT) // 10
            if len(finalT) % 10 != 0:
                times += 1
            cmList=[]
            for i in range(times):
                combined_str = ""
                if i == 0:
                    combined_str += "title,"
                for j in range(10):  # 10个一组发送消息
                    combined_str += f"Image(url=finalC[{rank - 1}],cache=True),finalT[{rank - 1}]"
                    rank += 1
                    if i * 10 + j + 1 == len(finalT):
                        break
                    if j != 9:
                        combined_str += ","
                if isbottom:
                    combined_str += ",bottom"
                for title, cover in zip(finalT, finalC[:len(finalT)]):
                    # display(Image(url=cover, cache=True))  # 显示图片
                    #print(title, cover)
                    cmList.append(Node(content=[Text(f'{title}'),Image(file=cover)]))
            bot.logger.info("获取番剧排行成功")
            await bot.send(event, cmList)
        except Exception as e:
            bot.logger.error(e)
            await bot.send(event, "获取番剧信息失败，请稍后再试")

    @bot.on(GroupMessageEvent)
    async def bangumi_search(event: GroupMessageEvent):
        if not event.raw_message.startswith(config.settings["acg_information"]["bangumi_query_prefix"]):
            return
        if "bangumi查询" in str(event.raw_message) or "番剧查询" in str(event.raw_message):
                #url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
                cat="all"
                keywords = str(event.raw_message).replace(" ", "").split("查询")[1]
        elif "查询动画" in str(event.raw_message) or "查询番剧" in str(event.raw_message):
                cat=2
                keywords = str(event.raw_message).replace(" ", "").split("动画")[1]
        elif "查询书籍" in str(event.raw_message):
                cat=1
                keywords = str(event.raw_message).replace(" ", "").split("书籍")[1]
        elif "查询游戏" in str(event.raw_message):
                cat=4
                keywords = str(event.raw_message).replace(" ", "").split("游戏")[1]
        elif "查询音乐" in str(event.raw_message):
                cat=3
                keywords = str(event.raw_message).replace(" ", "").split("音乐")[1]
        elif "查询三次元" in str(event.raw_message):
                cat=6
                keywords = str(event.raw_message).replace(" ", "").split("三次元")[1]
        else:
            return
        bot.logger.info("正在查询：" + keywords)
        url = f"https://bgm.tv/subject_search/{keywords}?cat={cat}"

        path = "data/pictures/cache/" + keywords + ".png"
        global searchtask  # 变量提前，否则可能未定义
        try:
            r = await bangumisearch(url)
            str0 = f"{r[0]}\n请发送编号进入详情页，或发送退出退出查询"
            await screenshot_to_pdf_and_png(url, path, 1080, 1750)
            global recall_id
            recall_id = await bot.send(event, [Text(f'{str0}'), Image(file=path)], True)
            # print(recall_id)
            global switch

            searchtask[event.sender.user_id] = keywords, cat
            switch = 1
        except Exception as e:
            bot.logger.error(e)
            searchtask.pop(event.sender.user_id)
            await bot.send(event, "查询失败，请稍后再试")


    @bot.on(GroupMessageEvent)
    async def bangumi_search_detail(event: GroupMessageEvent):
        global searchtask, recall_id
        if event.sender.user_id in searchtask:
            try:
                if str(event.raw_message) == "退出":
                    searchtask.pop(event.sender.user_id)
                    await bot.recall(recall_id['data']['message_id'])
                    await bot.send(event, "已退出查询")
                    return
                keywords, cat = searchtask[event.sender.user_id]
                url = f"https://bgm.tv/subject_search/{keywords}?cat={cat}"
                resu = await bangumisearch(url)
                subjectlist = resu[1]
                crtlist = resu[2]
                order = int(str(event.raw_message))
                searchtask.pop(event.sender.user_id)
                await bot.recall(recall_id['data']['message_id'])
                recall_id = await bot.send(event, "正在获取，请稍后~~~")
                if str(event.raw_message).startswith("0") and order <= len(crtlist):
                    crt = crtlist[order - 1].find("a")["href"]
                    url = "https://bgm.tv" + crt
                    bot.logger.info("正在获取" + crt + "详情")
                    path = f"data/pictures/cache/search-{keywords}-0{order}.png"
                    title = crtlist[order - 1].find("a").string
                elif 1 <= order <= len(subjectlist):
                    subject = subjectlist[order - 1].find("a")["href"]
                    url = "https://bgm.tv" + subject
                    bot.logger.info("正在获取" + subject + "详情")
                    path = f"data/pictures/cache/search-{keywords}-{order}.png"
                    title = subjectlist[order - 1].find("a").string
                else:
                    await bot.send(event, "查询失败！不规范的操作")
                    searchtask.pop(event.sender.user_id)
                    return
                try:
                    bot.logger.info("正在获取" + title + "详情")
                    await screenshot_to_pdf_and_png(url, path, 1080, 1750)
                    await bot.send(event, [Text(f'查询结果：{title}'), Image(file=path)])
                except Exception as e:
                    bot.logger.error(e)
                    await bot.send(event, "查询失败，请稍后再试")
                try:
                    searchtask.pop(event.sender.user_id)
                except Exception as e:
                    bot.logger.error(e)
                    pass
            except Exception as e:
                bot.logger.error(e)
                searchtask.pop(event.sender.user_id)
                await bot.send(event, "查询失败！不规范的操作")
            await bot.recall(recall_id['data']['message_id'])

    @bot.on(GroupMessageEvent)
    async def bangumi_search_timeout(event: GroupMessageEvent):
        global searchtask
        global switch
        if event.sender.user_id in searchtask:
            if switch:
                switch = 0  # 保证只发送一次超时提示
                await sleep(60 * 3)
                if event.sender.user_id in searchtask:  # 检验查询是否结束
                    searchtask.pop(event.sender.user_id)
                    await bot.send(event, "查询超时，已自动退出")

    @bot.on(GroupMessageEvent)
    async def Bilibili_today_hot(event: GroupMessageEvent):
        file_path = 'data/pictures/wife_you_want_img/'
        output_path = f'{file_path}bili_today_hot_back_out.png'
        if '今日热门'==event.raw_message:
            if not os.path.isfile(output_path):
                await daily_task()
            bot.logger.info('今日热门开启！！！')
            await bot.send(event, Image(file=output_path))