import httpx

from framework_common.database_util.llmDB import get_user_history, update_user_history


async def YuanQiTencent(prompt: list, assistant_id, token, userID):
    url = 'https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions'
    headers = {
        'X-Source': 'openapi',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    prompt.insert(0, {"role": "user", "content": [{"type": "text", "text": "你好"}]})
    prompt.insert(1, {"role": "assistant", "content": [{"type": "text", "text": "你好呀~"}]})
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


async def tecent_prompt_elements_construct(precessed_message, bot=None, func_result=False, event=None):
    prompt_elements = []

    for i in precessed_message:
        if "text" in i:
            prompt_elements.append({"type": "text", "text": i["text"]})
        elif "image" in i or "mface" in i:
            if "mface" in i:
                url = i["mface"]["url"]
            else:
                try:
                    url = i["image"]["url"]
                except:
                    url = i["image"]["file"]
            prompt_elements.append({"type": "text", "text": f"system提示: 当前图片的url为{url}"})

            prompt_elements.append({
                "type": "file_url",
                "file_url": {"type": "image", "url": url}
            })
        elif "reply" in i:
            try:
                event_obj = await bot.get_msg(int(event.get("reply")[0]["id"]))
                message = await tecent_prompt_elements_construct(event_obj.processed_message, bot)
                prompt_elements.extend(message["content"])
            except Exception as e:
                bot.logger.warning(f"引用消息解析失败:{e}")
        else:
            prompt_elements.append({"type": "text", "text": str(i)})
    if func_result:
        return {"role": "system", "content": prompt_elements}
    return {"role": "user", "content": prompt_elements}


async def construct_tecent_standard_prompt(processed_message, user_id, bot, event):
    message = await tecent_prompt_elements_construct(processed_message, func_result=False, bot=bot, event=event)
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(message)

    full_prompt = history
    await update_user_history(user_id, full_prompt)  # 更新数据库中的历史记录
    return full_prompt, original_history