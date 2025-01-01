import asyncio
import os
import random

import httpx

from developTools.utils.logger import get_logger
from plugins.core.aiReply_utils import construct_openai_standard_prompt, construct_gemini_standard_prompt
from plugins.core.llmDB import delete_user_history

logger=get_logger()
async def simple_aiReplyCore(processed_message,config,model=None): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"simple_aiReplyCore called with message: {processed_message}")
    reply_message = ""
    try:
        if config.api["llm"]["model"] == "openai":
            prompt, original_history = await construct_openai_standard_prompt(processed_message, "你是一个ai助手",00000)
            response_message = await openaiRequest(
                prompt,
                config.api["llm"]["openai"]["quest_url"],
                random.choice(config.api["llm"]["openai"]["api_keys"]),
                config.api["llm"]["openai"]["model"],
                False,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
            )
            reply_message = response_message["content"]
            #print(response_message)
        elif config.api["llm"]["model"]=="gemini":
            prompt, original_history = await construct_gemini_standard_prompt(processed_message, 00000)
            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None)
            #print(response_message)
            try:
                reply_message=response_message["parts"][0]["text"]  #函数调用可能不给你返回提示文本，只给你整一个调用函数。
            except:
                reply_message=None

        #logger.info(f"aiReplyCore returned: {reply_message}")
        await delete_user_history(00000)
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        await delete_user_history(00000)
        logger.error(f"Error occurred: {e}")
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
        #print(r.json())
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
        "safetySettings": [
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_HARASSMENT', "threshold": "BLOCK_None"},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', "threshold": "BLOCK_None"}],
    }
    if tools is not None:
        pay_load["tools"] = tools  #h函数调用开个头得了。之后再做。

    async with httpx.AsyncClient(proxies=proxies, timeout=100) as client:
        r = await client.post(url, json=pay_load)

        return r.json()['candidates'][0]["content"]

#asyncio.run(openaiRequest("1"))