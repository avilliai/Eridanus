# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
import httpx
import os
from io import BytesIO
import urllib
import re
from PIL import Image

import asyncio
import requests
import yaml
from bs4 import BeautifulSoup  # 用于解析 HTML

from framework_common.utils.random_str import random_str
from framework_common.utils.utils import get_headers


async def emojimix(emoji1, emoji2):
    if is_emoji(emoji1) and is_emoji(emoji2):
        pass
    else:
        print("not emoji")
        return None
    url = f"http://promptpan.com/mix/{emoji1}/{emoji2}"
    # url=f"https://emoji6.com/emojimix/?emoji={emoji1}+{emoji2}"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        # print(r.content)
        with open(path, "wb") as f:
            f.write(r.content)  # 从二进制数据创建图片对象
        # print(path)
        return path


url = "https://www.ipip5.com/today/api.php"
url2 = "https://api.pearktrue.cn/api/steamplusone/"


async def hisToday():
    async with httpx.AsyncClient(timeout=100) as client:
        data = {"type": "json"}
        r = await client.get(url, params=data)
        return r.json()


async def steamEpic():
    url = 'https://steamstats.cn/en/xi'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.41'}

    async with httpx.AsyncClient(timeout=100) as client:
        try:
            response = await client.get(url, headers=headers)

            response.raise_for_status()

            soup = bs(response.text, "html.parser")
            tbody = soup.find('tbody')
            tr = tbody.find_all('tr')

            i = 1
            text = "\n"
            for tr in tr:
                td = tr.find_all('td')
                name = td[1].string.strip().replace('\n', '').replace('\r', '')
                gametype = td[2].string.replace(" ", "").replace('\n', '').replace('\r', '')
                start = td[3].string.replace(" ", "").replace('\n', '').replace('\r', '')
                end = td[4].string.replace(" ", "").replace('\n', '').replace('\r', '')
                time = td[5].string.replace(" ", "").replace('\n', '').replace('\r', '')
                oringin = td[6].find('span').string.replace(" ", "").replace('\n', '').replace('\r', '')
                text += f"序号：{i}\n" \
                        f"游戏名称：{name}\n" \
                        f"DLC/game：{gametype}\n" \
                        f"开始时间：{start}\n" \
                        f"结束时间：{end}\n" \
                        f"是否永久：{time}\n" \
                        f"平台：{oringin}\n"
                i += 1

        except httpx.HTTPStatusError as e:
            text = f"HTTP错误: {e}"
        except Exception as e:
            text = f"发生错误: {e}"

    return text


async def arkSign(url):
    url = f"https://api.lolimi.cn/API/ark/a2.php?img={url}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
    # print(r.text)
    # print(r.text,type(r.json()))
    return str(r.text)


# 百度图片搜索并下载图片
async def baidusearch_and_download_image(keyword):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "close",
        "Priority": "u=4",
        "TE": "Trailers"
    }
    search_url = f"https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&word={keyword}"

    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            response = await client.get(search_url)
            response.raise_for_status()
            data = response.json()

            # 找到第一次出现的thumbURL
            thumb_url = next((item['thumbURL'] for item in data.get('data', []) if 'thumbURL' in item), None)

            if not thumb_url:
                raise ValueError("未找到thumbURL")

            print(f"找到的thumbURL: {thumb_url}")

            # 下载图片
            image_response = await client.get(thumb_url)
            image_response.raise_for_status()

            # 保存图片为JPEG格式
            ranpath = random_str()
            path = f"data/pictures/cache/{ranpath}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            img = Image.open(BytesIO(image_response.content))
            img.save(path, format='JPEG')
            print(f"图片保存路径: {path}")
            return path

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"搜索和下载图片失败: {e}")
        return None


# mc服务器查询
async def minecraftSeverQuery(ip):
    async with httpx.AsyncClient(headers=get_headers(), timeout=20) as client:
        r = await client.get(f"https://list.mczfw.cn/?ip={ip}")

        soup = BeautifulSoup(r.text, 'html.parser')
        # 找到 class 为 "form" 的第一个 <tr> 标签
        description = soup.find('meta', attrs={'name': 'description'}).get('content')
        og_title = soup.find('meta', property='og:title').get('content')
        favicon = soup.find('meta', property='og:image').get('content')
        return "https:" + str(favicon), og_title, description


# Bing 图片搜索并下载图片
async def bingsearch_and_download_image(keyword):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.2107.204 Safari/537.36'
    }
    url = "https://cn.bing.com/images/async?q={0}&first={1}&count={2}&scenario=ImageBasicHover&datsrc=N_I&layout=ColumnBased&mmasync=1&dgState=c*9_y*2226s2180s2072s2043s2292s2295s2079s2203s2094_i*71_w*198&IG=0D6AD6CBAF43430EA716510A4754C951&SFX={3}&iid=images.5599"

    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        try:
            search_url = url.format(urllib.parse.quote(keyword), 1, 35, 1)
            response = await client.get(search_url)
            response.raise_for_status()
            html = response.text

            # 从缩略图列表页中找到原图的url
            soup = BeautifulSoup(html, "lxml")
            link_list = soup.find_all("a", class_="iusc")
            image_url = None
            rule = re.compile(r"\"murl\"\:\"http\S[^\"]+")
            for link in link_list:
                result = re.search(rule, str(link))
                if result:
                    image_url = result.group(0).replace('amp;', '')[8:]
                    break

            if not image_url:
                raise ValueError("未找到图片URL")

            print(f"找到的imageURL: {image_url}")

            # 下载图片
            image_response = await client.get(image_url)
            image_response.raise_for_status()

            # 保存图片为JPEG格式
            ranpath = random_str()
            path = f"data/pictures/cache/{ranpath}.jpg"
            os.makedirs(os.path.dirname(path), exist_ok=True)

            img = Image.open(BytesIO(image_response.content))
            img.save(path, format='JPEG')
            print(f"图片保存路径: {path}")
            return path

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} {e.response.text}")
        except Exception as e:
            print(f"搜索和下载图片失败: {e}")
        return None


# 并发请求百度和Bing图片搜索，返回最先成功的图片路径
async def search_and_download_image(keyword):
    tasks = [
        asyncio.create_task(baidusearch_and_download_image(keyword)),
        asyncio.create_task(bingsearch_and_download_image(keyword))
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    for task in done:
        path = task.result()
        if path:
            # 取消未完成的任务
            for task in pending:
                task.cancel()
            return path

    # 如果第一个完成的任务返回None，继续等待其他任务完成
    done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
    for task in done:
        path = task.result()
        if path:
            return path

    return None


# 英语语法分析
async def eganylist(text, proxy):
    proxies = None
    if proxy != "" or proxy != " ":
        proxies = {
            "http://": proxy,
            "https://": proxy
        }
    URL = f"https://api.aipie.cool/api/ega/analysis/img?text={text}"
    async with httpx.AsyncClient(timeout=20, proxies=proxies, verify=False) as client:
        r = await client.get(URL)
        p = "data/pictures/cache/" + random_str() + '.png'
        with open(p, "wb") as f:
            f.write(r.content)
        return p


def manage_group_status(user_id, status=None,file_name=None,target_group=None,type=None):
    file_path_check = 'data/pictures/wife_you_want_img'
    if not os.path.exists(file_path_check):
        os.makedirs(file_path_check)
    if file_name:
        file_path = 'data/pictures/wife_you_want_img'
        file_path=os.path.join(file_path,file_name)
    else:
        file_path = "data/pictures/wife_you_want_img/wife_you_want.yaml"
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            yaml.dump({}, file)
    with open(file_path, 'r') as file:
        try:
            users_data = yaml.safe_load(file) or {}
        except yaml.YAMLError:
            users_data = {}
    #print(users_data)
    if type is None:
        type='day'#0代表天数，1代表周，2代表月
    if status is not None:
        if target_group is not None:
            if type=='day':
                if type not in users_data:
                    users_data[type] = {}
                if target_group not in users_data[type]:
                    users_data[type][target_group] = {}
                if user_id not in users_data[type][target_group]:
                    users_data[type][target_group][user_id] = 0
                number = int(users_data[type][target_group][user_id])
                users_data[type][target_group][user_id] = number + 1
                type = 'week'
            if type == 'week':
                if type not in users_data:
                    users_data[type] = {}
                if target_group not in users_data[type]:
                    users_data[type][target_group] = {}
                if user_id not in users_data[type][target_group]:
                    users_data[type][target_group][user_id] = 0
                number = int(users_data[type][target_group][user_id])
                users_data[type][target_group][user_id] = number + 1
                type = 'moon'
            if type == 'moon':
                if type not in users_data:
                    users_data[type] = {}
                if target_group not in users_data[type]:
                    users_data[type][target_group] = {}
                if user_id not in users_data[type][target_group]:
                    users_data[type][target_group][user_id] = 0
                number=int(users_data[type][target_group][user_id])
                #print(number)
                users_data[type][target_group][user_id] = number + 1
        else:
            users_data[user_id] = status
        with open(file_path, 'w') as file:
            yaml.safe_dump(users_data, file)
        return status

    if target_group:
        return users_data.get(type, {}).get(target_group, {}).get(user_id, False)
    else:
        return users_data.get(user_id, False)

def sort_yaml(file_name,target_group,type=None):
    file_path = 'data/pictures/wife_you_want_img'
    file_path = os.path.join(file_path, file_name)
    if not os.path.exists(file_path):
        return '还没有任何一位群友开过趴哦',None
    if type is None:
        type='day'#0代表天数，1代表周，2代表月
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    if type not in data:
        return '还没有任何一位群友开过趴哦',None
    if target_group not in data[type]:
        return '本群还没有任何一位群友开过趴哦',None
    data=data.get(type, {}).get(target_group, {})
        #print(data)
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)
    context=''
    king=None
    time=0
    for key, value in sorted_data:
        context +=f'【{key}】: {value}次~\n'
        if time != 0:
            continue
        time += 1
        king = key
    return context,king

def get_game_image(url,filepath,id):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    id = str(id) + '.jpg'
    #print(str(id))
    # 获取指定文件夹下的所有文件
    files = os.listdir(filepath)
    if id in files:
        img_path = os.path.join(filepath, id)
        print('图片已存在，返回图片名称')
        return img_path
    # 过滤出文件名（不包含文件夹）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        #filename = url.split('/')[-1]
        id = str(id)
        img_path = os.path.join(filepath, id)
        #print(img_path)
        # 打开一个文件以二进制写入模式保存图片
        with open(img_path, 'wb') as f:
            f.write(response.content)
        print("图片已下载并保存为 {}".format(img_path))
        return img_path
    else:
        print(f"下载失败，状态码: {response.status_code}")
        return None