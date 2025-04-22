import httpx

from framework_common.utils.utils import get_headers


async def cccdddm(musicname):
    url = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s=' + musicname + '&type=1&offset=0&total=true&limit=20'
    async with httpx.AsyncClient(timeout=None, headers=get_headers()) as client:
        r = await client.post(url)
        #print(r.json().get("result").get("songs"))
        #print(r.json().get("result").get("songs")[0].get("id"))
        newa = []
        for i in r.json().get("result").get("songs"):
            #newa.append([i.get("name"),i.get("id"),i.get("artists")[0].get("img1v1Url"),i.get("artists")[0].get("name")])
            newa.append(
                [i.get("name"), i.get("id"), i.get("artists")[0].get("name")])
        return newa
