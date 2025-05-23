import asyncio
import threading
from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor
from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from run.streaming_media.service.Link_parsing.Link_parsing import link_prising
from run.streaming_media.service.bilibili.bili import fetch_latest_dynamic_id, fetch_dynamic
import sys

from run.system_plugin.func_collection import operate_group_push_tasks

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())




async def check_bili_dynamic(bot,config):
    bot.logger.info_func("开始检查 B 站动态更新")

    async def check_single_uid(target_uid,bilibili_type_draw):

        try:
            latest_dynamic_id1,latest_dynamic_id2=await fetch_latest_dynamic_id(int(target_uid))
            dy_store = [config.streaming_media.bili_dynamic[target_uid]["latest_dynamic_id"][0],config.streaming_media.bili_dynamic[target_uid]["latest_dynamic_id"][1]]
            if latest_dynamic_id1 not in dy_store or latest_dynamic_id2 not in dy_store:
                if latest_dynamic_id1!=config.streaming_media.bili_dynamic[target_uid]["latest_dynamic_id"][0]:
                    latest_dynamic_id=latest_dynamic_id1
                else:
                    latest_dynamic_id=latest_dynamic_id2

                bot.logger.info_func(f"发现新的动态 群号：{config.streaming_media.bili_dynamic[target_uid]['push_groups']} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
                groups=config.streaming_media.bili_dynamic[target_uid]["push_groups"]
                try:
                    if bilibili_type_draw == 1:
                        try:
                            dynamic = await fetch_dynamic(latest_dynamic_id,config.streaming_media.config["bili_dynamic"]["screen_shot_mode"])
                        except:
                            bilibili_type_draw = 2
                    elif bilibili_type_draw == 2:
                        linking_prising_json=await link_prising(f'https://t.bilibili.com/{latest_dynamic_id}', filepath='data/pictures/cache/',type = 'dynamic_check')
                        if not linking_prising_json['status']:
                            config.streaming_media.bili_dynamic[target_uid]["latest_dynamic_id"] = [latest_dynamic_id1,latest_dynamic_id2]
                            config.save_yaml("bili_dynamic",plugin_name="streaming_media")

                        dynamic= linking_prising_json['pic_path']

                except Exception as e:
                    bot.logger.error(f"动态获取失败 ：{e} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")


                for group_id in groups:
                    bot.logger.info_func(f"推送动态 群号：{groups} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
                    try:
                        await bot.send_group_message(group_id,[Image(file=dynamic),f'\nhttps://t.bilibili.com/{latest_dynamic_id}'])
                    except:
                        bot.logger.error(f"推送动态失败 群号：{group_id} 关注id: {target_uid} 最新动态id: {latest_dynamic_id}")
                config.streaming_media.bili_dynamic[target_uid]["latest_dynamic_id"]=[latest_dynamic_id1,latest_dynamic_id2]
                config.save_yaml("bili_dynamic",plugin_name="streaming_media")
        except Exception as e:
            bot.logger.error(f"动态抓取失败{e} uid: {target_uid}")

    bilibili_type_draw = config.streaming_media.config["bili_dynamic"]["draw_type"]
    if config.streaming_media.config["bili_dynamic"]["并发模式"]:
        tasks = [check_single_uid(target_uid,bilibili_type_draw) for target_uid in config.streaming_media.bili_dynamic]
        await asyncio.gather(*tasks)
    else:
        for target_uid in config.streaming_media.bili_dynamic:
            await check_single_uid(target_uid,bilibili_type_draw)
            await sleep(30)
    bot.logger.info_func("完成 B 站动态更新检查")

def main(bot,config):
    threading.Thread(target=bili_main(bot,config), daemon=True).start()
def bili_main(bot,config):
    global bili_activate
    bili_activate=False
    @bot.on(LifecycleMetaEvent)
    async def _(event):
        global bili_activate
        if not bili_activate:
            bili_activate=True
            loop = asyncio.get_running_loop()
            while True:
                try:
                    with ThreadPoolExecutor() as executor:
                        pass
                        await loop.run_in_executor(executor, asyncio.run,check_bili_dynamic(bot,config))
                    #await check_bili_dynamic(bot,config)
                except Exception as e:
                    bot.logger.error(e)
                await asyncio.sleep(config.streaming_media.config["bili_dynamic"]["dynamic_interval"])  #哈哈
        else:
            bot.logger.info("B站动态更新检查已启动")

    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.pure_text.startswith("看看动态"):
            target_id = event.pure_text.split("看看动态")[1]
            bot.logger.info(f"Fetching dynamic id of {target_id}")
            dynamic_id1,dynamic_id2=await fetch_latest_dynamic_id(target_id)
            bot.logger.info(f"Dynamic id of {target_id} is {dynamic_id1} {dynamic_id2}")
            p=await fetch_dynamic(dynamic_id1,config.streaming_media.config["bili_dynamic"]["screen_shot_mode"])
            await bot.send(event,Image(file=p))
            p=await fetch_dynamic(dynamic_id2,config.streaming_media.config["bili_dynamic"]["screen_shot_mode"])
            await bot.send(event,Image(file=p))
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.pure_text.startswith("/bili add "):
            target_id = event.pure_text.split("/bili add ")[1] #注意是str
            try:
                target_id = int(target_id)
            except ValueError:
                await bot.send(event, "无效的uid")
                return
            bot.logger.info_func(f"添加动态关注 群号：{event.group_id} 关注id: {target_id}")
            await operate_group_push_tasks(bot,event,config,task_type="bilibili",operation=True,target_uid=int(target_id))
        elif event.pure_text.startswith("/bili remove "):
            target_id = event.pure_text.split("/bili remove ")[1] #注意是str
            try:
                target_id = int(target_id)
            except ValueError:
                await bot.send(event, "无效的uid")
                return
            bot.logger.info_func(f"取消动态关注 群号：{event.group_id} 关注id: {target_id}")
            await operate_group_push_tasks(bot,event,config,task_type="bilibili",operation=False,target_uid=int(target_id))

