import re
from concurrent.futures import ThreadPoolExecutor

import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import File, Image, Video
from plugins.core.userDB import get_user
from plugins.resource_search_plugin.asmr.asmr import get_audio
from plugins.streaming_media_service.Link_parsing.Link_parsing import link_prising, download_video_link_prising
from plugins.streaming_media_service.youtube.youtube_tools import get_img, audio_download, video_download


async def download_video(bot,event,config,url,type="audio",platform="youtube"):
    if platform == "youtube":
        loop = asyncio.get_running_loop()
        regex = r"(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})"

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
    elif platform == "bilibili":
        proxy = config.api["proxy"]["http_proxy"]
        link_prising_json = await link_prising(url, filepath='data/pictures/cache/',proxy=proxy)
        #print(link_prising_json)
        if link_prising_json['status']:
            bot.logger.info('链接解析成功，开始推送~~')
            if link_prising_json['video_url']:
                if "QQ小程序" in url and config.settings["bili_dynamic"]["is_QQ_chek"] is not True:
                    return {"status": False, "reason": "QQ小程序动态暂不支持下载"}
            if link_prising_json['soft_type'] not in {'bilibili', 'dy', 'wb', 'xhs', 'x'}:
                await bot.send(event, '该类型视频暂未提供下载支持，敬请期待')
                return
            try:
                video_json = await download_video_link_prising(link_prising_json, filepath='data/pictures/cache/', proxy=proxy)
                if 'video' in video_json['type']:
                    await bot.send(event, Video(file=video_json['video_path']))
                    return {"status": True, "reason": "下载成功，视频已发送。"}
                elif video_json['type'] == 'file':
                    await bot.send(event, File(file=video_json['video_path']))
                    return {"status": True, "reason": "下载成功，文件已发送。"}
                elif video_json['type'] == 'too_big':
                    return {"status": False, "reason": "文件过大"}
            except Exception as e:
                await bot.send(event, f'下载失败\n{e}')
                return {"status": False, "reason": str(e)}
        else:
            if link_prising_json['reason']:
                bot.logger.error(str('bili_link_error ') + link_prising_json['reason'])
                return {"status": False, "reason": link_prising_json['reason']}
def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def dl_youtube_audio(event):
        if event.raw_message.startswith("/yt音频"):
            url = event.raw_message.split("/yt音频")[1]
            await download_video(bot,event,config,url)
        elif event.raw_message.startswith("/yt视频"):
            url = event.raw_message.split("/yt视频")[1]
            await download_video(bot,event,config,url,type="video")