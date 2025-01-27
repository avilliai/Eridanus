import base64
import io

import httpx
from PIL import Image

from plugins.core.llmDB import get_user_history, update_user_history
from plugins.utils.random_str import random_str


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

"""
gemini标准prompt构建
"""
async def gemini_prompt_elements_construct(precessed_message,bot=None,func_result=False,event=None):
    prompt_elements=[]

    #{"role": "assistant","content":[{"type":"text","text":i["text"]}]}
    for i in precessed_message:
        if "text" in i:
            prompt_elements.append({"text": i["text"]})
        elif "image" in i or "mface" in i:
            if "mface" in i:
                url=i["mface"]["url"]
            else:
                url=i["image"]["url"]
            prompt_elements.append({"text": f"system提示: 当前图片的url为{url}"})
            # 下载图片转base64
            async with httpx.AsyncClient(timeout=60) as client:
                res = await client.get(url)
                # res.raise_for_status()  # Check for HTTP errors

                image = Image.open(io.BytesIO(res.content))
                image = image.convert("RGB")

                quality = 85
                while True:
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='JPEG', quality=quality)
                    size_kb = img_byte_arr.tell() / 1024
                    if size_kb <= 400 or quality <= 10:
                        break
                    quality -= 5
                img_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            prompt_elements.append({"inline_data": {"mime_type": "image/jpeg", "data": img_base64}})
            #prompt_elements.append({"type":"image_url","image_url":i["image"]["url"]})

        elif "record" in i:
            origin_voice_url=i["record"]["file"]
            r=await bot.get_record(origin_voice_url)
            print(r)
            mp3_filepath=r["data"]["file"]
            with open(mp3_filepath, "rb") as mp3_file:
                mp3_data = mp3_file.read()
                base64_encoded_data = base64.b64encode(mp3_data)
                base64_message = base64_encoded_data.decode('utf-8')
                prompt_elements.append({"inline_data": {"mime_type": "audio/mp3", "data": base64_message}})
            #prompt_elements.append({"type":"voice","voice":i["voice"]})
        elif "video" in i:
            video_url=i["video"]["url"]
            try:
                video=await bot.get_video(video_url,f"data/pictures/cache/{random_str()}.mp4")

                with open(video, "rb") as mp4_file:
                    mp4_data = mp4_file.read()
                    base64_encoded_data = base64.b64encode(mp4_data)
                    base64_message = base64_encoded_data.decode('utf-8')
                    prompt_elements.append({"inline_data": {"mime_type": "video/mp4", "data": base64_message}})
            except:
                bot.logger.warning(f"下载视频失败:{video_url}")
                prompt_elements.append({"text": str(i)})
        elif "reply" in i:
            try:
                event_obj=await bot.get_msg(int(event.get("reply")[0]["id"]))
                message = await gemini_prompt_elements_construct(event_obj.processed_message) #
                prompt_elements.extend(message["parts"])
            except Exception as e:
                bot.logger.warning(f"引用消息解析失败:{e}")
        else:
            prompt_elements.append({"text": str(i)})   #不知道还有什么类型，都需要做对应处理的，唉，任务还多着呢。
    if func_result:
        return {"role": "model","parts":prompt_elements}
    return {"role": "user","parts": prompt_elements}
async def construct_gemini_standard_prompt(processed_message, user_id, bot=None,func_result=False,event=None):
    message=await gemini_prompt_elements_construct(processed_message,bot,func_result,event=event)
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(message)
    history.append({"role": "model","parts":[{"text": "system:executing...."}]})

    full_prompt = []
    full_prompt.extend(history)
    await update_user_history(user_id, history)  # 更新数据库中的历史记录
    return full_prompt, original_history
async def clean_gemini_history(user_id,aim_element=None):
    if aim_element is None:
        aim_element={"role": "model", "parts": [{"text": "system:executing...."}]}
    history = await get_user_history(user_id)
    new_list = [x for x in history if x != aim_element]
    await update_user_history(user_id, new_list)
async def get_current_gemini_prompt(user_id):
    history = await get_user_history(user_id)
    return history
async def add_gemini_standard_prompt(prompt,user_id):
    history = await get_user_history(user_id)
    original_history = history.copy()  # 备份，出错的时候可以rollback
    history.append(prompt)

    await update_user_history(user_id, history)  # 更新数据库中的历史记录
    return history, original_history
