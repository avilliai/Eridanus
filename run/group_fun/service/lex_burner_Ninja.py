import asyncio

import httpx


class Lexburner_Ninja:
    def __init__(self):
        self.name = "Lexburner_Ninja"

    async def query_ninjutsu(self, name):
        async with httpx.AsyncClient() as client:
            # 直接调用 API 获取搜索结果
            url = f"https://wsfrs.com/api/jutsus?search={name}&limit=10&sortBy=weighted"
            response = await client.get(url)
            if response.status_code != 200:
                return {"error": f"API request failed with status {response.status_code}"}

            data = response.json()
            jutsus = data.get("jutsus", [])
            if not jutsus:
                return {"error": "No jutsus found for the search term"}

            first_jutsu = jutsus[0]
            # print(first_jutsu)
            return {
                "title": first_jutsu.get("name", "未找到标题"),
                "description": first_jutsu.get("description", "未找到描述"),
                "tags": [tag["name"] for tag in first_jutsu.get("tags", [])],
                "videoLink": first_jutsu.get("videoLink", "未找到视频链接"),  # 假设 API 返回视频链接
                "related_jutsus": [],  # API 可能不包含相关忍术，需单独处理
                "creator": first_jutsu.get("creator", {}).get("username", "未知作者"),
                "averageRating": first_jutsu.get("averageRating", 0),
                "commentCount": first_jutsu.get("_count", {}).get("comments", 0),
                "ratingCount": first_jutsu.get("_count", {}).get("ratings", 0)
            }

    async def random_ninjutsu(self):
        async with httpx.AsyncClient() as client:
            url = "https://wsfrs.com/api/jutsus?limit=1&sortBy=random"
            response = await client.get(url)

            data = response.json()
            jutsus = data.get("jutsus", [])

            return jutsus[0]


if __name__ == '__main__':
    ninja = Lexburner_Ninja()
    print(asyncio.run(ninja.random_ninjutsu()))
    print(asyncio.run(ninja.query_ninjutsu("手")))
