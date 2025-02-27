# -*- coding: utf-8 -*-
import datetime
import random
from asyncio import sleep

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image, Text
from plugins.basic_plugin.life_service import bingEveryDay, danxianglii
from plugins.basic_plugin.nasa_api import get_nasa_apod
from plugins.basic_plugin.weather_query import weather_query, free_weather_query
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import get_users_with_permission_above, get_user


def main(bot,config):
    logger=bot.logger
    scheduledTasks=config.settings["scheduledTasks"]

    global scheduler
    scheduler = AsyncIOScheduler()

    @bot.on(LifecycleMetaEvent)
    async def start_scheduler(_):
        await start_scheduler()  # 异步调用
        logger.info_func("定时任务已启动")

    async def task_executor(task_name, task_info):
        logger.info(f"执行任务：{task_name}")
        global trustUser, userdict
        if task_name == "晚安问候":
            friend_list = await bot.get_friend_list()
            friend_list = friend_list["data"]
            if config.settings["scheduledTasks"]["晚安问候"]["onlyTrustUser"]:
                user_ids = await get_users_with_permission_above(config.settings["scheduledTasks"]["晚安问候"]["trustThreshold"])
                filtered_users = [user for user in friend_list if user["user_id"] in user_ids]
            else:
                filtered_users = friend_list
            for user in filtered_users:
                try:
                    r = await aiReplyCore([{"text": f"道晚安，直接发送结果，不要发送多余内容"}], int(user["user_id"]), config,bot=bot,tools=None)
                    await bot.send_friend_message(int(user["user_id"]), r)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向{user['nickname']}发送晚安问候失败，原因：{e}")
            bot.logger.info("晚安问候任务执行完毕")
        elif task_name == "早安问候":
            friend_list = await bot.get_friend_list()
            friend_list = friend_list["data"]
            if config.settings["scheduledTasks"]["早安问候"]["onlyTrustUser"]:
                user_ids = await get_users_with_permission_above(
                    config.settings["scheduledTasks"]["早安问候"]["trustThreshold"])
                filtered_users = [user for user in friend_list if user["user_id"] in user_ids]
            else:
                filtered_users = friend_list
            for user in filtered_users:
                try:
                    user_info = await get_user(int(user["user_id"]))
                    location = user_info[5]
                    weather = await free_weather_query(location)
                    r = await aiReplyCore([{"text": f"播报今天的天气，直接发送结果，不要发送'好的'之类的命令应答提示。今天的天气信息如下{weather}"}], int(user["user_id"]),
                                          config, bot=bot, tools=None)
                    await bot.send_friend_message(int(user["user_id"]), r)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向{user['nickname']}发送早安问候失败，原因：{e}")
            logger.info("早安问候任务执行完毕")
        elif task_name == "新闻":
            pass
        elif task_name == "免费游戏喜加一":
            pass
        elif task_name == "每日天文":
            logger.info("获取今日nasa天文信息推送")
            img,text=await get_nasa_apod(config.api["nasa_api"]["api_key"],config.api["proxy"]["http_proxy"])
            text=await aiReplyCore([{"text": f"翻译下面的文本，直接发送结果，不要发送'好的'之类的命令应答提示。要翻译的文本为：{text}"}], random.randint(1000000, 99999999),
                                          config, bot=bot, tools=None)
            for group_id in config.sheduled_tasks_push_groups_ordinary["nasa_daily"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Text(text), Image(file=img)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送每日天文失败，原因：{e}")
                await sleep(6)
            logger.info("每日天文任务执行完毕")
        elif task_name == "摸鱼人日历":
            logger.info("摸鱼")

        elif task_name == "bing每日图像":
            logger.info("获取bing图像")
            text, p = await bingEveryDay()
            logger.info("推送bing每日图像")
            for group_id in config.sheduled_tasks_push_groups_ordinary["bing_daily"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Text(text), Image(file=p)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送bing每日图像失败，原因：{e}")
                await sleep(6)
            logger.info("bing每日图像任务执行完毕")

        elif task_name == "单向历":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("推送单向历")
            for group_id in config.sheduled_tasks_push_groups_ordinary["单向历"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Image(file=path)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送单向历失败，原因：{e}")
                await sleep(6)
            logger.info("单向历任务执行完毕")

        elif task_name == "bangumi":
            url = "https://www.bangumi.app/calendar/today"
            path = "data/pictures/cache/today-"
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            path = path + today + ".png"
            #await screenshot_to_pdf_and_png(url, path, 1080, 3000)
            """
            未完成
            """
        elif task_name == "nightASMR":
            logger.info("获取晚安ASMR")
            """
            用新的asmr推送实现
            """

    def create_dynamic_jobs():
        for task_name, task_info in scheduledTasks.items():
            if task_info.get('enable'):
                time_parts = task_info.get('time').split('/')
                hour = int(time_parts[0])
                minute = int(time_parts[1])

                bot.logger.info_func(f"定时任务已激活：{task_name}，时间：{hour}:{minute}")
                scheduler.add_job(
                    task_executor,
                    CronTrigger(hour=hour, minute=minute),
                    args=[task_name, task_info],
                    misfire_grace_time=120,
                )

    # 启动调度器
    async def start_scheduler():
        create_dynamic_jobs()
        scheduler.start()
        logger.info("定时任务已启动")

    allow_args = ["每日天文", "bing每日图像", "单向历", "bangumi", "nightASMR", "摸鱼人日历", "新闻", "免费游戏喜加一"]
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.message.startswith("/cron add "):
            args = event.message.split("/cron add ")

            if args[1] and args[1] in allow_args:
                if event.group_id in config.sheduled_tasks_push_groups_ordinary[args[1]]["groups"]:
                    await bot.send(event, "本群已经订阅过了")
                    return
                else:
                    config.sheduled_tasks_push_groups_ordinary[args[1]]["groups"].append(event.group_id)
                    config.save_yaml("sheduled_tasks_push_groups_ordinary")
                    await bot.send(event, "订阅成功")
            else:
                await bot.send(event, "不支持的任务，可选任务有：每日天文，bing每日图像，单向历，bangumi，nightASMR，摸鱼人日历，新闻，免费游戏喜加一")
        elif event.message.startswith("/cron remove "):
            args = event.message.split("/cron remove ")
            if args[1] and args[1] in allow_args:
                if event.group_id in config.sheduled_tasks_push_groups_ordinary[args[1]]["groups"]:
                    config.sheduled_tasks_push_groups_ordinary[args[1]]["groups"].remove(event.group_id)
                    config.save_yaml("sheduled_tasks_push_groups_ordinary")
                    await bot.send(event, "取消订阅成功")
                else:
                    await bot.send(event, "本群没有订阅过")
            else:
                await bot.send(event, "不支持的任务，可选任务有：每日天文，bing每日图像，单向历，bangumi，nightASMR，摸鱼人日历，新闻，免费游戏喜加一")

