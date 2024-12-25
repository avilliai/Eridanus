import asyncio
import os
import random

import httpx

from plugins.core.llmDB import get_user_history, update_user_history
from plugins.core.utils import construct_openai_standard_prompt, construct_gemini_standard_prompt
from plugins.func_map import call_func, gemini_func_map

proxies={"http://": "http://127.0.0.1:10809", "https://": "http://127.0.0.1:10809"}

async def aiReplyCore(processed_message,user_id,config,tools=None):
    reply_message = ""
    try:
        if config.api["llm"]["model"]=="openai":
            prompt, original_history = await construct_openai_standard_prompt(processed_message, user_id, config)
            response_message = await openaiRequest(
                prompt,
                config.api["llm"]["openai"]["quest_url"],
                random.choice(config.api["llm"]["openai"]["api_keys"]),
                config.api["llm"]["openai"]["model"],
                False,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
            )
            reply_message=response_message["content"]
            #print(response_message)
        elif config.api["llm"]["model"]=="gemini":
            prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, config)
            system_instruction=config.api["llm"]["system"]
            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction)
            print(response_message)

            reply_message=response_message["parts"][0]["text"]
        #更新数据库中的历史记录
        history = await get_user_history(user_id)
        if len(history) > config.api["llm"]["max_history_length"]:
            del history[0]
            del history[0]
        history.append(response_message)
        await update_user_history(user_id, history)
        #处理工具调用，但没做完，一用gemini函数调用就给我RESOURCE_EXHAUSTED，受不了一点byd
        if "toolCalls" in response_message:
            for future_funcs in response_message["toolCalls"]:
                r=await call_func(future_funcs["function"]["name"],future_funcs["function"]["arguments"])
            #print(f"funccall result:{r}")
            #return r
            #ask = await prompt_elements_construct(r)
            #response_message = await aiReplyCore(ask,user_id,config,tools=tools)
        return reply_message
    except Exception as e:
        await update_user_history(user_id, original_history)
        print(f"Error occurred: {e}")
        raise  # 继续抛出异常以便调用方处理



async def openaiRequest(ask_prompt,url: str,apikey: str,model: str,stream: bool=False,proxy=None,tools=None):
    if proxy is not None and proxy !="":
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
    if tools is not None:
        data["tools"] = tools
        data["tool_choice"]="auto"
    async with httpx.AsyncClient(proxies=proxies, headers=headers, timeout=200) as client:
        r = await client.post(url, json=data)  # 使用 `json=data`
        print(r.json())
        return r.json()["choices"][0]["message"]
async def geminiRequest(ask_prompt,base_url: str,apikey: str,model: str,proxy=None,tools=None,system_instruction=None):
    if proxy is not None and proxy !="":
        proxies={"http://": proxy, "https://": proxy}
    else:
        proxies=None
    url = f"{base_url}/v1beta/models/{model}:generateContent?key={apikey}"
    # print(requests.get(url,verify=False))

    pay_load={
        "contents": ask_prompt,
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instruction,
                }
            ]
        },
        "safetySettings": [
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HARASSMENT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', "threshold": "BLOCK_None"}],
    }
    if tools is not None:
        pay_load["tools"] = tools
    async with httpx.AsyncClient(proxies=proxies, timeout=100) as client:
        r = await client.post(url, json=pay_load)
        print(r.json())

        return r.json()['candidates'][0]["content"]

#asyncio.run(openaiRequest("1"))