import httpx
from xpinyin import Pinyin
p = Pinyin()
async def weather_query(proxy,api_key,location):
    location = location.replace('市','')
    location = p.get_pinyin(location, '')

    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    async with httpx.AsyncClient(proxies=proxies) as client:
        r = await client.get(f"https://api.seniverse.com/v3/weather/daily.json?key={api_key}&location={location}&language=zh-Hans&unit=c&start=0&days=5")
        data = r.json()
        #print(data)
        return data["results"]
async def free_weather_query(city):
    async with httpx.AsyncClient() as client:
        r=await client.get(f"https://api.52vmy.cn/api/query/tian/three?city={city}")
        data=r.json()
        return data["data"]
