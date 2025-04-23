import os
import re

import httpx
from httpx._urlparse import urlparse

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from framework_common.utils.random_str import random_str


def main(bot: ExtendBot,config:YAMLManager):
    @bot.on(GroupMessageEvent)
    async def today_husband(event: GroupMessageEvent):
        text = str(event.pure_text)
        if not text.startswith("今") or not any(keyword in text for keyword in ["今日", "今天"]):
            return
        url_map = {
            "腿": "https://api.dwo.cc/api/meizi",
            "黑丝": "https://api.dwo.cc/api/hs_img",
            "白丝": "https://api.dwo.cc/api/bs_img",
            "头像": "https://api.dwo.cc/api/dmtou",
        }

        url = next((u for k, u in url_map.items() if k in text), None)
        if not url and re.search(r'cos|cosplay|bacos|bacosplay|ba美女|ba小姐姐', text, re.IGNORECASE):
            bot.logger.info("今日bacos开启！")
            url = 'https://img.sorahub.site'

        if not url:
            return

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                content_type = response.headers.get('Content-Type', '')

                if 'image' in content_type:
                    ext = get_image_extension(content_type)
                    img_path = f'data/pictures/cache/{random_str()}{ext}'
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    await bot.send(event, [Image(file=img_path)])

                elif 'json' in content_type:
                    data = response.json()
                    img_url = data.get('数据', {}).get('pic') or data.get('data') or data.get('url')

                    if img_url:
                        ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                        img_path = f'data/pictures/cache/{random_str()}{ext}'
                        img_response = await client.get(img_url)
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)

                        msg_chain = [Image(file=img_path)]
                        if 'artistName' in data:
                            msg_chain.append(f'\ncoser：{data["artistName"]}')
                        await bot.send(event, msg_chain)
                    else:
                        await bot.send(event, 'API 返回了 JSON 但没有图片 URL 喵~')

                else:
                    await bot.send(event, 'API 返回了未知格式数据喵~')

        except Exception as e:
            bot.logger.error(f'API 请求失败: {e}')
            await bot.send(event, 'api失效了喵，请过一段时间再试试吧')

    def get_image_extension(content_type: str) -> str:
        if 'png' in content_type:
            return '.png'
        elif 'webp' in content_type:
            return '.webp'
        return '.jpg'