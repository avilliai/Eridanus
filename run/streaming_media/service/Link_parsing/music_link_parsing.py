import re
import copy
import os
import inspect

from run.streaming_media.service.Link_parsing.core.cloud_music_draw import draw_netease_music_card
from run.streaming_media.service.Link_parsing.core.netease_music import fetch_song_info, download_image

json_init = {
    "status": False,
    "content": {},
    "reason": {},
    "pic_path": {},
    "url": {},
    "video_url": False,  #可以保留，或者根据需要改名
    "soft_type": "",
    "url_file_path": None,  #下载链接文件路径
}
filepath_init = (
    f"{os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(fetch_song_info))))}/data/cache/"
)
if not os.path.exists(filepath_init):
    os.makedirs(filepath_init)


async def netease_music_link_parse(url, filepath=None):
    if filepath is None:
        filepath = filepath_init

    json_check = copy.deepcopy(json_init)
    json_check["url"] = url

    song_id = None

    if match := re.search(r"music\.163\.com/(?:#\/)?.*?song.*?(?:\?id=|/)(?P<id>\d+)", url):
        song_id = match.group("id")
        json_check["soft_type"] = "netease_music"
    else:
        json_check["status"] = False
        json_check["reason"] = "无法识别的网易云音乐链接"
        return json_check

    if song_id:
        #获取歌曲信息
        try:
            song_info = await fetch_song_info(song_id, filepath)
            if not song_info:
                raise Exception("无法获取歌曲信息")
        except Exception as e:
            json_check["status"] = False
            json_check["reason"] = str(e)
            return json_check

        #下载封面图
        try:
            cover_path = await download_image(song_info["cover_url"], filepath)
        except Exception as e:
            json_check["status"] = False
            json_check["reason"] = f"封面下载失败: {e}"
            return json_check

        #绘图数据
        draw_data = {
            "cover_path": cover_path,
            "song_name": song_info["name"],
            "artist_name": " / ".join(song_info["artists"]),
            "song_type": song_info.get("song_type", ""),
        }

        #绘制图片
        try:
            out_path = draw_netease_music_card(draw_data, filepath=filepath, song_id=song_id)
            json_check["pic_path"] = out_path
        except Exception as e:
            json_check["status"] = False
            json_check["reason"] = f"绘图失败: {e}"
            return json_check

        #存储下载链接文件路径
        if song_info.get("url_file_path"):
            json_check["url_file_path"] = song_info["url_file_path"]

        json_check["status"] = True
        return json_check

    json_check["status"] = True
    return json_check
