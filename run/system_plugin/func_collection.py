# -*- coding: utf-8 -*-


from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image
from run.basic_plugin.service.life_service import danxianglii
from run.basic_plugin.service.nasa_api import get_nasa_apod
from run.streaming_media.service.bilibili.bili import fetch_latest_dynamic, fetch_latest_dynamic_id
async def operate_group_push_tasks(bot,event:GroupMessageEvent,config,task_type:str,operation:bool,target_uid:int=None):
    if not isinstance(event,GroupMessageEvent):
        await bot.send(event,"订阅功能目前仅支持群聊")   #私聊主动群发消息容易被腾子shutdown
        return
    if task_type=="asmr":
        if operation:
            if event.group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"]:
                await bot.send(event,"本群已经订阅过了")
                return
            else:
                config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"].append(event.group_id)
                config.save_yaml("sheduled_tasks_push_groups_ordinary",plugin_name="scheduled_tasks")
                await bot.send(event,"订阅成功")
        else:
            if event.group_id in config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"]:
                config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"].remove(event.group_id)
                config.save_yaml("sheduled_tasks_push_groups_ordinary",plugin_name="scheduled_tasks")
                await bot.send(event,"取消订阅成功")
            else:
                await bot.send(event,"本群没有订阅过")
    elif task_type=="bilibili":
        if operation:
            bot.logger.info_func(f"添加动态关注 群号：{event.group_id} 关注id: {target_uid}")
            if target_uid in config.streaming_media.bili_dynamic:
                groups=config.streaming_media.bili_dynamic[target_uid]["push_groups"]

                if event.group_id in groups:
                    await bot.send(event,"你已经订阅过了")
                else:
                    config.streaming_media.bili_dynamic[target_uid]["push_groups"].append(event.group_id)
                    config.save_yaml("bili_dynamic",plugin_name="streaming_media")
                    await bot.send(event, "订阅成功")
            else:
                try:
                    latest_dynamic_id1, latest_dynamic_id2 = await fetch_latest_dynamic_id(int(target_uid))
                except:
                    await bot.send(event, "获取动态id失败，但任务已添加至配置文件。")
                    latest_dynamic_id1, latest_dynamic_id2 = 0, 0
                config.streaming_media.bili_dynamic[target_uid] = {"push_groups": [event.group_id], "latest_dynamic_id": [latest_dynamic_id1, latest_dynamic_id2]}
                config.save_yaml("bili_dynamic",plugin_name="streaming_media")
                await bot.send(event, "订阅成功")
            try:
                p=await fetch_latest_dynamic(target_uid,config)
                await bot.send(event,Image(file=p))
            except:
                bot.logger.error(f"获取动态失败 群号：{event.group_id} 关注id: {target_uid}")
        else:
            bot.logger.info_func(f"取消动态关注 群号：{event.group_id} 关注id: {target_uid}")
            if target_uid in config.streaming_media.bili_dynamic:
                groups=config.streaming_media.bili_dynamic[target_uid]["push_groups"]
                if event.group_id in groups:
                    groups.remove(event.group_id)
                    config.save_yaml("bili_dynamic",plugin_name="streaming_media")
                    await bot.send(event, "取消订阅成功")
                else:
                    await bot.send(event, "你没有订阅过")
            else:
                await bot.send(event, "不存在订阅任务")
async def trigger_tasks(bot,event,config,task_name):
    if task_name=="nasa_daily":
        bot.logger.info_func("获取今日nasa天文信息推送")
        img, text = await get_nasa_apod(config.basic_plugin.config["nasa_api"]["api_key"], config.common_config.basic_config["proxy"]["http_proxy"])
        return {"将下列文本翻译后发送": text, "要发送的图片": img}
    elif task_name=="单向历":
        bot.logger.info_func("获取单向历推送")
        path = await danxianglii()
        await bot.send(event, Image(file=path))
