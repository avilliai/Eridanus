import asyncio
from asyncio import sleep

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.streaming_media_service.bilibili.bili import fetch_latest_dynamic_id, fetch_dynamic, fetch_latest_dynamic
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from plugins.resource_search_plugin.Link_parsing.Link_parsing import bilibili

async def bili_subscribe(bot,event,config,target_uid: int,operation):
    if not isinstance(event,GroupMessageEvent):
        await bot.send(event,"订阅功能仅支持群聊")   #私聊主动群发消息容易被腾子shutdown
        return
    if operation=="add":
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
            latest_dynamic_id1, latest_dynamic_id2 = await fetch_latest_dynamic_id(int(target_uid))
            config.bili_dynamic[target_uid] = {"push_groups": [event.group_id], "latest_dynamic_id": [latest_dynamic_id1, latest_dynamic_id2]}
            config.save_yaml(str("bili_dynamic"))
            await bot.send(event, "订阅成功")
        try:
            p=await fetch_latest_dynamic(target_uid,config)
            await bot.send(event,Image(file=p))
        except:
            bot.logger.error(f"获取动态失败 群号：{event.group_id} 关注id: {target_uid}")
    elif operation=="remove":
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
async def check_bili_dynamic(bot,config):
    bot.logger.info_func("开始检查 B 站动态更新")
    bilibili_type_draw = config.settings["bili_dynamic"]["draw_type"]
    for target_uid in config.bili_dynamic:
        latest_dynamic_id1,latest_dynamic_id2=await fetch_latest_dynamic_id(int(target_uid))
        if latest_dynamic_id1!=config.bili_dynamic[target_uid]["latest_dynamic_id"][0] or latest_dynamic_id2!=config.bili_dynamic[target_uid]["latest_dynamic_id"][1]:
            if latest_dynamic_id1!=config.bili_dynamic[target_uid]["latest_dynamic_id"][0]:
                latest_dynamic_id=latest_dynamic_id1
            else:
                latest_dynamic_id=latest_dynamic_id2

            bot.logger.info_func(f"发现新的动态 群号：{config.bili_dynamic[target_uid]['push_groups']} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
            groups=config.bili_dynamic[target_uid]["push_groups"]
            try:
                if bilibili_type_draw == 1:
                    dynamic = await fetch_dynamic(latest_dynamic_id,config.settings["bili_dynamic"]["screen_shot_mode"])
                elif bilibili_type_draw == 2:
                    await bilibili(f'https://t.bilibili.com/{latest_dynamic_id}',
                                   filepath='plugins/resource_search_plugin/Link_parsing/data/')
                    dynamic = f'plugins/resource_search_plugin/Link_parsing/data/result.png'
            except Exception as e:
                bot.logger.error(f"动态获取失败 群号：{group_id} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")

            for group_id in groups:
                bot.logger.info_func(f"推送动态 群号：{groups} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
                try:
                    await bot.send_group_message(group_id,Image(file=dynamic))
                except:
                    bot.logger.error(f"推送动态失败 群号：{group_id} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
            config.bili_dynamic[target_uid]["latest_dynamic_id"]=[latest_dynamic_id1,latest_dynamic_id2]
            config.save_yaml("bili_dynamic")
    bot.logger.info_func("完成 B 站动态更新检查")

def main(bot,config):

    @bot.on(LifecycleMetaEvent)
    async def _(event):
        while True:
            await check_bili_dynamic(bot,config)
            await asyncio.sleep(300)  # 每 5 分钟检查一次
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.raw_message.startswith("看看动态"):
            target_id = event.raw_message.split("看看动态")[1]
            bot.logger.info(f"Fetching dynamic id of {target_id}")
            dynamic_id1,dynamic_id2=await fetch_latest_dynamic_id(target_id)
            bot.logger.info(f"Dynamic id of {target_id} is {dynamic_id1} {dynamic_id2}")
            p=await fetch_dynamic(dynamic_id1,config.settings["bili_dynamic"]["screen_shot_mode"])
            await bot.send(event,Image(file=p))
            p=await fetch_dynamic(dynamic_id2,config.settings["bili_dynamic"]["screen_shot_mode"])
            await bot.send(event,Image(file=p))
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.raw_message.startswith("/bili add "):
            target_id = event.raw_message.split("/bili add ")[1] #注意是str
            try:
                target_id = int(target_id)
            except ValueError:
                await bot.send(event, "无效的uid")
                return
            bot.logger.info_func(f"添加动态关注 群号：{event.group_id} 关注id: {target_id}")
            await bili_subscribe(bot,event,config,int(target_id),"add")
        elif event.raw_message.startswith("/bili remove "):
            target_id = event.raw_message.split("/bili remove ")[1] #注意是str
            try:
                target_id = int(target_id)
            except ValueError:
                await bot.send(event, "无效的uid")
                return
            bot.logger.info_func(f"取消动态关注 群号：{event.group_id} 关注id: {target_id}")
            await bili_subscribe(bot,event,config,int(target_id),"remove")

