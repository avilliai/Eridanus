import asyncio
import httpx


class OttoTTS:
    def __init__(self):
        pass
    async def speak(self, text):
        origin_url="https://ottohzys.wzq02.top//make"
        data={
            "text": text,
            "inYsddMode": False,
            "norm": False,
            "reverse": False,
            "speedMult": 1.2,
            "pitchMult": 1,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(origin_url, data=data)
            return await self.download_audio(response.json()["id"])
    async def download_audio(self,audio_id):
        audio_url=f"https://ottohzys.wzq02.top//get/{audio_id}.ogg"
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url)
            path=f"data/voice/cache/{audio_id}.ogg"
            with open(path, "wb") as f:
                f.write(response.content)
            return path
if __name__=="__main__":
    otto=OttoTTS()
    text="你好，我是忍者，今天来教大家释放忍术"
    r=asyncio.run(otto.speak(text))