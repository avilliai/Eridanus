import asyncio
import requests

from framework_common.utils.random_str import random_str


async def vits(text,speaker,base_url):
    url = f"{base_url}/get_audio"
    params = {
        "text": f"{text}",
        "speaker": speaker
    }
    def fetch():
        response = requests.get(url, params=params)
        return response.content

    audio_content = await asyncio.to_thread(fetch)

    p = f"data/voice/cache/{random_str()}.mp3"


    with open(p, "wb") as f:
        f.write(audio_content)
    return p
async def get_vits_speakers(base_url,proxies):
    url = f"{base_url}/get_speakers"
    def fetch():
        response = requests.get(url)
        return response.json()

    r = await asyncio.to_thread(fetch)
    return r
