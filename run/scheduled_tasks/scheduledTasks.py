# -*- coding: utf-8 -*-
import datetime
import random
from asyncio import sleep

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image, Text, Card
from framework_common.database_util.User import get_users_with_permission_above, get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.utils.random_str import random_str
from framework_common.utils.utils import download_img
from run.ai_llm.service.aiReplyCore import aiReplyCore
from run.basic_plugin.service.life_service import bingEveryDay, danxianglii
from run.basic_plugin.service.nasa_api import get_nasa_apod
from run.basic_plugin.service.weather_query import free_weather_query
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja
from run.resource_collector.service.asmr.asmr100 import random_asmr_100
from run.streaming_media.service.Link_parsing.Link_parsing import bangumi_PILimg
from run.system_plugin.func_collection import trigger_tasks


def main(bot: ExtendBot, config):
    logger = bot.logger
    scheduledTasks = config.scheduled_tasks.config["scheduledTasks"]

    scheduler = AsyncIOScheduler()

    enabled = False

    @bot.on(LifecycleMetaEvent)
    async def start_scheduler(_):
        nonlocal enabled
        if not enabled:
            enabled = True
            await start_scheduler()  # 异步调用

    async def task_executor(task_name, task_info):
        logger.info_func(f"执行任务：{task_name}, 信息:{task_info}")
        if task_name == "晚安问候":
            friend_list = await bot.get_friend_list()
            friend_list = friend_list["data"]
            if config.scheduled_tasks.config["scheduledTasks"]["晚安问候"]["onlyTrustUser"]:
                user_ids = await get_users_with_permission_above(
                    config.scheduled_tasks.config["scheduledTasks"]["晚安问候"]["trustThreshold"])
                filtered_users = [user for user in friend_list if user["user_id"] in user_ids]
            else:
                filtered_users = friend_list
            for user in filtered_users:
                try:
                    r = await aiReplyCore([{"text": f"道晚安，直接发送结果，不要发送多余内容"}], int(user["user_id"]),
                                          config, bot=bot, tools=None)
                    await bot.send_friend_message(int(user["user_id"]), r)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向{user['nickname']}发送晚安问候失败，原因：{e}")
            bot.logger.info_func("晚安问候任务执行完毕")
        elif task_name == "早安问候":
            friend_list = await bot.get_friend_list()
            friend_list = friend_list["data"]
            if config.scheduled_tasks.config["scheduledTasks"]["早安问候"]["onlyTrustUser"]:
                user_ids = await get_users_with_permission_above(
                    config.scheduled_tasks.config["scheduledTasks"]["早安问候"]["trustThreshold"])
                filtered_users = [user for user in friend_list if user["user_id"] in user_ids]
            else:
                filtered_users = friend_list
            for user in filtered_users:
                try:
                    user_info = await get_user(int(user["user_id"]))
                    location = user_info.city
                    weather = await free_weather_query(location)
                    r = await aiReplyCore([{
                        "text": f"播报今天的天气，保持你的角色，根据天气给出建议，直接发送结果，不要发送'好的'之类的命令应答提示。今天的天气信息如下{weather}"}],
                        int(user["user_id"]),
                        config, bot=bot, tools=None)
                    await bot.send_friend_message(int(user["user_id"]), r)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向{user['nickname']}发送早安问候失败，原因：{e}")
            logger.info_func("早安问候任务执行完毕")
        elif task_name == "新闻":
            pass
        elif task_name == "免费游戏喜加一":
            pass
        elif task_name == "每日天文":
            logger.info_func("获取今日nasa天文信息推送")
            img, text = await get_nasa_apod(config.basic_plugin.config["nasa_api"]["api_key"],
                                            config.common_config.basic_config["proxy"]["http_proxy"])
            text = await aiReplyCore(
                [{"text": f"翻译下面的文本，直接发送结果，不要发送'好的'之类的命令应答提示。要翻译的文本为：{text}"}],
                random.randint(1000000, 99999999),
                config, bot=bot, tools=None)
            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["每日天文"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Text(text), Image(file=img)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送每日天文失败，原因：{e}")
                await sleep(6)
            logger.info_func("每日天文任务执行完毕")
        elif task_name == "摸鱼人日历":
            logger.info_func("获取摸鱼人日历")
        elif task_name == "bing每日图像":
            text, p = await bingEveryDay()
            logger.info_func("推送bing每日图像")
            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["bing每日图像"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Text(text), Image(file=p)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送bing每日图像失败，原因：{e}")
                await sleep(6)
            logger.info_func("bing每日图像任务执行完毕")

        elif task_name == "单向历":
            logger.info_func("获取单向历")
            path = await danxianglii()
            logger.info_func("推送单向历")
            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["单向历"]["groups"]:
                if group_id == 0: continue
                try:
                    await bot.send_group_message(group_id, [Image(file=path)])
                except Exception as e:
                    logger.error(f"向群{group_id}推送单向历失败，原因：{e}")
                await sleep(6)
            logger.info_func("单向历推送执行完毕")

        elif task_name == "bangumi":
            logger.info_func("获取bangumi每日推送")
            weekday = datetime.datetime.today().weekday()
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            bangumi_json = await bangumi_PILimg(filepath='data/pictures/cache/',
                                                type_soft=f'bangumi 周{weekdays[weekday]}放送',
                                                name=f'bangumi 周{weekdays[weekday]}放送', type='calendar')
            if bangumi_json['status']:
                logger.info_func("推送bangumi每日番剧")
                for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["bangumi"]["groups"]:
                    text = config.scheduled_tasks.config['scheduledTasks']['bangumi']['text']
                    if group_id == 0: continue
                    try:
                        await bot.send_group_message(group_id, [Text(text), Image(file=bangumi_json['pic_path'])])
                    except Exception as e:
                        logger.error(f"向群{group_id}推送单向历失败，原因：{e}")
                    await sleep(6)
            logger.info_func("bangumi推送执行完毕")
        elif task_name == "nightASMR":
            logger.info_func("获取晚安ASMR")
            """
            用新的asmr推送实现
            """

            async def get_random_asmr():
                try:
                    r = await random_asmr_100(proxy=config.common_config.basic_config["proxy"]["http_proxy"])

                    i = random.choice(r['media_urls'])
                    return i, r
                except Exception as e:
                    logger.error(f"获取晚安ASMR失败，原因：{e}")
                    return get_random_asmr()

            i, r = await get_random_asmr()
            try:
                img = await download_img(r['mainCoverUrl'], f"data/pictures/cache/{random_str()}.png",
                                         config.resource_collector.config["asmr"]["gray_layer"],
                                         proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            except Exception as e:
                bot.logger.error(f"download_img error:{e}")
                img = None

            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"]:
                if group_id == 0: continue
                try:

                    await bot.send_group_message(group_id, Card(audio=i[0], title=i[1], image=r['mainCoverUrl']))
                    if img:
                        await bot.send_group_message(group_id,
                                                     [Text(
                                                         f"随机asmr\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"),
                                                         Image(file=img)])
                    else:
                        await bot.send_group_message(group_id,
                                                     [Text(
                                                         f"随机asmr\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}")])
                except Exception as e:
                    logger.error(f"向群{group_id}推送单向历失败，原因：{e}")
                await sleep(6)
            logger.info_func("单向历推送执行完毕")
        elif task_name in ["早安", "晚安", "午安"]:
            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[task_name]["groups"]:
                if group_id == 0: continue
                try:
                    r = await aiReplyCore(
                        [{"text": f"你现在是一个群机器人，向群内所有人道{task_name}，直接发送结果，不要发送多余内容"}],
                        random.randint(1000000, 99999999), config, bot=bot, tools=None)
                    await bot.send_group_message(group_id, r)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向群{group_id}推送{task_name}失败，原因：{e}")
                    continue
        elif task_name == "忍术大学习":
            logger.info_func("获取忍术大学习")

            async def get_random_renshu():
                ninja = Lexburner_Ninja()
                ninjutsu = await ninja.random_ninjutsu()
                tags = ""
                for tag in ninjutsu['tags']:
                    tags += f"{tag['name']}"
                parse_message = f"忍术名称: {ninjutsu['name']}\n忍术介绍: {ninjutsu['description']}\n忍术标签: {tags}\n忍术教学: {ninjutsu['videoLink']}\n更多忍术请访问: https://wsfrs.com/"
                if not ninjutsu['imageUrl']:
                    messages = [Image(file="run/group_fun/service/img.png"), Text("啊没图使\n"),
                                Text(parse_message)]
                else:
                    messages = [Image(file=ninjutsu['imageUrl']), Text(parse_message)]
                return messages

            messages = await get_random_renshu()
            logger.info_func("推送忍术大学习")
            for group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[task_name]["groups"]:
                if group_id == 0: continue
                try:
                    # r = await aiReplyCore([{"text": f"你现在是一个群机器人，向群内所有人道{task_name}，直接发送结果，不要发送多余内容"}], random.randint(1000000, 99999999),config, bot=bot, tools=None)
                    await bot.send_group_message(group_id, messages)
                    await sleep(6)
                except Exception as e:
                    logger.error(f"向群{group_id}推送{task_name}失败，原因：{e}")
                    continue

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

    @bot.on(GroupMessageEvent)
    async def _(event: GroupMessageEvent):
        if event.pure_text == "测试定时任务" and event.user_id == config.common_config.basic_config["master"]['id']:
            for task_name, task_info in scheduledTasks.items():
                await task_executor(task_name, task_info)

    # 启动调度器
    async def start_scheduler():
        create_dynamic_jobs()
        scheduler.start()

    allow_args = ["忍术大学习", "每日天文", "bing每日图像", "单向历", "bangumi", "nightASMR", "摸鱼人日历", "新闻",
                  "免费游戏喜加一", "早安", "晚安", "午安"]

    @bot.on(GroupMessageEvent)
    async def _(event: GroupMessageEvent):
        if event.pure_text.startswith("/cron add "):
            args = event.pure_text.split("/cron add ")

            async def check_and_add_group_id(arg):
                if arg and arg in allow_args:
                    if event.group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[arg]["groups"]:
                        if args[1] != "all": await bot.send(event, f"本群已经订阅过了{arg}")
                        return
                    else:
                        config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[arg]["groups"].append(event.group_id)
                        config.save_yaml("sheduled_tasks_push_groups_ordinary", plugin_name="scheduled_tasks")
                        if args[1] != "all": await bot.send(event, f"{arg}订阅成功")
                else:
                    if args[1] != "all": await bot.send(event,
                                                        f"不支持的任务，可选任务有：{allow_args}")

            if args[1] == "all":
                for allow_arg in allow_args:
                    await check_and_add_group_id(allow_arg)
                await bot.send(event, "所有订阅已更新")
            else:
                await check_and_add_group_id(args[1])

        elif event.pure_text.startswith("/cron remove "):
            args = event.pure_text.split("/cron remove ")

            async def remove_group_id(arg):
                if arg and arg in allow_args:
                    if event.group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[arg]["groups"]:
                        config.scheduled_tasks.sheduled_tasks_push_groups_ordinary[arg]["groups"].remove(event.group_id)
                        config.save_yaml("sheduled_tasks_push_groups_ordinary", plugin_name="scheduled_tasks")
                        if args[1] != "all": await bot.send(event, f"取消{arg}订阅成功")
                    else:
                        if args[1] != "all": await bot.send(event, "本群没有订阅过")
                else:
                    if args[1] != "all": await bot.send(event, f"不支持的任务，可选任务有：{allow_args}")

            if args[1] == "all":
                for allow_arg in allow_args:
                    await remove_group_id(allow_arg)
                await bot.send(event, "所有订阅已取消")
            else:
                await remove_group_id(args[1])

    @bot.on(GroupMessageEvent)
    async def _(event: GroupMessageEvent):
        if event.pure_text == "今日天文":
            data = await trigger_tasks(bot, event, config, "nasa_daily")
            img = data["要发送的图片"]
            text = data["将下列文本翻译后发送"]
            text = await aiReplyCore(
                [{"text": f"翻译下面的文本，直接发送结果，不要发送'好的'之类的命令应答提示。要翻译的文本为：{text}"}],
                random.randint(1000000, 99999999),
                config, bot=bot, tools=None)
            await bot.send(event, [Text(text), Image(file=img)])
        if event.pure_text == "单向历":
            await trigger_tasks(bot, event, config, "单向历")
