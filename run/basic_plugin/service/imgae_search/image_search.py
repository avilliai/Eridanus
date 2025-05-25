import asyncio
from typing import Optional, Tuple, List, Dict, Any


from developTools.utils.logger import get_logger
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from framework_common.utils.random_str import random_str

# proxies =
#proxies = "http://127.0.0.1:10809"

#url = "https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=CgoxODQwMDk0OTcyEhRIG9o5t_uwgsEQUyL4lGRnEDZCVhjlig4g_woo24jQxMuKiQMyBHByb2RQgL2jAQ&spec=0&rkey=CAESKBkcro_MGujoBSDPSkH77WdNctk4U08YL50QmBMLw88CPMwNfXTXTmw"






logger=get_logger()

"""
来源：soutu.bot
"""

async def automate_browser(image_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 改为 False 以便观察
        context = await browser.new_context()
        page = await context.new_page()
        logger.info("Browser launched")
        await page.goto("https://soutubot.moe/")
        await page.wait_for_load_state("networkidle", timeout=60000)
        logger.info("Page loaded")
        file_input = page.locator('input[type="file"]')
        #await file_input.wait_for(state="visible", timeout=90000)
        await file_input.set_input_files(image_path,timeout=150000)
        logger.info("File input")
        await page.wait_for_url("https://soutubot.moe/results/*", timeout=90000)
        await page.wait_for_load_state("domcontentloaded", timeout=90000)

        extracted_html = await page.locator('#app > div > div > div > div.grid.grid-cols-1.gap-4.w-full').evaluate("element => element.outerHTML")
        #await page.wait_for_load_state("domcontentloaded",timeout=90000)
        #print(extracted_html)
        img_path = "data/pictures/cache/" + random_str() + ".png"
        r, _ = await asyncio.gather(
            extract_data(extracted_html),
            page.locator('xpath=//*[@id="app"]/div/div/div/div[2]').screenshot(path=img_path)
        )

        try:
            await browser.close()
        except:
            pass
        return r, img_path


async def extract_data(html_code):
    soup = await asyncio.to_thread(BeautifulSoup, html_code, 'html.parser')
    cards = soup.find_all('div', class_='card-2')
    data = []

    for card in cards:
      item = {}

      title_span = card.find('div', class_='sm:text-xl')
      if title_span:
          item['title'] = title_span.span.text.strip()
      else:
          item['title'] = ""

      similarity_span = card.find('span', class_='bg-emerald-600')
      if similarity_span:
          item['similarity'] = similarity_span.text.strip()
      else:
          item['similarity'] = ""

      img_tag = card.find('img')
      if img_tag:
          item['image_url'] = img_tag['src']
      else:
          item['image_url'] = ""

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
#print(asyncio.run(automate_browser("img_4.png")))