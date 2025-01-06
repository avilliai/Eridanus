# -*- coding: utf-8 -*-
import datetime
import sys
from asyncio import sleep

import httpx
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import LifecycleMetaEvent
from developTools.message.message_components import Text, Image
from plugins.basic_plugin.life_service2 import steamEpic
from plugins.game_plugin.bangumisearch import screenshot_to_pdf_and_png
from plugins.basic_plugin.life_service import news, danxianglii, moyu, xingzuo,bingEveryDay
from plugins.utils.utils import download_img


def main(bot,config):
    logger=bot.logger
    nasa_api=config.api["nasa_api"]["api_key"]
    aiReplyCore=config.api["llm"]["aiReplyCore"]
    global scheduler
    scheduler = AsyncIOScheduler()
    proxy=config.api["proxy"]["http_proxy"]
    if proxy is not None and proxy!= '':
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    @bot.on(LifecycleMetaEvent)
    def start_scheduler(_):
        create_dynamic_jobs()
        scheduler.start()  # 启动定时器

    async def task_executor(task_name, task_info):
        logger.info(f"执行任务：{task_name}")
        global trustUser, userdict
        if task_name=="goodnight":
            morningText = task_info.get("text")
            friendList = await bot.friend_list()
            userli = [i.id for i in friendList.data]
            if task_info.get("onlyTrustUser"):
                userli2=[]
                for i in userdict:
                    try:
                        s=int(i)
                    except:
                        continue
                    singleUserData = userdict.get(i)
                    times = int(str(singleUserData.get('sts')))
                    if times > task_info.get("trustThreshold") and int(i) in userli:
                        userli2.append(str(i))
                userli = userli2
            for i in userli:
                try:
                    if aiReplyCore:
                        r = await modelReply(userdict.get(str(i)).get("userName"), int(i),
                                             f"请你对我进行晚安道别，直接发送结果即可，不要发送其他内容")
                        await bot.send_friend_message(int(i), r)
                    else:
                        await bot.send_friend_message(int(i), morningText)
                except Exception as e:
                    logger.error(e)
                    continue
                await sleep(6)
        elif task_name == "morning":
            morningText = task_info.get("text")
            friendList = await bot.friend_list()
            userli = [i.id for i in friendList.data]
            if task_info.get("onlyTrustUser"):
                userli2 = []
                for i in userdict:
                    try:
                        s=int(i)
                    except:
                        continue
                    singleUserData = userdict.get(i)
                    times = int(str(singleUserData.get('sts')))
                    if times > task_info.get("trustThreshold") and int(i) in userli:
                        userli2.append(str(i))
                userli = userli2
            for i in userli:
                try:
                    city = userdict.get(i).get("city")
                    logger.info(f"查询 {city} 天气")
                    if aiReplyCore:


                        await bot.send_friend_message(int(i), r)
                    else:
                        wSult = await weatherQuery.querys(city, api_KEY)
                        await bot.send_friend_message(int(i), morningText + wSult)
                except Exception as e:
                    logger.error(e)
                    continue
                await sleep(6)
        elif task_name == "news":
            logger.info("获取新闻")
            path = await news()
            logger.info("推送今日新闻")
            for i in config.scheduledTasks_push_groups.get(task_name).get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="steamadd1":
            logger.info("获取steam喜加一")
            path = await steamEpic()
            logger.info("推送今日喜加一列表")
            if path is None or path == "":
                return
            elif "错误" in path:
                logger.error(f"喜加一出错,{path}")
                return
            for i in config.scheduledTasks_push_groups.get("steamadd1").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), path])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="astronomy":
            logger.info("获取今日nasa天文信息推送")
            # Replace the key with your own
            dataa = {"api_key": nasa_api}
            logger.info("发起nasa请求")
            try:
                # 拼接url和参数
                url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.get(url=url)
                logger.info("获取到结果" + str(response.json()))
                # logger.info("下载缩略图")
                filename = await download_img(response.json().get("url"),
                                        "data/pictures/nasa/" + response.json().get("date") + ".png")
                txta = response.json().get(
                    "explanation")  # await translate(response.json().get("explanation"), "EN2ZH_CN")
                txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
                if aiReplyCore:
                    r = await modelReply("用户", 000000, f"将下面这段内容翻译为中文:{txt}")
                    txt = r
                for i in config.scheduledTasks_push_groups.get("astronomy").get("groups"):
                    try:
                        await bot.send_group_message(int(i),
                                                     [task_info.get("text"), Image(path=filename), txt])
                    except:
                        logger.error("不存在的群" + str(i))
            except:
                logger.warning("获取每日天文图片失败")
        elif task_name=="moyu":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("推送摸鱼人日历")
            for i in config.scheduledTasks_push_groups.get("moyu").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="bingEveryDay":
            logger.info("获取bing图像")
            text,p=await bingEveryDay()
            logger.info("推送")
            for i in config.scheduledTasks_push_groups.get("bingEveryDay").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text")+text, Image(path=p)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="constellation":
            logger.info("获取星座运势")
            path = await xingzuo()
            logger.info("推送星座运势")
            for i in config.scheduledTasks_push_groups.get("constellation").get("groups"):
                try:
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="danxiangli":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("推送单向历")
            for i in config.scheduledTasks_push_groups.get("danxiangli").get("groups"):
                try:
                    if path is None:
                        return
                    await bot.send_group_message(int(i), [task_info.get("text"), Image(path=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="bangumi":
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/cache/today-"
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            path = path + today + ".png"
            await screenshot_to_pdf_and_png(url, path, 1080, 3000)
            for i in config.scheduledTasks_push_groups.get("bangumi").get("groups"):
                try:
                    if path is None:
                        return
                    await bot.send_group_message(int(i), [Text(task_info.get("text")), Image(file=path)])
                except:
                    logger.error("不存在的群" + str(i))
        elif task_name=="nightASMR":
            logger.info("获取晚安ASMR")

        
    def create_dynamic_jobs():
        for task_name, task_info in config.scheduledTasks["scheduledTasks"].items():
            if task_info.get('enable'):
                time_parts = task_info.get('time').split('/')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                scheduler.add_job(task_executor, CronTrigger(hour=hour, minute=minute), args=[task_name, task_info])

    '''@bot.on(GroupMessage)
    async def addSubds(event: GroupMessage):
        global groupdata
        try:
            head, cmd, *o = str(event.message_chain).strip().split()
        except ValueError:
            return
        if o or head != '/推送' or not cmd:
            return
        cmds = {"摸鱼人日历": "moyu",
                "每日天文": "astronomy",
                "每日新闻": "news",
                "喜加一": "steamadd1",
                "每日星座": "constellation",
                "单向历": "danxiangli",
                "bangumi日榜":"bangumi",
                "每日bing": "bingEveryDay",
                "所有订阅": "所有订阅",
                "晚安ASMR":"nightASMR"}
        key = cmds.get(cmd, 'unknown')
        if key == 'unknown':
            return
        if cmd == "所有订阅":
            for key in keys:
                la = groupdata.get(key).get("groups")
                if event.group.id not in la:
                    la.append(event.group.id)
                    groupdata[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(groupdata, file, allow_unicode=True)
            await bot.send(event, "添加所有订阅成功")
        else:
            la = groupdata.get(key).get("groups")
            if event.group.id not in la:
                la.append(event.group.id)
                groupdata[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(groupdata, file, allow_unicode=True)
                await bot.send(event, "添加订阅成功，推送时间：" + str(scheduledTasks.get(key).get("time")))
            else:
                await bot.send(event, "添加失败，已经添加过对应的任务。")

    @bot.on(GroupMessage)
    async def cancelSubds(event: GroupMessage):
        global groupdata
        if str(event.message_chain) == "/取消 摸鱼人日历":
            key = "moyu"
        elif str(event.message_chain) == "/取消 每日天文":
            key = "astronomy"
        elif str(event.message_chain) == "/取消 每日新闻":
            key = "news"
        elif str(event.message_chain) == "/取消 喜加一":
            key = "steamadd1"
        elif str(event.message_chain) == "/取消 每日星座":
            key = "constellation"
        elif str(event.message_chain) == "/取消 单向历":
            key = "danxiangli"
        elif str(event.message_chain)=="/取消 bangumi日榜":
            key="bangumi"
        elif str(event.message_chain)=="/取消 晚安ASMR":
            key="nightASMR"
        elif str(event.message_chain)=="/取消 每日bing":
            key="bingEveryDay"
        else:
            if str(event.message_chain) == "/取消 所有订阅":
                for key in keys:
                    la = groupdata.get(key).get("groups")
                    if event.group.id in la:
                        la.remove(event.group.id)
                        groupdata[key]["groups"] = la
                with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(groupdata, file, allow_unicode=True)
                await bot.send(event, "取消所有订阅成功")
            return
        la = groupdata.get(key).get("groups")
        if event.group.id in la:
            la.remove(event.group.id)
            groupdata[key]["groups"] = la
            with open('data/scheduledTasks.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(groupdata, file, allow_unicode=True)
            await bot.send(event, "取消订阅成功")
        else:
            await bot.send(event, "取消失败，没有添加过对应的任务。")'''
