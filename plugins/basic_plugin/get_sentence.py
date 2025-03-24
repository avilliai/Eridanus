import httpx
async def get_en(api,a,b):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(api)
        first = response.json()['data'].get(a)
        second = response.json()['data'].get(b)
    return first + '\n' + second
async def get_common(api):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(api)
        return response.content.decode('utf-8')
async def get_news(api):
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(api)
        with open('djt.png', 'wb') as f:
            f.write(response.content)
