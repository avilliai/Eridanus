import httpx

async def pic_audit_standalone(
        img_base64,
        is_return_tags=False,
        audit=False,
        return_none=False,
        url = "http://server.20020026.xyz:7865"
):

    async def get_caption(payload):
        async with httpx.AsyncClient(timeout=1000) as client:
            try:
                response = await client.post(
                    url=f"{url}/tagger/v1/interrogate",# http://server.20020026.xyz:7865
                    json=payload
                )
                response.raise_for_status()  # 抛出异常，如果请求失败
                return response.json()
            except httpx.HTTPStatusError as e:
                #logger.error(f"API失败，错误信息: {e.response.status_code}, {await e.response.text()}")
                return None

    payload = {"image": img_base64, "model": "wd14-vit-v2-git", "threshold": 0.35}

    resp_dict = await get_caption(payload)

    if not resp_dict:
        return None

    tags = resp_dict["caption"]
    replace_list = ["general", "sensitive", "questionable", "explicit"]
    to_user_list = ["这张图很安全!", "较为安全", "色情", "泰色辣!"]
    possibilities = {}
    to_user_dict = {}
    message = "这是审核结果:\n"

    for i, to_user in zip(replace_list, to_user_list):
        possibilities[i] = tags[i]
        percent = f":{tags[i] * 100:.2f}".rjust(6)
        message += f"[{to_user}{percent}%]\n"
        to_user_dict[to_user] = tags[i]

    value = list(to_user_dict.values())
    value.sort(reverse=True)
    reverse_dict = {v: k for k, v in to_user_dict.items()}
    message += (f"最终结果为:{reverse_dict[value[0]].rjust(5)}")
    
    keys = list(tags.keys())
    tags_str = ", ".join(keys)

    if return_none:
        value = list(possibilities.values())
        value.sort(reverse=True)
        reverse_dict = {v: k for k, v in possibilities.items()}
        #logger.info(message)
        return True if reverse_dict[value[0]] == "questionable" or reverse_dict[value[0]] == "explicit" else False

    if is_return_tags:
        return message, tags, tags_str
    if audit:
        return possibilities, message
    return message