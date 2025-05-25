import httpx

from framework_common.utils.utils import download_img

async def get_nasa_apod(apikey,proxy):
    dataa = {"api_key": apikey}
    if proxy:
        proxies={
            "http://": proxy,
            "https://": proxy
        }
    else:
        proxies=None
    url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
    async with httpx.AsyncClient(proxies=proxies) as client:
        response = await client.get(url=url)
        #print(response.json())
    # logger.info("下载缩略图")
    filename = await download_img(response.json().get("url"),
                                  "data/pictures/cache/" + response.json().get("date") + ".png")
    txta = response.json().get(
        "explanation")  # await translate(response.json().get("explanation"), "EN2ZH_CN")
    txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta

    return filename, txt
