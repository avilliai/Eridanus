import asyncio
import os
import random
import re
import httpx
import json
from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image,Node,Text
headers = {
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
    }
async def get_img(url,params,path,r=None):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(url,params=params)
        if response.status_code != 200:
            print("Error: Request failed with status code", response.status_code)
            return
        try:
            r = response.json().get('imgurl') or response.json().get('url') or response.json().get('jpegurl') or response.json().get('data')[0].get('urls').get('original')
            new_response = await client.get(r)
            print(new_response)
            if new_response.status_code != 200:
                print("Error: Request failed with status code", new_response.status_code)
                return
            with open(path, 'wb') as f:
                f.write(new_response.content)
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON")
async def get_random(i):
    url = 'https://www.98qy.com/sjbz/api.php'    #随机动漫
    params = {'lx': 'dongman', 'format': 'json'}
    path = f'data/pictures/cache/ran{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_all_pic(i):                        
    url = "https://api.seaya.link/random.php"  # 随机动漫
    params={'type': 'json'}
    path = f'data/pictures/cache/all{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_wap(i):
    url = 'https://api.seaya.link/wap.php'    #竖屏随机
    params={'type': 'json'}
    path=f'data/pictures/cache/pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_web(i):
    url = 'https://api.seaya.link/web.php'    #横屏随机
    params={'type': 'json'}
    path=f'data/pictures/cache/pic1{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_sex(i):
    url = 'https://api.lolicon.app/setu/v2'    #色图
    params={'type': 'json'}
    path=f'data/pictures/cache/pic2{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_json(i):
    url = 'https://www.dmoe.cc/random.php?return=json'    #随机图片
    params={'type': 'json'}
    path=f'data/pictures/cache/pic3{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
'''async def get_random_pic():
    url = 'https://api.mtyqx.cn/tapi/random.php'    #随机图  
    params={'type': 'json'}
    path='plugins/random_pic/pic6.png'
    await get_img(url,params,path)
    return path'''

async def get_random_cat(i):
    url = 'https://api.suyanw.cn/api/mao.php'    #随机猫猫
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        print(r.status_code)
        path = f'data/pictures/cache/cat{i}.png'
        with open(path, 'wb') as f:
            f.write(r.content)
    return Image(file=path)

async def get_random_pic_1(i):
    url = f'https://api.vvhan.com/api/wallpaper/acg?type=json'    #随机图
    params={'type': 'json'}
    path=f'data/pictures/cache/4pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_pic_2(i):
    url = 'https://api.horosama.com/random.php'    #随机图
    params={'format': 'json'}
    path=f'data/pictures/cache/5pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_dongfangproject(i):
    url = 'https://img.paulzzh.com/touhou/random'    #随机东方
    params={'type': 'json'}
    path=f'data/pictures/cache/pic6{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_meng(i):
    url = 'https://www.loliapi.com/acg/'    #随机萌图
    params={'type': 'json'}
    path=f'data/pictures/cache/pic7{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)


urls = ['https://img.ethanliang.top/animeGirl','https://img.ethanliang.top/hot','https://img.ethanliang.top/minimize','https://img.ethanliang.top/landscape',
'https://img.ethanliang.top/nature','https://img.ethanliang.top/jpanime','https://img.ethanliang.top/artwork','https://img.ethanliang.top/cityscape',
'https://img.ethanliang.top/cosplay','https://img.ethanliang.top/cyberpunk','https://img.ethanliang.top/digtal','https://img.ethanliang.top/fastal',
'https://img.ethanliang.top/spiderman','https://img.ethanliang.top/scifi','https://img.ethanliang.top/pixelart']

async def func(url):
    async with httpx.AsyncClient(timeout=None,http2=True) as client:
        response = await client.get(url)
        if response.status_code != 200:
            print("Error: Request failed with status code", response.status_code)
            return
        try:
            with open(f'data/pictures/cache/{url.split("/")[-1]}.png', 'wb') as f:
                f.write(response.content)
                return Image(file=f'data/pictures/cache/{url.split("/")[-1]}.png')
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON")

def functions(urls):
    return [func(url) for url in urls]
# possibly be failed
async def get_deskphoto(functions):
    try:
        r = await asyncio.gather(*functions)
    except Exception as e:
        print(f"Error in get_anime: {e}")
# slow
async def get_pixiv(i):
    api = 'https://image.anosu.top/pixiv'
    async with httpx.AsyncClient(timeout=None,follow_redirects=True) as client:
        response = await client.get(api)
        if response.status_code != 200:
            print("Error: Request failed with status code", response.status_code)
            return
        print(response.status_code)
        path = f'data/pictures/cache/pixiv{i}.png'
        with open(path, 'wb') as f:
            f.write(response.content)
    return Image(file=path)

urls = ['https://img.ethanliang.top/animeGirl','https://img.ethanliang.top/hot','https://img.ethanliang.top/minimize','https://img.ethanliang.top/landscape',
'https://img.ethanliang.top/nature','https://img.ethanliang.top/jpanime','https://img.ethanliang.top/artwork','https://img.ethanliang.top/cityscape',
'https://img.ethanliang.top/cosplay','https://img.ethanliang.top/cyberpunk','https://img.ethanliang.top/digtal','https://img.ethanliang.top/fastal',
'https://img.ethanliang.top/spiderman','https://img.ethanliang.top/scifi','https://img.ethanliang.top/pixelart']

def functions():
    return [func(url) for url in urls]
async def get_request(bot,config,event,func,num):
    functions = [func(i) for i in range(1,num+1)]
    try:
        r = await asyncio.gather(*functions)
        await bot.send(event,Node(content=r))
    except Exception as e:
        bot.logger.error(f"Error in get_anime: {e}")

async def get_text_number(bot,config,event):
  if re.findall(r'\d+', event.pure_text):
    numbers = int(re.findall(r'\d+', event.pure_text)[0])
  else:
    numbers = 3
  return numbers

async def doro():
    first = random.randint(1,2)
    if first == 1:
        second = random.randint(1,14)
    else: second = random.randint(1,9)
    random_files = f'data/pictures/doro/第{first}页/第{second}格'
    file_path = os.path.join(random_files,random.choice(os.listdir(random_files)))
    return file_path

async def chaijun():                              #async def是固定前缀，不能变
    url = "http://api.yujn.cn/api/chaijun.php?"   #柴郡图片的api地址
    async with httpx.AsyncClient() as client:      #使用httpx库发送get请求
        r = await client.get(url)             
        path="data/pictures/cache/"+'chaijun'+".png"     #图片保存路径
        with open(path, "wb") as f:              #将图片保存到本地
            f.write(r.content)
        return path                         #返回图片路径

def delete_files(directory):
    file_list = os.listdir(directory)
    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

import time 
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_vv_pic(keys: str, num: int, out_path=None):
    out_path = r'C:\Users\29735\Desktop\project\eridanus_with_webui.ver.0.1.1.fix\Eridanus\data\pictures\cache'
    # 确保目录存在
    os.makedirs(out_path, exist_ok=True)
    # Chrome 配置
    options = webdriver.ChromeOptions()
    prefs = {
        'profile.default_content_settings.popups': 0,
        'download.default_directory': out_path,
        'directory_upgrade': True  # 允许更改下载目录
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(options=options)
    driver.get('https://vvapi.cicada000.work/?')
    driver.find_element(By.ID, 'query').send_keys(keys)
    time.sleep(0.5)
    driver.find_element(By.CLASS_NAME, 'search-button').click()
    time.sleep(3.5)
    pics = driver.find_elements(By.CLASS_NAME, 'preview-frame-container')[:num]
    for pic in pics:
        pic.click()
        time.sleep(0.35)
    driver.quit()
    return out_path
