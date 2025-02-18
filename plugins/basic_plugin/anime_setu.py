import asyncio
import httpx


async def anime_setu(tags:list,num:int=1,r18:bool=False,proxies=None):
    tags = [tag for tag in tags if tag not in ('涩图', '色图')]
    tags = "AND".join(tags)
    #print(tags)
    if r18:
        r18='true'
    else:
        r18='false'
    url=f"https://api.hikarinagi.com/random/v2/?tag={tags}&num={num}&r-18={r18}"
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url)
        return response.json()
async def anime_setu1(tags:list,num:int=1,r18:bool=False):
    tags = [tag for tag in tags if tag not in ('涩图', '色图')]
    #tags = "AND".join(tags)
    r18=2 if r18 else 0
    #print(tags)
    data={"tag":tags,"num":num,"r18":r18,"size": "regular"}
    url = "https://api.lolicon.app/setu/v2"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.get(url, params=data)
        #print(r.json())
        return r.json()["data"]
#asyncio.run(anime_setu1(["萝莉"],3))