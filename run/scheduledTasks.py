# -*- coding: utf-8 -*-
import datetime
from asyncio import sleep

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.basic_plugin.life_service import bingEveryDay, danxianglii
from plugins.basic_plugin.nasa_api import get_nasa_apod
from plugins.basic_plugin.weather_query import weather_query, free_weather_query
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import get_users_with_permission_above, get_user
from plugins.game_plugin.bangumisearch import screenshot_to_pdf_and_png
from plugins.streaming_media_service.bilibili.bili import fetch_latest_dynamic, fetch_latest_dynamic_id


async def operate_group_push_tasks(bot,event:GroupMessageEvent,config,task_type:str,operation:bool,target_uid:int=None):
    if not isinstance(event,GroupMessageEvent):
        await bot.send(event,"订阅功能目前仅支持群聊")   #私聊主动群发消息容易被腾子shutdown
        return
    if task_type=="asmr":
        if operation:
            if event.group_id in config.scheduledTasks_push_groups["latest_asmr_push"]["groups"]:
                await bot.send(event,"本群已经订阅过了")
                return
            else:
                config.scheduledTasks_push_groups["latest_asmr_push"]["groups"].append(event.group_id)
                config.save_yaml("scheduledTasks_push_groups")
                await bot.send(event,"订阅成功")
        else:
            if event.group_id in config.scheduledTasks_push_groups.yaml["latest_asmr_push"]["groups"]:
                config.scheduledTasks_push_groups["latest_asmr_push"]["groups"].remove(event.group_id)
                config.save_yaml("scheduledTasks_push_groups")
                await bot.send(event,"取消订阅成功")
            else:
                await bot.send(event,"本群没有订阅过")
    elif task_type=="bilibili":
        if operation:
            bot.logger.info_func(f"添加动态关注 群号：{event.group_id} 关注id: {target_uid}")
            if target_uid in config.bili_dynamic:
                groups=config.bili_dynamic[target_uid]["push_groups"]

                if event.group_id in groups:
                    await bot.send(event,"你已经订阅过了")
                else:
                    config.bili_dynamic[target_uid]["push_groups"].append(event.group_id)
                    config.save_yaml(str("bili_dynamic"))
                    await bot.send(event, "订阅成功")
            else:
                try:
                    latest_dynamic_id1, latest_dynamic_id2 = await fetch_latest_dynamic_id(int(target_uid))
                except:
                    await bot.send(event, "获取动态id失败，但任务已添加至配置文件。")
                    latest_dynamic_id1, latest_dynamic_id2 = 0, 0
                config.bili_dynamic[target_uid] = {"push_groups": [event.group_id], "latest_dynamic_id": [latest_dynamic_id1, latest_dynamic_id2]}
                config.save_yaml(str("bili_dynamic"))
                await bot.send(event, "订阅成功")
            try:
                p=await fetch_latest_dynamic(target_uid,config)
                await bot.send(event,Image(file=p))
            except:
                bot.logger.error(f"获取动态失败 群号：{event.group_id} 关注id: {target_uid}")
        else:
            bot.logger.info_func(f"取消动态关注 群号：{event.group_id} 关注id: {target_uid}")
            if target_uid in config.bili_dynamic:
                groups=config.bili_dynamic[target_uid]["push_groups"]
                if event.group_id in groups:
                    groups.remove(event.group_id)
                    config.save_yaml(str("bili_dynamic"))
                    await bot.send(event, "取消订阅成功")
                else:
                    await bot.send(event, "你没有订阅过")
            else:
                await bot.send(event, "不存在订阅任务")

def main(bot,config):
    logger=bot.logger
    scheduledTasks=config.settings["scheduledTasks"]


    global scheduler
    scheduler = AsyncIOScheduler()

    @bot.on(LifecycleMetaEvent)
    def start_scheduler(_):
        create_dynamic_jobs()
        scheduler.start()
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
        elif task_name == "新闻":
            pass
        elif task_name == "免费游戏喜加一":
            pass
        elif task_name == "每日天文":
            logger.info("获取今日nasa天文信息推送")
            img,text=await get_nasa_apod(config.api["nasa_api"]["api_key"],config.api["proxy"]["http_proxy"])

            """
            让ai翻译、获取群列表，然后推送
            """
        elif task_name == "摸鱼人日历":
            logger.info("摸鱼")

        elif task_name == "bing每日图像":
            logger.info("获取bing图像")
            text, p = await bingEveryDay()
            logger.info("推送")
            """
            未完成
            """
        elif task_name == "单向历":
            logger.info("获取单向历")
            path = await danxianglii()
            logger.info("推送单向历")
            """
            未完成"""
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
                scheduler.add_job(task_executor, CronTrigger(hour=hour, minute=minute), args=[task_name, task_info])
