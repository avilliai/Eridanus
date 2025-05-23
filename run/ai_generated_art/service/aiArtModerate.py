import httpx


async def aiArtModerate(imgurl,api_user,api_secret):
    params = {
        'url': f'{imgurl}',
        'models': 'genai',
        'api_user': f'{api_user}',
        'api_secret': f'{api_secret}'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.sightengine.com/1.0/check.json', params=params)
        data = response.json()
    return data["type"]['ai_generated']*100