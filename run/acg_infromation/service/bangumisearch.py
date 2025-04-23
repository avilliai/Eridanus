from bs4 import BeautifulSoup
import httpx
import random

from bilibili_api import hot, sync
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import requests
import asyncio

def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers
async def banguimiList(year, month, top):
    rank = 1  # 排名
    page = 1  # 页数
    finNal_Cover = []
    fiNal_Text = []
    isbottom = 0  # 标记是否到底
    page = top // 24  # 计算页数
    if top % 24 != 0:
        page += 1  # 向上取整
    for i in range(1, page + 1):
        url = f"https://bgm.tv/anime/browser/airtime/{year}-{month}?sort=rank&page={i}"  # 构造请求网址，page参数为第i页
        #print(url)
        async with httpx.AsyncClient(timeout=20, headers=get_headers()) as client:  # 100s超时
            response = await client.get(url)  # 发起请求
        soup = BeautifulSoup(response.content, "html.parser")
        name_list = soup.find_all("h3")  # 获取番剧名称列表
        score_list = soup.find_all("small", class_="fade")  # 获取番剧评分列表
        popularity_list = soup.find_all("span", class_="tip_j")  # 获取番剧评分人数列表)
        anime_items = soup.find_all("img", class_="cover")

        for iCover in anime_items:
            src_value = str(iCover).split('src="')[1].split('"')[0]
            # 自动补全https前缀
            src_url = f"https:{src_value}"
            finNal_Cover.append(src_url)

        for j in range(len(score_list)):
            try:
                name_jp = name_list[j].find("small", class_="grey").string + "\n    "  # 获取番剧日文名称
            except:
                name_jp = ""
            name_ch = name_list[j].find("a", class_="l").string  # 获取番剧中文名称
            score = score_list[j].string  # 获取番剧评分
            popularity = popularity_list[j].string  # 获取番剧评分人数
            fiNal_Text.append("{:<3}".format(rank) + f"{name_jp}{name_ch}\n    {score}☆  {popularity}\n")
            if rank == top:  # 达到显示上限
                break
            rank += 1
        if rank >= top:  # 到底了
            isbottom = 1
            break
        #print(rank,top)
    return fiNal_Text, finNal_Cover, isbottom


async def bangumisearch(url):
    async with httpx.AsyncClient(timeout=20, headers=get_headers()) as client:  # 100s超时
        response = await client.get(url)  # 发起请求
    soup = BeautifulSoup(response.content, "html.parser")
    subjectlist = soup.find_all("h3")[0:-2]
    crtlist = soup.find_all("h3")[-2].find_all("dd")
    if len(crtlist) == 0:
        subjectlist = soup.find_all("h3")[0:-3]
        crtlist = soup.find_all("h3")[-3].find_all("dd")
    str0 = soup.find("title").string + "\n"
    for i in range(len(subjectlist)):
        str0 += f"{i + 1}.{subjectlist[i].find('a').string}\n"
    str0 += "相关人物：\n"
    for j in range(len(crtlist)):
        str0 += f"0{j + 1}.{crtlist[j].string}\n"
    list = [str0, subjectlist, crtlist]
    return list


async def screenshot_to_pdf_and_png(url, path, width=1024, height=9680):
    url = f"https://mini.s-shot.ru/{width}x{height}/PNG/1800/?{url}"
    async with httpx.AsyncClient(timeout=200) as client:
        r = await client.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
        return path


async def delete_msg_async(msg_id):
    url = "http://localhost:3000/delete_msg"
    payload = {
        "message_id": str(msg_id)
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ff'
    }
    async with httpx.AsyncClient(timeout=None, headers=headers) as client:
        response = await client.post(url, json=payload)





async def add_rounded_rectangle(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)

async def draw_PIL_today_hot():
    # 打开模板图片

    file_path = 'data/pictures/wife_you_want_img/'
    template_path=f'{file_path}bili_today_hot_back.png'
    output_path=f'{file_path}bili_today_hot_back_out.png'
    template = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(template)

    resize_x=370
    resize_y=260
    resize_x_touxiang=90
    resize_y_touxiang=90

    hot_get_bili = sync(hot.get_hot_videos())
    number=0
    for context_check in hot_get_bili['list']:

        #print(number)
        if number == 8:break
        text=context_check[f'title']
        thumbnail_path_url = context_check[f'pic']
        touxiang_path_url = context_check['owner']['face']
        thumbnail_path=f'{file_path}fengmian.png'
        touxiang_path=f'{file_path}touxiang.png'
        response = requests.get(thumbnail_path_url)
        with open(thumbnail_path, 'wb') as file:
            file.write(response.content)
        response = requests.get(touxiang_path_url)
        with open(touxiang_path, 'wb') as file:
            file.write(response.content)

        x_check=number%2
        y_check=number//2
        #print(x_check,y_check)
        paste_x=146+x_check*430
        paste_y=343+y_check*394
        paste_x_touxiang=paste_x
        paste_y_touxiang=paste_y+283

        thumbnail = Image.open(thumbnail_path).resize((resize_x, resize_y), Image.Resampling.LANCZOS)
        mask = Image.new("L", (resize_x, resize_y), 0)
        mask_draw = ImageDraw.Draw(mask)
        await add_rounded_rectangle(mask_draw, (0, 0, resize_x, resize_y), radius=20, fill=255)
        template.paste(thumbnail, (paste_x, paste_y), mask)

        thumbnail = Image.open(touxiang_path).resize((resize_x_touxiang, resize_y_touxiang), Image.Resampling.LANCZOS)
        mask = Image.new("L", (resize_x_touxiang, resize_y_touxiang), 0)
        mask_draw = ImageDraw.Draw(mask)
        await add_rounded_rectangle(mask_draw, (0, 0, resize_x_touxiang, resize_y_touxiang), radius=45, fill=255)
        template.paste(thumbnail, (paste_x_touxiang, paste_y_touxiang), mask)

        text = [text[i:i + 9] for i in range(0, len(text), 9)]
        text = text[:2]
        text = '\n'.join(text)
        # 添加文案
        font = ImageFont.truetype(f"run/streaming_media/service/Link_parsing/data/fort/LXGWWenKai-Bold.ttf", 30)  # 替换为实际字体路径
        text_position = (paste_x_touxiang+100, paste_y_touxiang+6)  # 文案位置
        draw.text(text_position, text, font=font, fill="black")
        number += 1
    # 保存输出图片
    template.save(output_path)
    #template.show()

async def daily_task():
    await draw_PIL_today_hot()

# 包装一个同步任务来调用异步任务
def run_async_task():
    asyncio.run(daily_task())
