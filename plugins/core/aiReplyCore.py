import asyncio
import json
import os
import random
import time
from collections import defaultdict

import httpx

from developTools.message.message_components import Record
from developTools.utils.logger import get_logger
from plugins.core.llmDB import get_user_history, update_user_history
from plugins.core.tts import tts
from plugins.core.userDB import get_user
from plugins.core.aiReply_utils import construct_openai_standard_prompt, construct_gemini_standard_prompt
from plugins.func_map import call_func
last_trigger_time = defaultdict(float)

logger=get_logger()
async def judge_trigger(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False):
    trigger = False
    if event.user_id in last_trigger_time:
        bot.logger.info(f"last_trigger_time: {last_trigger_time.get(event.user_id)}")
        if (time.time() - last_trigger_time.get(event.user_id)) <= config.api["llm"]["focus_time"]:
            trigger = True
        else:
            last_trigger_time.pop(event.user_id)
            trigger = False
    if trigger:
        r=await aiReplyCore(processed_message,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=func_result)
        return r
    else:
        return None
async def end_chat(user_id):
    try:
        last_trigger_time.pop(user_id)
    except:
        print("end_chat error。已不存在对应trigger")
async def aiReplyCore(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    reply_message = ""
    if not system_instruction:
        system_instruction = config.api["llm"]["system"]
        user_info=await get_user(user_id)
        system_instruction=system_instruction.replace("{用户}",user_info[1]).replace("{bot_name}",config.basic_config["bot"]["name"])
    try:
        if config.api["llm"]["model"]=="openai":
            prompt, original_history = await construct_openai_standard_prompt(processed_message,system_instruction, user_id)
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
            last_trigger_time[user_id] = time.time()
            """
            openai标准函数调用还没做。待处理
            """
            #检查是否存在函数调用，如果还有提示词就发
            status=False
            if "tool_calls" in response_message:
                status=True
            generate_voice=False
            if status and reply_message is not None: #有函数调用且有回复，就发回复和语音
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
                    generate_voice=True
                else:
                    await bot.send(event, reply_message, config.api["llm"]["Quote"])
            if "tool_calls" in response_message:
                for part in response_message['tool_calls']:
                #目前不太确定多个函数调用的情况，先只处理第一个。
                    func_name = part['function']["name"]
                    args = part['function']['arguments']
                    try:
                        r=await call_func(bot, event, config,func_name, json.loads(args)) #真是到处都不想相互兼容。
                        if r==False:
                            await end_chat(user_id)
                    except Exception as e:
                        #logger.error(f"Error occurred when calling function: {e}")
                        raise Exception(f"Error occurred when calling function: {e}")

                    #函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message=None

                if generate_voice and reply_message:
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path = await tts(reply_message, config=config)
                        await bot.send(event, Record(file=path))
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
            #print(response_message)
        elif config.api["llm"]["model"]=="gemini":
            prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, bot,func_result)

            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction)
            #print(response_message)
            try:
                reply_message=response_message["parts"][0]["text"]  #函数调用可能不给你返回提示文本，只给你整一个调用函数。
            except:
                reply_message=None
            last_trigger_time[user_id] = time.time()
            #检查是否存在函数调用，如果还有提示词就发
            status=False
            for part in response_message["parts"]:
                if "functionCall" in part:
                    status=True
            generate_voice=False
            if status and reply_message is not None: #有函数调用且有回复，就发回复和语音
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
                    generate_voice=True
                else:
                    await bot.send(event, reply_message, config.api["llm"]["Quote"])

            for part in response_message["parts"]:
                if "functionCall" in part:               #目前不太确定多个函数调用的情况，先只处理第一个。
                    func_name = part['functionCall']["name"]
                    args = part['functionCall']['args']
                    try:
                         #只能在这里导入，否则会循环导入，解释器会不给跑。
                        r=await call_func(bot, event, config,func_name, args)
                        if r==False:
                            await end_chat(user_id)
                    except Exception as e:
                        #logger.error(f"Error occurred when calling function: {e}")
                        raise Exception(f"Error occurred when calling function: {e}")

                    #函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message=None

            if generate_voice and reply_message is not None:
                try:
                    bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                    path = await tts(reply_message, config=config)
                    await bot.send(event, Record(file=path))
                except Exception as e:
                    bot.logger.error(f"Error occurred when calling tts: {e}")
                if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                    await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])

        #更新数据库中的历史记录
        history = await get_user_history(user_id)
        if len(history) > config.api["llm"]["max_history_length"]:
            del history[0]
            del history[0]
        history.append(response_message)
        await update_user_history(user_id, history)
        #处理工具调用，但没做完，一用gemini函数调用就给我RESOURCE_EXHAUSTED，受不了一点byd

            #print(f"funccall result:{r}")
            #return r
            #ask = await prompt_elements_construct(r)
            #response_message = await aiReplyCore(ask,user_id,config,tools=tools)
        logger.info(f"aiReplyCore returned: {reply_message}")
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        await update_user_history(user_id, original_history)
        logger.error(f"Error occurred: {e}")
        raise  # 继续抛出异常以便调用方处理



async def openaiRequest(ask_prompt,url: str,apikey: str,model: str,stream: bool=False,proxy=None,tools=None,instructions=None):
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
        pay_load["tools"] = tools  #h函数调用开个头得了。之后再做。


    async with httpx.AsyncClient(proxies=proxies, timeout=100) as client:
        r = await client.post(url, json=pay_load)
        print(r.json())
        return r.json()['candidates'][0]["content"]

#asyncio.run(openaiRequest("1"))