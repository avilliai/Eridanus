import asyncio
import os
import random

import httpx

from plugins.core.llmDB import get_user_history, update_user_history

proxies={"http://": "http://127.0.0.1:10809", "https://": "http://127.0.0.1:10809"}
async def constructPrompt(message,user_id,config):
    history =await get_user_history(user_id)
    history.append(message)

    full_prompt = [
        {"role": "system", "content": [{"type": "text", "text": config.api["llm"]["system"]}]},
    ]
    full_prompt.extend(history)
    await update_user_history(user_id, history)  # 更新数据库中的历史记录
    return full_prompt
async def aiReplyCore(message,user_id,config):
    prompt = await constructPrompt(message,user_id,config)
    print(prompt)
    if config.api["llm"]["model"]=="openai":
        response_message=await openaiRequest(prompt,config.api["llm"]["openai"]["quest_url"],random.choice(config.api["llm"]["openai"]["api_keys"]),config.api["llm"]["openai"]["model"],False,config.api["proxy"]["http_proxy"])

    #更新数据库中的历史记录
    history = await get_user_history(user_id)
    history.append(response_message)
    await update_user_history(user_id, history)
    return response_message


async def openaiRequest(ask_prompt,url: str,apikey: str,model: str,stream: bool=False,proxy=None):
    if proxy is not None:
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apikey}"
    }
    data={
    "model": model,
    "messages": ask_prompt,
    "stream": stream
  }
    async with httpx.AsyncClient(proxies=proxies, headers=headers, timeout=200) as client:
        r = await client.post(url, json=data)  # 使用 `json=data`
        print(r.json())
        return r.json()["choices"][0]["message"]
#asyncio.run(openaiRequest("1"))