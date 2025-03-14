import httpx
import json
import requests
from developTools.message.message_components import Image, Text, Node, File
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
    path = f'data/pictures/random/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
async def get_all_pic(i):                        
    url = "https://api.seaya.link/random.php"  # 随机动漫
    params={'type': 'json'}
    path = f'data/pictures/random/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
async def get_wap(i):
    url = 'https://api.seaya.link/wap.php'    #竖屏随机
    params={'type': 'json'}
    path=f'data/pictures/col_img/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
async def get_web(i):
    url = 'https://api.seaya.link/web.php'    #横屏随机
    params={'type': 'json'}
    path=f'data/pictures/row_img/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
async def get_sex(i):
    url = 'https://api.lolicon.app/setu/v2'    #色图
    params={'type': 'json'}
    path=f'data/pictures/setu/pic{i}.png'
    r = await get_img(url,params,path)
    '''async with httpx.AsyncClient() as client:
        response = await client.get(url,params=params,headers=headers)
        if response.status_code != 200:
            print("Error: Request failed with status code", response.status_code)
            return
        try:
            r = response.json().get('data')[0].get('urls').get('original')
            r = new_response = await client.get(r)
            print(new_response)
            if new_response.status_code != 200:
                print("Error: Request failed with status code", new_response.status_code)
                return
            with open(path, 'wb') as f:
                f.write(new_response.content)
        except json.JSONDecodeError:
            print("Error: Failed to decode JSON")'''

    return Image(file=path)
async def get_random_json(i):
    url = 'https://www.dmoe.cc/random.php?return=json'    #随机图片
    params={'type': 'json'}
    path=f'data/pictures/random/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
'''async def get_random_pic():
    url = 'https://api.mtyqx.cn/tapi/random.php'    #随机图  
    params={'type': 'json'}
    path='plugins/random_pic/pic6.png'
    await get_img(url,params,path)
    return path'''
'''async def get_random_cat():
    url_7 = 'https://api.suyanw.cn/api/mao'    #随机猫猫
    async with httpx.AsyncClient() as client:
        r_7 = await client.get(url_7)
        path_7=r_7.json()['imgurl']
        return path_7'''
async def get_random_pic_1(i):
    url = f'https://api.vvhan.com/api/wallpaper/acg?type=json'    #随机图
    params={'type': 'json'}
    path=f'data/pictures/random/pic{i}.png'
    r = await get_img(url,params,path)

    return Image(file=path)
async def get_random_pic_2(i):
    url = 'https://api.horosama.com/random.php'    #随机图
    params={'format': 'json'}
    path=f'data/pictures/random/pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_dongfangproject(i):
    url = 'https://img.paulzzh.com/touhou/random'    #随机东方
    params={'type': 'json'}
    path=f'data/pictures/dongfang/pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)
async def get_random_meng(i):
    url = 'https://www.loliapi.com/acg/'    #随机萌图
    params={'type': 'json'}
    path=f'data/pictures/cute/pic{i}.png'
    r = await get_img(url,params,path)
    return Image(file=path)