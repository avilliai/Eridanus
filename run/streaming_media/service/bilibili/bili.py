import sys
import asyncio
import httpx
from playwright.async_api import async_playwright
from run.streaming_media.service.Link_parsing.Link_parsing import link_prising
from framework_common.utils.random_str import random_str
from run.streaming_media.service.Link_parsing.core.bili import fetch_latest_dynamic_id_api
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
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
    try:

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.get(url, params=params, headers=headers,timeout=5)
            data = response.json()
            d1=data['data']['items'][0]['id_str']
            d2=data['data']['items'][1]['id_str']  # 返回最新动态id
            return d1,d2

    except Exception as e:

        dy_id_1,dy_id_2=await fetch_latest_dynamic_id_api(uid)
        return dy_id_1,dy_id_2


async def fetch_dynamic(dynamic_id, mode="mobile"):
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
        browser = await p.chromium.launch(headless=True)  # 无头模式
        if mode == "mobile":
            iphone = p.devices['iPhone 14']  # 模拟 iPhone 设备
            context = await browser.new_context(
                **iphone,
                proxy=None  # 禁用代理
            )
        else:
            context = await browser.new_context()
        page = await context.new_page()

        # 打开目标网页
        await page.goto(url)

        if mode == "mobile":
            # 注入 CSS 隐藏右上角的“打开APP”按钮
            await page.add_style_tag(content="""
                .openapp-content {
                    display: none !important;
                }
            """)
            await page.add_style_tag(content="""
                        .m-fixed-openapp {
                            display: none !important;
                        }
                    """)
        else:
            await page.add_style_tag(content="""
                        .login-panel-popover {
                            display: none !important;
                        }
                    """)
            await page.add_style_tag(content="""
                                .login-tip {
                                    display: none !important;
                                }
                            """)

        # 判断目标类名是否存在
        if await page.locator('.dyn-card').is_visible():
            target_selector = '.dyn-card'
        elif await page.locator('.opus-modules').is_visible():
            target_selector = '.opus-modules'
        elif await page.locator('.bili-dyn-item').is_visible():
            target_selector = '.bili-dyn-item'
        else:
            await asyncio.sleep(5)
            await page.screenshot(path=output_filename, full_page=True)  # 截取整个页面，我草，我真的服了
            await browser.close()
            return output_filename

        # 等待目标元素加载
        await page.wait_for_selector(target_selector)

        # 截取目标元素
        element = page.locator(target_selector)
        await element.screenshot(path=output_filename)

        await browser.close()
        return output_filename


async def fetch_latest_dynamic(uid, config):
    r1, r2 = await fetch_latest_dynamic_id(uid)
    bilibili_type_draw = config.streaming_media.config["bili_dynamic"]["draw_type"]
    if r1:
        if bilibili_type_draw == 1:
            dynamic = await fetch_dynamic(r1, config.streaming_media.config["bili_dynamic"]["screen_shot_mode"])
        elif bilibili_type_draw == 2:
            dynamic= (await link_prising(f'https://t.bilibili.com/{r1}',filepath='data/pictures/cache/'))['pic_path']
        return dynamic
    else:
        return None

