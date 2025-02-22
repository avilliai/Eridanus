import asyncio

import httpx
import requests


async def translate(text, mode="ZH_CN2JA"):
    try:
        URL = f"https://api.pearktrue.cn/api/translate/?text={text}&type={mode}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(URL)
            #print(r.json()["data"]["translate"])
            return r.json()["data"]["translate"]
    except:
        pass
        if mode != "ZH_CN2JA":
            return text
    try:
        url = f"https://findmyip.net/api/translate.php?text={text}&target_lang=ja"
        r = requests.get(url=url, timeout=10)
        return r.json()["data"]["translate_result"]
    except:
        pass
    try:
        url = f"https://translate.appworlds.cn?text={text}&from=zh-CN&to=ja"
        r = requests.get(url=url, timeout=10, verify=False)
        return r.json()["data"]
    except:
        pass
    return text
