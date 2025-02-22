import httpx

from plugins.utils.random_str import random_str
from plugins.utils.translate import translate


async def vits(text,speaker,base_url,lang,proxies):
    if lang=="ja":
        text=f"[JA]{translate(text)}[JA]"
    url = f"{base_url}/get_audio"
    params = {
        "text": f"{text}",
        "speaker": speaker
    }
    def fetch():
        response = requests.get(url, params=params)
        return response.content

    audio_content = await asyncio.to_thread(fetch)

    p = f"data/voice/cache/{random_str()}.wav"


    with open(p, "wb") as f:
        f.write(audio_content)
async def get_vits_speakers(base_url,proxies):
    url = f"{base_url}/get_speakers"
    def fetch():
        response = requests.get(url)
        return response.json()

    r = await asyncio.to_thread(fetch)
    return r
