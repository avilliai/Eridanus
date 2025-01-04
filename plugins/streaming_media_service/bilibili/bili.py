import json
import time

import asyncio
import httpx
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from PIL import Image
from io import BytesIO
import time

from playwright.sync_api import sync_playwright

from plugins.utils.random_str import random_str

# 添加请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    'Cookie': 'buvid3=...; b_nut=...; _uuid=...; buvid4=...;'
}
async def fetch_latest_dynamic_id(uid):
    url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space"
    params = {
        "offset": "",
        "host_mid": uid
    }
    async with httpx.AsyncClient() as client:
        response=await client.get(url, params=params, headers=headers)
        data=response.json()
        return data['data']['items'][0]['id_str']   #返回最新动态id


async def fetch_dynamic(dynamic_id):
    """
    使用 Playwright 异步模式截图指定 URL 中指定 class name 元素的截图, 使用分块截图和拼接方法，并添加上下边距。

    Args:
        dynamic_id: 动态ID。

    Returns:
        保存截图的文件名 或 None (如果截图失败)。
    """
    url = f"https://t.bilibili.com/{dynamic_id}"

    output_filename = f"data/pictures/cache/{random_str()}.png"
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False)  # 设置为 False 以便调试
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标网页
        await page.goto(url)

        # 等待悬浮窗出现并关闭


        # 等待类名为 'bili-dyn-item' 的元素加载
        await page.wait_for_selector('.bili-dyn-item')
        await page.mouse.wheel(0, 500)
        await page.mouse.wheel(0, -500)
        await asyncio.sleep(1)
        try:
            await page.wait_for_selector("body > div:nth-child(16) > div > div > div.close > svg > path", timeout=5000)
            await page.click("body > div:nth-child(16) > div > div > div.close > svg > path")
            print("悬浮窗已关闭")
        except Exception as e:
            print(f"未能关闭悬浮窗: {e}")
        element = page.locator('.bili-dyn-item')

        # 截图保存
        await element.screenshot(path=output_filename)

        await browser.close()
        return output_filename
async def fetch_latest_dynamic(uid):
    r=await fetch_latest_dynamic_id(uid)
    if r:
        return await fetch_dynamic(r)
    else:
        return None