import asyncio
from httpx import AsyncClient
import os

async def anime_trace(image_source)->list[str,str,bool]:
    """
    ai检测，返回结果。识别角色
    """
    url = "https://api.animetrace.com/v1/search"
    data = {
        "is_multi": 0,
        "model": "animetrace_high_beta",
        "ai_detect": "True",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    }
    ai_work=False
    async def get_data():
        async with AsyncClient(trust_env=False) as client:
            try:
                if image_source.startswith("http"):
                    data["url"] = image_source
                    res = await client.post(url=url, headers=headers, data=data, timeout=30)
                else:
                    if not os.path.exists(image_source):
                        raise FileNotFoundError(f"Image file '{image_source}' not found")
                    with open(image_source, "rb") as f:
                        files = {"file": (os.path.basename(image_source), f, "image/jpeg")}
                        res = await client.post(url=url, headers=headers, data=data, files=files, timeout=30)
                content = res.json()
                if content["ai"]:
                    ai_work=True
                if data["model"] == "animetrace_high_beta":
                    a = "anime"
                else:
                    a = "galgame"
                str_result = f"角色识别|{a}模型搜索结果：\n"
                for result in content["data"][0]["character"]:
                    #print(result)
                    str_result += f"{result['work']} ({result['character']}%)\n"
                    if content["data"][0]["character"].index(result)>2:
                        break
                return str_result
            except Exception as e:
                print(f"Error: {str(e)}")
                return None
    anime_res=await get_data()
    data["model"] = "full_game_model_kira"
    game_res=await get_data()
    return [anime_res,game_res,ai_work]

# Example usage
if __name__ == "__main__":
    # Replace 'test.jpg' with the path to an actual image file
    anime_res=asyncio.run(anime_trace("D:\BlueArchive\Eridanus\img.png"))
    print(anime_res)
