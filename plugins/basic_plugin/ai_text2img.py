import httpx

from plugins.utils.utils import random_str


async def bing_dalle3(prompt,proxy=None):
    if proxy is not None:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    print(f"Bing Dalle-3: {prompt} proxy: {proxy}" )
    url=f"https://apiserver.alcex.cn/dall-e-3/generate-image?prompt={prompt}"
    async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
        response = await client.get(url)
        print(response.json())
    if response:
        paths=[]
        d=response.json()["data"]
        for i in d:
            try:
                url=i["url"]
                async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
                    response = await client.get(url)
                p=f"data/pictures/cache/{random_str(10)}.png"
                with open(p,"wb") as f:
                    f.write(response.content)
                paths.append(p)
            except:
                continue
        return paths
    else:
        return []