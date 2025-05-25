import httpx
import random

import yaml
from pytubefix import Channel, YouTube
from ruamel.yaml import YAML

from developTools.utils.logger import get_logger
from framework_common.framework_util.yamlLoader import YAMLManager
from framework_common.utils.utils import get_headers


yaml_manager = YAMLManager.get_instance()

local_config = yaml_manager.common_config.basic_config
try:
    proxy = local_config.get("proxy").get("http_proxy")
except:
    proxy = None
if not proxy:
    proxy=None

proxies = {
    "http://": proxy,
    "https://": proxy
}
pyproxies = {  # pytubefix代理
    "http": proxy,
    "https": proxy
}




ASMR_channels =yaml_manager.resource_collector.config["asmr"]["channels"]

logger=get_logger()
async def ASMR_today():
    global ASMR_channels  # ASMR频道列表
    global pushed_videos  # 已推送ASMR列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}', proxies=pyproxies)
    athor = c.channel_name

    video_idlist = [video_url.video_id for video_url in c.video_urls]  # 获取该频道所有ASMR视频id
    try:
        video_id = next(video_id for video_id in video_idlist if video_id not in pushed_videos)  # 过滤已推送ASMR,不改变时间排序
        pushed_videos.append(video_id)
        ASMRpush["已推送ASMR"] = pushed_videos
        with open('data/ASMR.yaml', 'w', encoding="utf-8") as file:
            yaml.dump(ASMRpush, file, allow_unicode=True)
    except:
        print(f"{athor}频道没有未推送的ASMR,从投稿中随机选择")  # 如果没有未推送的ASMR,从该频道投稿中随机选择
        video_id = random.choice(c.video_urls).video_id
    url = 'https://www.youtube.com/watch?v=' + video_id
    yt = YouTube(url)
    title = yt.title
    length = yt.length
    return athor, title, video_id, length


def ASMR_random():
    global ASMR_channels  # ASMR频道列表
    channel = random.choice(ASMR_channels)
    c = Channel(url=f'https://www.youtube.com/{channel}', proxies=pyproxies)
    athor = c.channel_name
    video_id = str(random.choice(c.video_urls)).split('=')[1].replace('>', '')  # 从该频道投稿中随机选择
    url = 'https://www.youtube.com/watch?v=' + video_id
    yt = YouTube(url, proxies=pyproxies)
    title = yt.title
    length = yt.length
    logger.info(f"选择{athor}频道的ASMR:{title}")
    return athor, title, video_id, length


def get_audio(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    #
    yt = YouTube(url=url, client='IOS', proxies=pyproxies,use_oauth=True, allow_oauth_cache=True)

    ys = yt.streams.get_audio_only()
    ys.download(output_path="data/voice/cache/", filename=f"{video_id}.mp3")


    return f"data/voice/cache/{video_id}.mp3"


async def get_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url=url, proxies=pyproxies)
    title = yt.title

    url = f"https://ripyoutube.com/mates/en/convert?id={video_id}"  # 从ripyoutube获取视频下载地址
    data = {
        'platform': 'youtube',
        'url': f'https://www.youtube.com/watch?v={video_id}',
        'title': title,
        'id': 'iCMgE7C1JltWuflTeD0TJn==',
        'ext': 'mp4',
        'note': '1080p',
        'format': 137
    }
    async with httpx.AsyncClient(headers=get_headers(), proxies=proxies, timeout=100) as client:
        response = await client.post(url=url, data=data)
    videourl = response.json()['downloadUrlX']
    return videourl


async def get_img(video_id):
    path = f"data/pictures/cache/{video_id}.jpg"
    url = f"https://i.ytimg.com/vi/{video_id}/hq720.jpg"  # 下载视频封面
    async with httpx.AsyncClient(headers=get_headers(), proxies=proxies, timeout=100) as client:
        response = await client.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    return path




'''athor, title, video_id, length = asyncio.run(ASMR_random())
imgurl =asyncio.run(get_img(video_id))
print(imgurl)
audiourl =asyncio.run(get_audio(video_id))
print(audiourl)
print(f"标题:{title}\n频道:{athor}\n视频id:{video_id}\n视频时长:{length}\n视频封面:{imgurl}\n音频:{audiourl}")'''