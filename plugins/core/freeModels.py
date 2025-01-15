import json

import asyncio
import httpx


async def meta_llama(prompt, proxies):
    url = "https://apiserver.alcex.cn/v1/chat/completions"
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": prompt,
        "stream": False
    }
    async with httpx.AsyncClient(proxies=proxies, timeout=200) as client:
        r = await client.post(url, json=data)

        return r.json()["choices"][0]["message"]


async def free_phi_3_5(prompt,proxies):
    url = "https://apiserver.alcex.cn/v1/chat/completions"
    data = {
        "model": "phi-3.5",
        "messages": prompt,
        "stream": False
    }
    async with httpx.AsyncClient(proxies=proxies, timeout=200) as client:
        r = await client.post(url, json=data)

        return r.json()["choices"][0]["message"]


async def free_gemini(prompt,proxies):
    url = f"https://apiserver.alcex.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "sl-session=Ei97VrWfame4ViswzDZ/IQ=="
    }
    data ={
        "model": "gemini-1.5-flash",
        "messages": prompt,
        "stream": False
    }

    async with httpx.AsyncClient(proxies=proxies, headers=headers, timeout=200) as client:
        r = await client.post(url, json=data)

        return r.json()["choices"][0]["message"]
async def free_model_result(prompt, proxies=None):
    functions = [
        meta_llama(prompt,proxies),
        free_phi_3_5(prompt, proxies),
        free_gemini(prompt,proxies)
    ]

    for future in asyncio.as_completed(functions):
        try:
            result = await future
            if result:
                if result["content"]!= "" and result["content"]!= "You've reached your free usage limit today":
                    return result
        except Exception as e:
            print(f"Task failed: {e}")
