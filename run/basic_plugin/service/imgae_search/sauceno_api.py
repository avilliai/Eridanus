import asyncio
from httpx import AsyncClient
import os

async def saucenao(image_source, apiKey,proxies=None)->list[list[str,str]]:
    """
    sauceno
    """
    url = "https://saucenao.com/search.php"
    data = {
        'url': image_source,
        'output_type': '2',
        'api_key': apiKey,
    }

    def extract_results(data):
        # Extract the first three results (or fewer if less than three are available)
        results = data.get('results', [])[:2]

        # Create a list to store the concatenated strings
        results_data = []

        for result in results:
            header = result.get('header', {})
            data = result.get('data', {})

            result_str = ""
            result_str += f"saucenao搜图结果：\n相似度: {header.get('similarity', '')}\n"
            for key, value in data.items():
                result_str += f"{key}: {value}\n "

            result_str = result_str.rstrip(", ")

            results_data.append([header.get('thumbnail'), result_str])

        return results_data
    async with AsyncClient(proxies=proxies) as client:
        response = await client.post(url, data=data)

        return extract_results(response.json())






# Example usage
if __name__ == "__main__":
    # Replace 'test.jpg' with the path to an actual image file
    anime_res=asyncio.run(sauceno("https://multimedia.nt.qq.com.cn/download?appid=1406&fileid=EhRq8Zf3Qv-XjJsas9Amk4cVErIziBiJihIg_gooppGTgNXwjAMyBHByb2RQgLsvWhDFcH7f9X7NnVwae5oKTZ9negK9ag&spec=0&rkey=CAESKBkcro_MGujoaVbNUyDExifqFmLH1P-PMnmpir0K1TjvFScqGJSs8A8","e3c085a454b08ca07641284b0eab3753b16e2654"))
    print(anime_res)
