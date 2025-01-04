import re
from concurrent.futures import ThreadPoolExecutor

import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import File, Image
from plugins.resource_search_plugin.asmr.asmr import get_audio
from plugins.streamingMedia_Subscribe_plugin.youtube.youtube_tools import get_img, audio_download, video_download


async def download_youtube(bot,event,config,url,type="audio"):
    loop = asyncio.get_running_loop()
    regex = r"(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})"

    match1 = re.search(regex, url)

    if match1:
        bot.logger.info(f"Video ID from url1: {match1.group(1)}")
        if type == "audio":
            await bot.send(event,"正在下载音频，请稍后...")
            video_id = match1.group(1)
            imgurl = await get_img(video_id)
            with ThreadPoolExecutor() as executor:
                path = await loop.run_in_executor(executor,audio_download , video_id)
            await bot.send(event,[Image(file=imgurl)],True)
        elif type == "video":
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