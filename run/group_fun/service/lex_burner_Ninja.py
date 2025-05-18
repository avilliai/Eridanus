import asyncio
import httpx


class Lexburner_Ninja:
    def __init__(self):
        self.name = "Lexburner_Ninja"
    async def Ninjutsu_query(self,Ninjutsu_name):
        async with httpx.AsyncClient() as client:
            pass
    async def random_ninjutsu(self):
        async with httpx.AsyncClient() as client:
            url="https://wsfrs.com/api/jutsus?limit=1&sortBy=random"
            response = await client.get(url)
            data = response.json()
            return data['jutsus'][0]