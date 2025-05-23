import os
import asyncio
import os
import re
import sys
import time
from io import BytesIO
from typing import List, Dict
from urllib.parse import urlparse

import aiofiles
import httpx
import requests
from PIL import Image

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
"""
通用请求头
"""
COMMON_HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 '
                  'UBrowser/6.2.4098.3 Safari/537.36'
}
# 插件名字
PLUGIN_NAME = "nonebot-plugin-resolver"

GENERAL_REQ_LINK = "http://47.99.158.118/video-crack/v2/parse?content={}"
# 解析列表文件名
RESOLVE_SHUTDOWN_LIST_NAME = "resolver_shutdown_list"

async def download_video(url, proxy: str = None, ext_headers=None,filepath=None) -> str:
    """
    异步下载（httpx）视频，并支持通过代理下载。
    文件名将使用时间戳生成，以确保唯一性。
    如果提供了代理地址，则会通过该代理下载视频。

    :param ext_headers:
    :param url: 要下载的视频的URL。
    :param proxy: 可选，下载视频时使用的代理服务器的URL。
    :return: 保存视频的路径。
    """
    # 使用时间戳生成文件名，确保唯一性
    #path = os.path.join(os.getcwd(), f"{int(time.time())}.mp4")
    path=filepath+f"{int(time.time())}.mp4"
    print(f"下载视频路径:{path}")
    # 判断 ext_headers 是否为 None
    if ext_headers is None:
        headers = COMMON_HEADER
    else:
        # 使用 update 方法合并两个字典
        headers = COMMON_HEADER.copy()  # 先复制 COMMON_HEADER
        headers.update(ext_headers)  # 然后更新 ext_headers

    # 配置代理
    client_config = {
        'headers': headers,
        'timeout': httpx.Timeout(60, connect=5.0),
        'follow_redirects': True
    }
    if proxy:
        client_config['proxies'] = { 'https': proxy }

    # 下载文件
    try:
        async with httpx.AsyncClient(**client_config) as client:
            async with client.stream("GET", url) as resp:
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in resp.aiter_bytes():
                        await f.write(chunk)
        return path
    except Exception as e:
        print(f"下载视频错误原因是: {e}")
        return None

async def add_append_img(contents,links_path):
    for link in links_path:
        if link not in {' '}:
            contents.append(link)
    return contents



async def download_img(url: str, path: str = '', proxy: str = None, session=None, headers=None,len=None) -> str:
    """
    异步下载（aiohttp）网络图片，并支持通过代理下载。
    如果未指定path，则图片将保存在当前工作目录并以图片的文件名命名。
    如果提供了代理地址，则会通过该代理下载图片。

    :param url: 要下载的图片的URL。
    :param path: 图片保存的路径。如果为空，则保存在当前目录。
    :param proxy: 可选，下载图片时使用的代理服务器的URL。
    :return: 保存图片的路径。
    """
    if headers is None:
        headers = COMMON_HEADER
    def crop_center_square(image):
        width, height = image.size
        min_edge = min(width, height)
        left = (width - min_edge) // 2
        top = (height - min_edge) // 2
        right = left + min_edge
        bottom = top + min_edge
        return image.crop((left, top, right, bottom))
    file_name=re.sub(r'[:]', '_', url.split('/').pop().split('?')[0])
    path=f'{path}{file_name}'
    if 'gif' in path:
        path=path.replace("gif", "jpg")
    #if not ('jpg' in path or 'png' in path or 'webp' in path or 'jpeg' in path):
    if not path.lower().endswith((".jpg", ".jpeg", ".png")):
        path = f'{path}.jpg'
    if 'jpeg' in path:
        path=path.replace("jpeg", "jpg")
    # print(f'url:{url}\nfilename:{file_name}\npath:{path}')
    if len is None:
        len=1
    # 单个文件下载
    if int(len) == 1 :
        async with httpx.AsyncClient(proxies=proxy, headers=headers) as client:
            try:
                response = await client.get(url)
                if response.status_code  == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    return path
                else:
                    response = requests.get(url)
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    return path
            except Exception as e:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    with open(path, 'wb') as file:
                        file.write(response.content)
                return path

    # 多个文件
    else:
        async with httpx.AsyncClient(proxies=proxy, headers=headers) as client:
            try:
                response = await client.get(url)
                #print(url,response)
                if response.status_code  == 200:
                    square_image = crop_center_square(Image.open(BytesIO(response.content)))
                    if square_image.mode != "RGB":
                        square_image = square_image.convert("RGB")
                    square_image.save(path)
                    return path
            except Exception as e:
                print(f'url: {url}, response: {e}')
                response = await client.get('https://gal.manshuo.ink/usr/uploads/galgame/zatan.png')
                if response.status_code  == 200:
                    square_image = crop_center_square(Image.open(BytesIO(response.content)))
                    if square_image.mode != "RGB":
                        square_image = square_image.convert("RGB")
                    square_image.save(path)
                    return path





async def download_audio(url):
    # 从URL中提取文件名
    parsed_url = urlparse(url)
    file_name = parsed_url.path.split('/')[-1]
    # 去除可能存在的请求参数
    file_name = file_name.split('?')[0]

    path = os.path.join(os.getcwd(), file_name)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()  # 检查请求是否成功

        async with aiofiles.open(path, 'wb') as file:
            await file.write(response.content)
    return path


def delete_boring_characters(sentence):
    """
        去除标题的特殊字符
    :param sentence:
    :return:
    """
    return re.sub(r'[0-9’!"∀〃#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~～\s]+', "", sentence)


def remove_files(file_paths: List[str]) -> Dict[str, str]:
    """
    根据路径删除文件

    Parameters:
    *file_paths (str): 要删除的一个或多个文件路径

    Returns:
    dict: 一个以文件路径为键、删除状态为值的字典
    """
    results = { }

    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                results[file_path] = 'remove'
            except Exception as e:
                results[file_path] = f'error: {e}'
        else:
            results[file_path] = 'don\'t exist'

    return results


def get_file_size_mb(file_path):
    """
    判断当前文件的大小是多少MB
    :param file_path:
    :return:
    """
    # 获取文件大小（以字节为单位）
    file_size_bytes = os.path.getsize(file_path)

    # 将字节转换为 MB 并取整
    file_size_mb = int(file_size_bytes / (1024 * 1024))

    return file_size_mb


def split_and_strip(text, sep=None) -> List[str]:
    # 先去除两边的空格，然后按指定分隔符分割
    split_text = text.strip().split(sep)
    # 去除每个子字符串两边的空格
    return [sub_text.strip() for sub_text in split_text]
