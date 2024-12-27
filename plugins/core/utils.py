from io import BytesIO

import httpx
from PIL import Image


async def download_img(url,path,gray_layer=False):
    async with httpx.AsyncClient() as client:
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