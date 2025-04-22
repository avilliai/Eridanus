import re
from concurrent.futures import ThreadPoolExecutor

import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import File, Image, Video, Node, Text
from framework_common.database_util.User import get_user
from run.resource_collector.service.asmr.asmr100 import parse_from_asmr_id
from run.streaming_media.service.Link_parsing.Link_parsing import link_prising, download_video_link_prising
from run.streaming_media.service.youtube.youtube_tools import get_img, audio_download, video_download
from framework_common.utils.random_str import random_str
from framework_common.utils.utils import download_img, download_file, merge_audio_files


async def download_video(bot,event,config,url,type="audio",platform="youtube"):
    async def _download_video():
        if platform == "youtube":
            loop = asyncio.get_running_loop()
            regex = r"(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})"

            match1 = re.search(regex, url)
            user_info = await get_user(event.user_id)
            if match1:
                bot.logger.info(f"Video ID from url1: {match1.group(1)}")
                if type == "audio":

                    if user_info.permission < config.streaming_media.config["流媒体"]["youtube"]["download_audio_level"]:
                        await bot.send(event,"您的权限不足，无法下载音频")
                        return
                    await bot.send(event,"正在下载音频，请稍后...")
                    video_id = match1.group(1)
                    imgurl = await get_img(video_id)
                    with ThreadPoolExecutor() as executor:
                        path = await loop.run_in_executor(executor,audio_download , video_id)
                    await bot.send(event,[Image(file=imgurl)],True)
                elif type == "video":
                    if user_info.permission < config.streaming_media.config["流媒体"]["youtube"]["download_video_level"]:
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
            proxy = config.common_config.basic_config["proxy"]["http_proxy"]
            link_prising_json = await link_prising(url, filepath='data/pictures/cache/',proxy=proxy)
            #print(link_prising_json)
            if link_prising_json['status']:
                bot.logger.info('链接解析成功，开始推送~~')
                if link_prising_json['video_url']:
                    if "QQ小程序" in url and config.streaming_media.config["bili_dynamic"]["is_QQ_chek"] is not True:
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
        elif platform == "asmr100":
            user_info = await get_user(event.user_id)
            if user_info.permission < config.streaming_media.config["流媒体"]["asmr"]["download_audio_level"]:
                await bot.send(event, "您的权限不足，无法下载音频")
                return
            match = re.search(r"RJ(\d+)", url)
            if match:
                bot.logger.info(f"Asmr ID from url1: {match.group(1)}")
                proxy = config.common_config.basic_config["proxy"]["http_proxy"]
                r=await parse_from_asmr_id(match.group(1), proxy=proxy)
                bot.logger.info(f"Asmr titile:{r['title']}  nsfw:{r['nsfw']}  source_url:{r['source_url']}")
                try:
                    img=await download_img(r['mainCoverUrl'],f"data/pictures/cache/{random_str()}.png",config.resource_collector.config["asmr"]["gray_layer"],proxy=config.common_config.basic_config["proxy"]["http_proxy"])
                except Exception as e:
                    bot.logger.error(f"download_img error:{e}")
                    img=r['mainCoverUrl']
                forward_list = []

                forward_list.append(Node(content=[Text(f"随机asmr\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"), Image(file=img)]))

                file_paths=[]
                main_path = f"data/voice/cache/{r['title']}.{r['media_urls'][0][1].split('.')[-1]}"
                metype=r['media_urls'][0][1].split('.')[-1]
                for i in r['media_urls']:
                    if i[1].split('.')[-1]!= metype or len(file_paths)>=config.resource_collector.config["asmr"]["max_merge_file_num"]:
                        bot.logger.error(f"audio type change:{i[1]}")
                        break
                    path=f"data/voice/cache/{i[1]}"
                    file=await download_file(i[0],path,config.common_config.basic_config["proxy"]["http_proxy"])
                    file_paths.append(file)
                    bot.logger.info(f"download_file success:{file}")

                await bot.send(event, forward_list)

                loop = asyncio.get_running_loop()
                try:
                    await bot.send(event, "正在合并音频文件，请等待完成...")
                    bot.logger.info(f"asmr file merge and upload start: path:{main_path},merge_files:{file_paths}")
                    with ThreadPoolExecutor() as executor:
                        path = await loop.run_in_executor(executor, merge_audio_files, file_paths, main_path)
                    await bot.send(event, File(file=path))
                except Exception as e:
                    bot.logger.error(f"asmr file merge and upload error:{e}")
    asyncio.create_task(_download_video())
    return {"status": "running", "message": "任务已在后台启动，请耐心等待结果"}
def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def dl_youtube_audio(event):
        if event.pure_text.startswith("/yt音频"):
            url = event.pure_text.split("/yt音频")[1]
            await download_video(bot,event,config,url)
        elif event.pure_text.startswith("/yt视频"):
            url = event.pure_text.split("/yt视频")[1]
            await download_video(bot,event,config,url,type="video")