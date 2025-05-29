import base64
import random

import asyncio
import httpx
import base64

import re
from io import BytesIO
from asyncio import get_event_loop
from PIL import Image

def download_img_sync(url,gray_layer=False,proxy=None):
    if url.startswith("data:image"):
        match = re.match(r"data:image/(.*?);base64,(.+)", url)
        if not match:
            raise ValueError("Invalid Data URI format")

        img_type, base64_data = match.groups()
        img_data = base64.b64decode(base64_data)  # 解码 Base64 数据
        base64_img = base64.b64encode(img_data).decode('utf-8')
        return base64_img

    if proxy is not None and proxy!= '':
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None

    with httpx.Client(proxies=proxies) as client:
        response = client.get(url)  # 同步 GET 请求

        if gray_layer:
            img = Image.open(BytesIO(response.content))  # 从二进制数据创建图片对象
            image_raw = img
            image_black_white = image_raw.convert('1')
            #将该pillow对象转化为base64
            buffer = BytesIO()
            image_black_white.save(buffer, format='format')
            img_data = buffer.getvalue()
            base64_img = base64.b64encode(img_data).decode('utf-8')
        else:
            base64_img = base64.b64encode(response.content).decode('utf-8')
        return base64_img

