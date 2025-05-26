import base64
import random

import asyncio
import httpx
import base64

import re
from io import BytesIO

from PIL import Image

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