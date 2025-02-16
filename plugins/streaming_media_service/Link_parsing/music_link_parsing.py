
import re
import copy

import os
import inspect

from plugins.streaming_media_service.Link_parsing.core.cloud_music_draw import draw_netease_music_card
from plugins.streaming_media_service.Link_parsing.core.netease_music import fetch_song_info, download_image

json_init = {
    "status": False,
    "content": {},
    "reason": {},
    "pic_path": {},
    "url": {},
    "video_url": False,  # 对于纯音乐链接，这个应该是 False
    "soft_type": "netease_music",
}
filepath_init = (
    f"{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(fetch_song_info))))}/data/cache/"
)
if not os.path.exists(filepath_init):
    os.makedirs(filepath_init)

async def netease_music_link_parse(url, filepath=None):
    """
    解析网易云音乐链接，生成预览图。
    """
    if filepath is None:
        filepath = filepath_init

    json_check = copy.deepcopy(json_init)
    json_check["status"] = True
    json_check["url"] = url
    #识别链接（使用正则表达式）
    song_id = None
    #更新后的正则表达式，可以匹配两种格式的链接
    if match := re.search(r"music\.163\.com/(?:#\/)?.*?song.*?(?:\?id=|/)(?P<id>\d+)", url):
        song_id = match.group("id")
    if not song_id:
        json_check["status"] = False
        json_check["reason"] = "无法识别的网易云音乐链接"
        return json_check
    #调用netease_music.py中的函数获取歌曲信息
    try:
        song_info = await fetch_song_info(song_id)
        if not song_info:
            raise Exception("无法获取歌曲信息")
    except Exception as e:
        json_check["status"] = False
        json_check["reason"] = str(e)
        return json_check

    #下载歌曲封面图
    try:
        cover_path = await download_image(song_info["cover_url"], filepath)
    except Exception as e:
        json_check["status"] = False
        json_check["reason"] = f"封面下载失败: {e}"
        return json_check

    #准备绘图数据
    draw_data = {
        "cover_path": cover_path,
        "song_name": song_info["name"],
        "artist_name": " / ".join(song_info["artists"]),
        "album_name": song_info["album"],
        "song_type": song_info.get("song_type", ""),  #新增歌曲类型
        "bpm": song_info.get("bpm", ""),  #新增BPM
    }

    #调用绘图函数生成预览图
    try:
        out_path = draw_netease_music_card(draw_data, filepath=filepath,song_id=song_id)
        json_check["pic_path"] = out_path
    except Exception as e:
        json_check["status"] = False
        json_check["reason"] = f"绘图失败: {e}"
        return json_check
    return json_check
