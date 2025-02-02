import httpx
import base64
import io

import httpx
from PIL import Image

from plugins.core.llmDB import get_user_history, update_user_history
from plugins.utils.random_str import random_str

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
"""
从processed_message构造openai标准的prompt
"""


async def prompt_elements_construct(precessed_message,bot=None,func_result=False,event=None):
    prompt_elements = []

    for i in precessed_message:
        if "text" in i and i["text"]!="":
            prompt_elements.append({"type":"text", "text":i["text"]})
        elif "image" in i or "mface" in i:
            if "mface" in i:
                url = i["mface"]["url"]
            else:
                url = i["image"]["url"]
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
                bot.logger.warning(f"引用消息解析失败:{e}")
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
            {"role": "system", "content": [{"type": "text", "text": system_instruction}]},
        ]
        full_prompt.extend(history)
    else:
        full_prompt = history
    await update_user_history(user_id, full_prompt)  # 更新数据库中的历史记录
    return full_prompt, original_history
async def get_current_openai_prompt(user_id):
    history = await get_user_history(user_id)
    return history
async def add_openai_standard_prompt(prompt,user_id):
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(prompt)

    await update_user_history(user_id, history)  # 更新数据库中的历史记录
    return history, original_history