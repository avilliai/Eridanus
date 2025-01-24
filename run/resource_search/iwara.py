from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text, File
from plugins.resource_search_plugin.iwara.iwara1 import download_specific_video, search_videos, rank_videos, fetch_video_info
from plugins.utils.random_str import random_str
from plugins.core.userDB import get_user

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def search_image(event):
        user_info = await get_user(event.user_id, event.sender.nickname)
        if str(event.raw_message).startswith("iwara下载") and user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_download_level"]:
            videoid = str(event.raw_message).replace("iwara下载", "")
            list = await download_specific_video(videoid,config)
            msg = [Node(content=[Text(list.get('title')),Text("\nvideo_id:"), Text(list.get('video_id'))]),Node(content=[File(file=list.get('path'))])]
            await bot.send(event, msg)
        elif str(event.raw_message).startswith("iwara搜") and user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
            word = str(event.raw_message).replace("iwara搜", "")
            list = await search_videos(word,config)
            node_list = [
                Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        elif str(event.raw_message).startswith("iwara最新") and user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
            videoid = str(event.raw_message).replace("iwara最新", "")
            list = await fetch_video_info('date',config)
            node_list = [
                Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        elif str(event.raw_message).startswith("iwara趋势") and user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
            videoid = str(event.raw_message).replace("iwara趋势", "")
            list = await fetch_video_info('trending',config)
            node_list = [
                Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        elif str(event.raw_message).startswith("iwara热门") and user_info[6] >= config.controller["resource_search"]["iwara"]["iwara_search_level"]:
            videoid = str(event.raw_message).replace("iwara热门", "")
            list = await fetch_video_info('popularity',config)
            node_list = [
                Node(content=[Text(i.get('title')),Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        elif str(event.raw_message).startswith("iwara热门") or str(event.raw_message).startswith("iwara趋势") or str(event.raw_message).startswith("iwara最新") or str(event.raw_message).startswith("iwara搜") or str(event.raw_message).startswith("iwara下载"):
            await bot.send(event, "无权限或指令无效")