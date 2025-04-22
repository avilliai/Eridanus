import httpx


from framework_common.utils.random_str import random_str



async def get_results(url,proxy=None):
    if proxy is not None and proxy!= "":
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    try:
        async with httpx.AsyncClient(proxies=proxies,timeout=100) as client:
            response = await client.get(url)
    except:
        return []
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
async def ideo_gram(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/ideogram/generate-image?prompt={prompt}"
    return await get_results(url,proxy)

async def bing_dalle3(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/dall-e-3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_speed(prompt,proxy=None):

    url=f"https://apiserver.alcex.cn/flux-speed/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def recraft_v3(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/recraft-v3/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
async def flux_ultra(prompt,proxy=None):
    url=f"https://apiserver.alcex.cn/flux-pro.ultra/generate-image?prompt={prompt}"
    return await get_results(url,proxy)
