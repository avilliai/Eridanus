import re
from concurrent.futures import ThreadPoolExecutor

import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import File, Image
from plugins.core.userDB import get_user
from plugins.resource_search_plugin.asmr.asmr import get_audio
from plugins.streaming_media_service.youtube.youtube_tools import get_img, audio_download, video_download


async def download_youtube(bot,event,config,url,type="audio"):
    loop = asyncio.get_running_loop()
    regex = r"(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})"

    match1 = re.search(regex, url)
    user_info = await get_user(event.user_id, event.sender.nickname)
    if match1:
        bot.logger.info(f"Video ID from url1: {match1.group(1)}")
        if type == "audio":

            if user_info[6] < config.controller["流媒体"]["youtube"]["download_audio_level"]:
                await bot.send(event,"您的权限不足，无法下载音频")
                return
            await bot.send(event,"正在下载音频，请稍后...")
            video_id = match1.group(1)
            imgurl = await get_img(video_id)
            with ThreadPoolExecutor() as executor:
                path = await loop.run_in_executor(executor,audio_download , video_id)
            await bot.send(event,[Image(file=imgurl)],True)
        elif type == "video":
            if user_info[6] < config.controller["流媒体"]["youtube"]["download_video_level"]:
                await bot.send(event,"您的权限不足，无法下载音频")
                return
            await bot.send(event,"正在下载视频，请稍后...")
            video_id = match1.group(1)
            with ThreadPoolExecutor() as executor:
                path = await loop.run_in_executor(executor,video_download , video_id)
        await bot.send(event,File(file=path))
    else:
        await bot.send(event,"Invalid URL")

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def dl_youtube_audio(event):
        if event.raw_message.startswith("/yt音频"):
            url = event.raw_message.split("/yt音频")[1]
            await download_youtube(bot,event,config,url)
        elif event.raw_message.startswith("/yt视频"):
            url = event.raw_message.split("/yt视频")[1]
            await download_youtube(bot,event,config,url,type="video")