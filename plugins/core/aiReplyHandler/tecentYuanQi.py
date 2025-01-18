import httpx

from plugins.core.llmDB import get_user_history, update_user_history


async def YuanQiTencent(prompt,assistant_id,token,userID):
    url = 'https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions'
    headers = {
        'X-Source': 'openapi',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "assistant_id": assistant_id,
        "user_id": str(userID),
        "stream": False,
        "messages": prompt
    }
    async with httpx.AsyncClient(headers=headers, timeout=200) as client:
        r = await client.post(url, json=data)  # 使用 `json=data`
        print(r.json())
        return r.json()["choices"][0]["message"]
"""
从processed_message构造腾讯元器标准的prompt
"""


async def tecent_prompt_elements_construct(precessed_message,bot=None,func_result=False):
    prompt_elements = []

    for i in precessed_message:
        if "text" in i:
            prompt_elements.append({"type":"text", "text":i["text"]})
            '''elif "image" in i or "mface" in i:
                if "mface" in i:
                    url = i["mface"]["url"]
                else:
                    url = i["image"]["url"]
                prompt_elements.append({"type":"text","text": f"system提示: 当前图片的url为{url}"})
    
                prompt_elements.append({
                    "type": "file_url",
                    "file_url": {"type": "image", "url": url}
                    })''' #啥比腾讯，兼容做的和矢一样
        else:
            prompt_elements.append({"type":"text", "text":str(i)})  # 不知道还有什么类型，都需要做对应处理的，唉，任务还多着呢。
    if func_result:
        return {"role": "system", "content": prompt_elements}
    return {"role": "user", "content": prompt_elements}
async def construct_tecent_standard_prompt(processed_message,user_id):
    message=await tecent_prompt_elements_construct(processed_message,func_result=False)
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(message)

    full_prompt=history
    await update_user_history(user_id, full_prompt)  # 更新数据库中的历史记录
    return full_prompt, original_history