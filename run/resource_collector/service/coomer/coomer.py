import httpx


class Coomer:
    def __init__(self,proxies=None):
        self.base_url = "https://coomer.su/api/v1/posts?q=hentai-tv"
        self.proxies = proxies
    async def get_posts(self,keyword):
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.get(f"{self.base_url}&q={keyword}")
            return response.json()["posts"]
        """
        [
            {
              "id": "885061140",
              "user": "hentai-tv",
              "service": "onlyfans",
              "title": "Hentaiさんへ💕\nhttps://onlyfans.com/870370422/hentai-tv\n別カメラの動画で..",
              "substring": "Hentaiさんへ💕\nhttps://onlyfans.com/870370422/hentai-t",
              "published": "2024-01-11T13:42:28",
              "file": {
                "name": "0hlq0pzh8gqejbplle9qf_source.mp4",
                "path": "/ef/ae/efae044a5b45c9b377b17aa2e2f3aa6514b1fa7c48242c290e0b99bd6ef271f6.mp4"
              },
              "attachments": []
            }]
        """
    pass