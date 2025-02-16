import httpx
import re
from PIL import Image, ImageFilter
from io import BytesIO

# 常用的请求头
NETEASE_MUSIC_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://music.163.com/",
}

NEW_SONG_DETAIL_API = "https://api.paugram.com/netease/?id={}"

async def fetch_song_info(song_id):
    """
    根据歌曲 ID 获取歌曲信息（使用新的 API）。
    """
    async with httpx.AsyncClient(headers=NETEASE_MUSIC_HEADERS) as client:
        response = await client.get(NEW_SONG_DETAIL_API.format(song_id))

        if response.status_code != 200:
            print(f"API 请求失败，状态码：{response.status_code}")
            print(f"响应内容：{response.text}")
            return None

        response_json = response.json()

        if "id" not in response_json:
            print("API 返回数据格式错误")
            return None

        return {
            "name": response_json["title"],
            "artists": [response_json["artist"]],
            "album": response_json["album"],
            "cover_url": response_json["cover"],
            "song_type": get_song_type(response_json),  #从歌词中猜测类型
            "bpm": get_bpm(response_json),
        }
async def download_image(url: str, path: str = "") -> str:
    """
    下载网络图片并进行处理
    如果未指定path，则图片将保存在当前工作目录并以图片的文件名命名。
    如果提供了代理地址，则会通过该代理下载图片。
    :param url: 要下载的图片的URL。
    :param path: 图片保存的路径。如果为空，则保存在当前目录。
    :return: 保存图片的路径。
    """
    def crop_center_square(image):
        width, height = image.size
        min_edge = min(width, height)
        left = (width - min_edge) // 2
        top = (height - min_edge) // 2
        right = left + min_edge
        bottom = top + min_edge
        return image.crop((left, top, right, bottom))
    file_name = re.sub(r"[:/]", "_", url.split('/').pop().split('?')[0])
    path = f"{path}{file_name}"
    async with httpx.AsyncClient(headers=NETEASE_MUSIC_HEADERS) as client:
        response = await client.get(url)
        if response.status_code == 200:
            square_image = crop_center_square(Image.open(BytesIO(response.content)))
            if square_image.mode != "RGB":
                square_image = square_image.convert("RGB")
            square_image.save(path)
            return path
def get_song_type(song_data):
    """
    根据歌曲信息猜测歌曲类型（还没写）。
    """
    if "lyric" not in song_data:
        return ""

    lyric = song_data["lyric"].lower()
    if "纯音乐" in lyric or "instrumental" in lyric:
        return "纯音乐"
    elif "原声带" in song_data["album"].lower() or "ost" in song_data["album"].lower():
        return "原声带"
    return ""
def get_bpm(song_data):
    """
    尝试获取歌曲的 BPM（还没写）。
    """
    return ""