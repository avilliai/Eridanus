import asyncio
import random

import httpx
async def get_info(data,proxies=None,mode="default"):
    if mode=="random":
        id=random.choice(data["works"])['id']
        source_id=random.choice(data["works"])['source_id']
        title=random.choice(data["works"])['title']
        nsfw=random.choice(data["works"])['nsfw']
        mainCoverUrl=random.choice(data["works"])['mainCoverUrl']
        new_url=f"https://api.asmr-200.com/api/tracks/{id}?v=1"
    else:
        id = data["works"][0]['id']
        source_id = data["works"][0]['source_id']
        title = data["works"][0]['title']
        nsfw = data["works"][0]['nsfw']
        mainCoverUrl = data["works"][0]['mainCoverUrl']
        new_url = f"https://api.asmr-200.com/api/tracks/{id}?v=1"
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(new_url)
        data = response.json()
    media_urls = []

    if isinstance(data, list):
        if "children" in data[0]:
            for i in data[0]['children']:
                """
                子目录判断，但因为有重试，所以我觉得用不上。
                """
                if "children" in i and 'mediaStreamUrl' not in i:
                    for j in i['children']:
                        media_url = j['mediaStreamUrl']
                        son_title = j['title']
                        media_urls.append([media_url, son_title])
                else:
                    media_url = i['mediaStreamUrl']
                    son_title = i['title']
                    media_urls.append([media_url, son_title])
        else:
            media_url = data[0]['mediaStreamUrl']
            son_title = data[0]['title']
            media_urls.append([media_url, son_title])
    else:
        for i in data['children']:
            media_url = i['mediaStreamUrl']
            son_title = i['title']
            media_urls.append([media_url, son_title])
    final_data = {"id": id, "title": title, "source_url": f"https://asmr.one/work/{source_id}", "nsfw": nsfw,
                  "mainCoverUrl": mainCoverUrl, "media_urls": media_urls}
    return final_data

async def random_asmr_100(proxy=None):
    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    url='https://api.asmr-200.com/api/works?order=betterRandom'
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url)
        data = response.json()
        #print(data)
        return await get_info(data,proxies)

async def latest_asmr_100(proxy=None):
    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    url='https://api.asmr-200.com/api/works?order=create_date&sort=desc&page=1&subtitle=0'
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url)
        data = response.json()
        print(data)
    return await get_info(data,proxies)
async def choose_from_latest_asmr_100(proxy=None):
    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    url = 'https://api.asmr-200.com/api/works?order=create_date&sort=desc&page=1&subtitle=0'
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url)
        data = response.json()
        #print(data)
    return await get_info(data, proxies, "random")
async def choose_from_hotest_asmr_100(proxy=None):
    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    url="https://api.asmr-200.com/api/recommender/popular"
    payload={"keyword":" ","page":1,"subtitle":0,"localSubtitledWorks":[],"withPlaylistStatus":[]}
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.post(url,json=payload)
        data = response.json()
        return await get_info(data, proxies, "random")
