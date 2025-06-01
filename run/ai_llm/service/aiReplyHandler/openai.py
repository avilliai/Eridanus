import re

import base64

import httpx

from developTools.utils.logger import get_logger
from framework_common.database_util.llmDB import get_user_history, update_user_history
from framework_common.utils.install_and_import import install_and_import

logger=get_logger()
"""
安全导入
"""


openai = install_and_import('openai')

if openai:
    from openai import AsyncOpenAI



BASE64_PATTERN = re.compile(r"^data:([a-zA-Z0-9]+/[a-zA-Z0-9-.+]+);base64,([A-Za-z0-9+/=]+)$")
async def openaiRequest(ask_prompt,url: str,apikey: str,model: str,stream: bool=False,proxy=None,tools=None,instructions=None,temperature=1.3,max_tokens=2560):
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
    "stream": stream,
    "temperature": temperature,
    "max_tokens": max_tokens,
  }

    if tools is not None:
        data["tools"] = tools
        data["tool_choice"]="auto"
    async with httpx.AsyncClient(proxies=proxies, headers=headers, timeout=200) as client:
        r = await client.post(url, json=data)  # 使用 `json=data`
        print(r.json())
        return r.json()["choices"][0]["message"]
async def openaiRequest_official(ask_prompt,url: str,apikey: str,model: str,stream: bool=False,proxy=None,tools=None,instructions=None,temperature=1.3,max_tokens=2560):
    """
    使用官方sdk
    :param ask_prompt:
    :param url:
    :param apikey:
    :param model:
    :param stream:
    :param proxy:
    :param tools:
    :param instructions:
    :param temperature:
    :param max_tokens:
    :return:
    """
    #print(ask_prompt)
    kwargs = {
        "model": model,
        "messages": ask_prompt,
        "stream": stream,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # 仅当 tools 不为 None 时添加它
    if tools is not None:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"


    client = AsyncOpenAI(api_key=apikey, base_url=url)

    async def get_response():
        response =await client.chat.completions.create(**kwargs)

        #response = await client.chat.completions.create(**kwargs)
        print(response)
        response_dict=response.model_dump()
        return response_dict["choices"][0]["message"]
        #print(response.choices[0].message.content)
    return await get_response()




async def prompt_elements_construct(precessed_message,bot=None,func_result=False,event=None):
    prompt_elements = []

    for i in precessed_message:
        if "text" in i and i["text"]!="":
            prompt_elements.append({"type":"text", "text":i["text"]})
        elif "image" in i or "mface" in i:
            if "mface" in i:
                url = i["mface"]["url"]
            else:
                try:
                    url = i["image"]["url"]
                except:
                    url = i["image"]["file"]
            base64_match = BASE64_PATTERN.match(url)
            if base64_match:
                img_base64 = base64_match.group(2)
                prompt_elements.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                })
                continue
            prompt_elements.append({"type":"text","text": f"system提示: 当前图片的url为{url}"})
            # 下载图片转base64
            async with httpx.AsyncClient(timeout=60) as client:
                res = await client.get(url)
                img_base64 =base64.b64encode(res.content).decode("utf-8")

            prompt_elements.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                })
        elif "reply" in i:
            try:
                event_obj=await bot.get_msg(int(event.get("reply")[0]["id"]))
                message = await prompt_elements_construct(event_obj.processed_message,bot)
                prompt_elements.extend(message["content"])
            except Exception as e:
                logger.warning(f"引用消息解析失败:{e}")
        else:
            prompt_elements.append({"type":"text", "text":str(i)})  # 不知道还有什么类型，都需要做对应处理的，唉，任务还多着呢。
    if func_result:
        return {"role": "system", "content": prompt_elements}
    return {"role": "user", "content": prompt_elements}
async def construct_openai_standard_prompt(processed_message,system_instruction,user_id,bot=None,func_result=False,event=None):
    message=await prompt_elements_construct(processed_message,bot,func_result,event)
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(message)
    if system_instruction:
        full_prompt = [

        ]
        try:
            history.index({"role": "system", "content": [{"type": "text", "text": system_instruction}]})
        except ValueError:
            full_prompt.append({"role": "system", "content": [{"type": "text", "text": system_instruction}]})
        full_prompt.extend(history)
    else:
        full_prompt = history
    await update_user_history(user_id, full_prompt)  # 更新数据库中的历史记录
    return full_prompt, original_history
"""
旧版prompt都是谁在用啊，原来是你啊deepseek
"""
async def construct_openai_standard_prompt_old_version(processed_message,system_instruction,user_id,bot=None,func_result=False,event=None):
    message = await prompt_elements_construct_old_version(processed_message, bot, func_result, event)
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(message)
    if system_instruction:
        full_prompt = [

        ]
        try:
            history.index({"role": "user", "content": system_instruction})
        except ValueError:
            full_prompt.append({"role": "user", "content": system_instruction})
            full_prompt.append({"role": "assistant", "content": "好的，在接下来的回复中我会扮演好自己的角色"})

        full_prompt.extend(history)
    else:
        full_prompt = history
    await update_user_history(user_id, full_prompt)  # 更新数据库中的历史记录
    return full_prompt, original_history
async def prompt_elements_construct_old_version(precessed_message,bot=None,func_result=False,event=None):
    result = "".join(item.get("text", "") for item in precessed_message)
    if result:
        prompt_elements=result
    else:
        prompt_elements=str(precessed_message)
    return {"role": "user", "content": prompt_elements}

async def get_current_openai_prompt(user_id):
    history = await get_user_history(user_id)
    return history
async def add_openai_standard_prompt(prompt,user_id):
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(prompt)

    await update_user_history(user_id, history)  # 更新数据库中的历史记录
    return history, original_history