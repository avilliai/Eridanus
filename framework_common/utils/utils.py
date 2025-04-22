import base64
import random

import asyncio
import httpx
import base64

import re
from io import BytesIO

from PIL import Image

async def delay_recall(bot, msg, interval=20):
    """
    延迟撤回消息的非阻塞封装函数，撤回机器人自身消息可以先msg = await bot.send(event, 'xxx')然后调用await delay_recall(bot, msg, 20)这样来不阻塞的撤回，默认20秒后撤回
    
    参数:
        bot
        msg: 消息
        interval: 延迟时间（秒）
    """
    async def recall_task():
        await asyncio.sleep(interval)
        await bot.recall(msg['data']['message_id'])

    asyncio.create_task(recall_task())

async def get_img(processed_message, bot, event):
    """
    获取消息中或者引用消息中的图片url，如果没有找到返回False
    """
    for item in processed_message:
        if "image" in item or "mface" in item:
            try:
                if "mface" in item:
                    url = item["mface"]["url"]
                else:
                    url = item["image"]["url"]
                return url
            except Exception as e:
                bot.logger.warning(f"获取图片失败: {e}")
                return False
        elif "reply" in item:
            try:
                event_obj = await bot.get_msg(int(event.get("reply")[0]["id"]))
                message = await get_img(event_obj.processed_message, bot, event)
                if message:
                    return message
            except Exception as e:
                bot.logger.warning(f"引用消息解析失败: {e}")
                return False
    return False

async def url_to_base64(url):
    async with httpx.AsyncClient(timeout=9000) as client:
        response = await client.get(url)
        if response.status_code == 200:
            image_bytes = response.content
            encoded_string = base64.b64encode(image_bytes).decode('utf-8')
            return encoded_string
        else:
            raise Exception(f"Failed to retrieve image: {response.status_code}")

def parse_arguments(arg_string, original_dict):
    args = arg_string.split()
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--') and len(arg) > 2:
            key = arg[2:]
            value_parts = []
            j = i + 1
            while j < len(args) and not args[j].startswith('--'):
                value_parts.append(args[j])
                j += 1
            if value_parts:
                value = ' '.join(value_parts)
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                original_dict[key] = value
                i = j - 1
            else:
                if key in original_dict:
                    del original_dict[key]
        i += 1
    return original_dict

async def download_img(url,path,gray_layer=False,proxy=None):
    if url.startswith("data:image"):
        match = re.match(r"data:image/(.*?);base64,(.+)", url)
        if not match:
            raise ValueError("Invalid Data URI format")

        img_type, base64_data = match.groups()
        img_data = base64.b64decode(base64_data)  # 解码 Base64 数据

        # 保存图片文件
        with open(path, "wb") as f:
            f.write(img_data)
        return path
    if proxy is not None and proxy!= '':
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url)
        if gray_layer:
            img = Image.open(BytesIO(response.content))  # 从二进制数据创建图片对象
            image_raw = img
            image_black_white = image_raw.convert('1')
            image_black_white.save(path)
        else:
            with open(path, 'wb') as f:
                f.write(response.content)
        return path
async def download_file(url,path,proxy=None):
    if proxy is not None and proxy!= '':
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    async with httpx.AsyncClient(proxies=proxies,timeout=None) as client:
        response = await client.get(url)
        with open(path, 'wb') as f:
            f.write(response.content)
        return path

from pydub import AudioSegment
def merge_audio_files(audio_files: list, output_file: str) -> str:
    """
    合并音频文件列表并保存为一个文件，支持 MP3、FLAC、WAV 等格式。

    :param audio_files: 音频文件路径列表（支持 wav, mp3, flac 等格式）。
    :param output_file: 输出的合并音频文件路径。
    :return: 输出文件路径。
    """
    if not audio_files:
        raise ValueError("音频文件列表不能为空。")

    combined = AudioSegment.empty()

    for file in audio_files:
        audio = AudioSegment.from_file(file)
        combined += audio

    file_format = output_file.split('.')[-1].lower()
    if file_format not in ['mp3', 'wav', 'flac']:
        raise ValueError(f"不支持的输出格式：{file_format}")

    combined.export(output_file, format=file_format)
    return output_file





def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers


