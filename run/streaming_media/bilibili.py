import asyncio

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.streaming_media_service.bilibili.bili import fetch_latest_dynamic_id, fetch_dynamic
async def bili_subscribe(bot,event,config,target_uid: int,operation):

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
async def check_bili_dynamic(bot,config):
    bot.logger.info_func("开始检查 B 站动态更新")
    for target_uid in config.bili_dynamic:
        latest_dynamic_id=await fetch_latest_dynamic_id(int(target_uid))
        if latest_dynamic_id!=config.bili_dynamic[target_uid]["latest_dynamic_id"]:
            bot.logger.info_func(f"发现新的动态 群号：{config.bili_dynamic[target_uid]['push_groups']} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
            groups=config.bili_dynamic[target_uid]["push_groups"]
            dynamic = await fetch_dynamic(latest_dynamic_id)

            for group_id in groups:
                bot.logger.info_func(f"推送动态 群号：{groups} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
                try:
                    await bot.send_group_message(group_id,Image(file=dynamic))
                except:
                    bot.logger.error_func(f"推送动态失败 群号：{group_id} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
            config.bili_dynamic[target_uid]["latest_dynamic_id"]=latest_dynamic_id
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
            dynamic_id=await fetch_latest_dynamic_id(target_id)
            bot.logger.info(f"Dynamic id of {target_id} is {dynamic_id}")
            p=await fetch_dynamic(dynamic_id)
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
        elif event.raw_message.startswith("/bili remove "):
            target_id = event.raw_message.split("/bili remove ")[1] #注意是str
            try:
                target_id = int(target_id)
            except ValueError:
                await bot.send(event, "无效的uid")
                return
            bot.logger.info_func(f"取消动态关注 群号：{event.group_id} 关注id: {target_id}")

