from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text, File
from plugins.resource_search_plugin.iwara.iwara1 import download_specific_video, search_videos, rank_videos, fetch_video_info
from plugins.utils.random_str import random_str
from plugins.core.userDB import get_user

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def search_image(event):
        if str(event.pure_text).startswith("iwara下载"):
            if not user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_download_level"]:
                return
            videoid = str(event.pure_text).replace("iwara下载", "")
            await bot.send(event, Text(f"正在下载iwara视频{videoid}"))
            try:
                list = await download_specific_video(videoid,config)
                msg = [Node(content=[Text(list.get('title')),Text("\nvideo_id:"), Text(list.get('video_id'))]),Node(content=[File(file=list.get('path'))])]
                await bot.send(event, msg)
            except Exception as e:
                await bot.send(event, Text(f"iwara视频{videoid}下载失败：{e}"))
        elif str(event.pure_text).startswith("iwara搜"):
            user_info = await get_user(event.user_id)
            if not user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
                return
            word = str(event.pure_text).replace("iwara搜", "")
            await bot.send(event, Text(f"正在iwara搜索{word}"))
            try:
                list = await search_videos(word,config)
                if len(list) == 0:
                    await bot.send(event, Text(f"未搜索到{word}相关iwara视频"))
                    return
                node_list = [
                    Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                    for i in list
                ]
                await bot.send(event, node_list)
            except Exception as e:
                await bot.send(event, Text(f"iwara搜索{word}失败：{e}"))
        elif str(event.pure_text).startswith("iwara最新"):
            user_info = await get_user(event.user_id)
            if not user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
                return
            await bot.send(event, Text(f"正在获取iwara最新视频"))
            try:
                list = await fetch_video_info('date',config)
                if len(list) == 0:
                    await bot.send(event, Text(f"未获取到iwara最新视频"))
                    return
                node_list = [
                    Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                    for i in list
                ]
                await bot.send(event, node_list)
            except Exception as e:
                await bot.send(event, Text(f"iwara最新获取失败：{e}"))
        elif str(event.pure_text).startswith("iwara趋势"):
            user_info = await get_user(event.user_id)
            if not user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
                return
            await bot.send(event, Text(f"正在获取iwara趋势视频"))
            try:
                list = await fetch_video_info('trending',config)
                if len(list) == 0:
                    await bot.send(event, Text(f"未获取到iwara趋势视频"))
                    return
                node_list = [
                    Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                    for i in list
                ]
                await bot.send(event, node_list)
            except Exception as e:
                await bot.send(event, Text(f"iwara趋势获取失败：{e}"))
        elif str(event.pure_text).startswith("iwara热门"):
            user_info = await get_user(event.user_id)
            if not user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
                return
            await bot.send(event, Text(f"正在获取iwara热门视频"))
            try:
                list = await fetch_video_info('popularity',config)
                if len(list) == 0:
                    await bot.send(event, Text(f"未获取到iwara热门视频"))
                    return
                node_list = [
                    Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                    for i in list
                ]
                await bot.send(event, node_list)
            except Exception as e:
                await bot.send(event, Text(f"iwara热门获取失败：{e}"))
        elif str(event.pure_text).startswith("iwara"):
            await bot.send(event, "无权限或指令无效")
