import asyncio
from asyncio import sleep
from typing import Optional, Tuple, List, Dict, Any


from PicImageSearch import Network

from developTools.utils.logger import get_logger
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from plugins.utils.random_str import random_str

# proxies =
#proxies = "http://127.0.0.1:10809"

#url = "https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=CgoxODQwMDk0OTcyEhRIG9o5t_uwgsEQUyL4lGRnEDZCVhjlig4g_woo24jQxMuKiQMyBHByb2RQgL2jAQ&spec=0&rkey=CAESKBkcro_MGujoBSDPSkH77WdNctk4U08YL50QmBMLw88CPMwNfXTXTmw"
bovw = False  # Use feature search or not
verify_ssl = False  # Whether to verify SSL certificates or not
async def ascii2d_async(proxies,url):
    base_url = "https://ascii2d.net"
    async with Network(proxies=proxies, verify_ssl=verify_ssl) as client:
        from PicImageSearch import Ascii2D
        ascii2d = Ascii2D(base_url=base_url, client=client, bovw=bovw)
        resp = await ascii2d.search(url=url)
        print(resp.raw[0])
        selected = next((i for i in resp.raw if i.title or i.url_list), resp.raw[0])
        return [resp.raw[0].thumbnail, f"标题：{selected.title}\n作者：{selected.author}\n{selected.author_url}\n链接：{selected.url}"]

async def baidu_async(proxies,url):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import BaiDu
        baidu = BaiDu(client=client)
        resp = await baidu.search(url=url)
        #resp = await baidu.search(file=file)
        return [resp.raw[0].thumbnail, f"相关链接：{resp.raw[0].title}\n 百度识图：{resp.url}"]

async def Copyseeker_async(proxies,url):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import Copyseeker
        copyseeker = Copyseeker(client=client)
        resp = await copyseeker.search(url=url)
        #resp = await copyseeker.search(file=file)
        if resp.raw:
            return [resp.raw[0].thumbnail, f"相关链接：{resp.raw[0].url}\n 来源：{resp.raw[0].title}"]
    # logger.info(resp.visuallySimilarImages)
async def google_async(proxies,url):
    base_url = "https://www.google.co.jp"
    async with Network(proxies=proxies) as client:
        from PicImageSearch import Google
        google = Google(client=client, base_url=base_url)
        resp = await google.search(url=url)
        #resp = await google.search(file=file)
        if resp:
            selected = next((i for i in resp.raw if i.thumbnail), resp.raw[0])
            return [selected.thumbnail, f"标题：{selected.title}\n 来源：{selected.url}"]

async def iqdb_async(proxies,url):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import Iqdb
        iqdb = Iqdb(client=client)
        resp = await iqdb.search(url=url)
        #resp = await iqdb.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度：{resp.raw[0].similarity}\niqdb\n 图片来源：{resp.raw[0].url}\n 其他图片来源：{resp.raw[0].other_source}\nSauceNAO Search Link: {resp.saucenao_url}\nAscii2d Search Link: {resp.ascii2d_url}\nTinEye Search Link: {resp.tineye_url}\nGoogle Search Link: {resp.google_url}\nNumber of Results with Lower Similarity: {len(resp.more)}"]

async def iqdb3D_async(proxies,url):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import Iqdb
        iqdb = Iqdb(client=client, is_3d=True)
        resp = await iqdb.search(url=url)
        #resp = await iqdb.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度：{resp.raw[0].similarity},\n源网站搜索：{resp.raw[0].content}\n图片来源：{resp.raw[0].url}"]


async def saucenao_async(proxies,url,api_key):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import SauceNAO
        saucenao = SauceNAO(client=client, api_key=api_key, hide=3)
        resp = await saucenao.search(url=url)
        #resp = await saucenao.search(file=file)
        return [resp.raw[0].thumbnail,f"相似度{resp.raw[0].similarity}\n标题：{resp.raw[0].title}\n作者：{resp.raw[0].author}\n{resp.raw[0].author_url}\n图片来源：{resp.raw[0].url}\n{resp.raw[0].source}"]
async def yandex_async(proxies,url):
    async with Network(proxies=proxies) as client:
        from PicImageSearch import Yandex
        yandex = Yandex(client=client)
        resp = await yandex.search(url=url)
        #resp = await yandex.search(file=file)
        return [resp.raw[0].thumbnail,f"\n标题：{resp.raw[0].title}\n图片来源：{resp.raw[0].url}\n{resp.raw[0].source}"]





logger=get_logger()
async def fetch_results(proxies, url: str,sauceno_api:str) -> Dict[str, Optional[List[Any]]]:

    async def _safe_call(func, *args, **kwargs) -> Tuple[str, Optional[List[Any]]]:
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=60)
            return func.__name__, result
        except asyncio.TimeoutError:
            logger.warning(f"{func.__name__} 超时")
            return func.__name__, None
        except Exception as e:
            logger.error(f"{func.__name__} 出现错误: {e}")
            return func.__name__, None

    # 定义所有要并发执行的任务
    tasks = [
        _safe_call(ascii2d_async, proxies, url),
        _safe_call(baidu_async, proxies, url),
        _safe_call(Copyseeker_async, proxies, url),
        _safe_call(google_async, proxies, url),
        _safe_call(iqdb_async, proxies, url),
        _safe_call(iqdb3D_async, proxies, url),
        _safe_call(saucenao_async, proxies, url, sauceno_api),  # 替换为你的 API key
        _safe_call(yandex_async, proxies, url),
    ]

    # 并发执行所有任务并获取结果
    results = await asyncio.gather(*tasks)

    # 转换为字典形式，方便查看各任务结果
    return {name: result for name, result in results}
"""
来源：soutu.bot
"""

async def automate_browser(image_path):
    async with async_playwright() as p:
        # 启动浏览器
        p.context_options = {
            "timeout": 110000  # 设置默认超时时间为 60 秒
        }
        browser = await p.chromium.launch(headless=True)  # headless=False 以便观察操作
        context = await browser.new_context()
        page = await context.new_page()

        # 打开目标网页
        await page.goto("https://soutubot.moe/",wait_until="load")

        # 点击目标元素
        await page.locator('xpath=//*[@id="app"]/div/div/div/div[1]/div[2]/div/div[2]/div/div/span[2]').click(timeout=900000)


        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(image_path,timeout=900000)

        await page.wait_for_load_state("networkidle",timeout=900000)

        # 提取目标部分的原始 HTML 源代码
        extracted_html = await page.locator('xpath=//*[@id="app"]/div/div/div/div[2]').evaluate("element => element.outerHTML",timeout=900000)


        img_path = "data/pictures/cache/" + random_str() + ".png"
        r, _ = await asyncio.gather(
            extract_data(extracted_html),
            page.locator('xpath=//*[@id="app"]/div/div/div/div[2]').screenshot(path=img_path,timeout=900000)
        )

        # 关闭浏览器
        try:
            await browser.close()
        except:
            pass
        return r,img_path

async def extract_data(html_code):
    # 使用 asyncio.to_thread 在不同的线程中执行 BeautifulSoup 解析
    # 避免阻塞事件循环
    soup = await asyncio.to_thread(BeautifulSoup, html_code, 'html.parser')
    cards = soup.find_all('div', class_='card-2')
    data = []

    for card in cards:
      item = {}

      # Extract title
      title_span = card.find('div', class_='sm:text-xl')
      if title_span:
          item['title'] = title_span.span.text.strip()
      else:
          item['title'] = ""

      # Extract similarity
      similarity_span = card.find('span', class_='bg-emerald-600')
      if similarity_span:
          item['similarity'] = similarity_span.text.strip()
      else:
          item['similarity'] = ""

      # Extract image URL
      img_tag = card.find('img')
      if img_tag:
          item['image_url'] = img_tag['src']
      else:
          item['image_url'] = ""

      # Extract links
      links = card.find_all('a', class_='el-button')
      if len(links) > 0:
          item['detail_page_url'] = links[0]['href']
      else:
          item['detail_page_url'] = ""
      if len(links) > 1:
          item['image_page_url'] = links[1]['href']
      else:
          item['image_page_url'] = ""

      data.append(item)

    return data