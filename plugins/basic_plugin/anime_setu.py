import asyncio
import httpx


async def anime_setu(tags:list,num:int=1,r18:bool=False):
    tags = [tag for tag in tags if tag not in ('涩图', '色图')]
    tags = "AND".join(tags)
    tags = tags.replace("涩图","").replace("色图","") #ai会把这个也识别为tag
    url=f"https://api.hikarinagi.com/random/v2/?tag={tags}&num={num}&r-18={r18}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


#asyncio.run(anime_setu(["hentai","yuri"]))