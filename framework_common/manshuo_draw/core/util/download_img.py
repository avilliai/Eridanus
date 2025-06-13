import random
import asyncio
import httpx
import base64
import os
import re
from io import BytesIO
from asyncio import get_event_loop
from PIL import Image
from .common import get_abs_path


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
        if response.status_code!= 200:
            response = client.get('https://gal.manshuo.ink/usr/uploads/galgame/zatan.png')  # 同步 GET 请求

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

#对图像进行批量处理
def process_img_download(img_list,is_abs_path_convert=True,gray_layer=False,proxy=None):
    if not isinstance(img_list, list):
        img_list = [img_list]
    processed_img=[]
    for content in img_list:
        if isinstance(content, str) and os.path.splitext(content)[1].lower() in [".jpg", ".png", ".jpeg",'.webp'] and not content.startswith("http"):  # 若图片为本地文件，则转化为img对象
            if is_abs_path_convert is True: content = get_abs_path(content)
            processed_img.append(Image.open(content))
        elif isinstance(content, str) and content.startswith("http"):
            processed_img.append(Image.open(BytesIO(base64.b64decode(download_img_sync(content)))))

        else:  # 最后判断是否为base64，若不是，则不添加本次图像
            try:
                processed_img.append(Image.open(BytesIO(base64.b64decode(content))))
            except:
                pass
    return processed_img