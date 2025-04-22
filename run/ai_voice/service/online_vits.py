# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import asyncio
import json

import httpx

from developTools.utils.logger import get_logger
from framework_common.utils.random_str import random_str

logger=get_logger()



cookie = "_gid=GA1.2.617812556.1740732308; _ga_R1FN4KJKJH=GS1.1.1740732308.1.1.1740732567.0.0.0; _ga=GA1.1.1440020043.1740732308"
def random_session_hash(random_length):
    # 给gradio一类的api用，生成随机session_hash,避免多任务撞车导致推理出错。这里偷懒套个娃（bushi
    return random_str(random_length, "abcdefghijklmnopqrstuvwxyz1234567890")

#modelscopeTTS V3，对接原神崩铁语音合成器。API用法相较之前发生了变化，参考V2修改而成。
async def huggingface_online_vits(text,speaker,fn_index,proxy=None):
    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
    else:
        proxies = None
    # 随机session hash
    session_hash = random_session_hash(11)

    # 第一个请求的URL和参数
    queue_join_url = "https://skytnt-moe-tts.hf.space/queue/join"
    queue_join_params = {
        "__theme":"system",
    }
    # 第二个请求的URL和headers
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",

        "content-type": "application/json",
        "cookie": cookie,
        "Origin": "https://skytnt-moe-tts.hf.space",
        "priority": "u=1, i",
        "referer": f"https://skytnt-moe-tts.hf.space/?__theme=system",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-fetch-storage-access": "active",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    }
    data1={"data":[text,speaker,1,False],"event_data":None,"fn_index":fn_index,"trigger_id":51,"session_hash":session_hash}
    # 发起第一个请求
    async with httpx.AsyncClient(headers=headers,proxies=proxies) as client:
        response = await client.post(queue_join_url, params=queue_join_params,json=data1)


        await asyncio.sleep(1)

        queue_data_url=f"https://skytnt-moe-tts.hf.space/queue/data?session_hash={session_hash}"
        async with client.stream("GET", queue_data_url, headers=headers,timeout=60) as event_stream_response:
            async for line in event_stream_response.aiter_text():
                event = line.replace("data:", "").strip()
                if event:
                    print(event)
                    try:
                        event_data = json.loads(event)
                        #print(event_data)
                        if "output" in event_data:
                            save_path = f"data/voice/cache/{session_hash}.wav"
                            audiourl=event_data["output"]["data"][1]["url"]
                            for attempt in range(10):  # 最多重试 10 次
                                response = await client.get(audiourl)
                                print(f"请求状态码: {response.status_code}")

                                if response.status_code == 200:
                                    with open(save_path, "wb") as f:
                                        f.write(response.content)
                                    print(f"音频已保存: {save_path}")
                                    return save_path

                                elif response.status_code == 404:
                                    print("音频文件未生成，等待 2 秒后重试...")
                                    await asyncio.sleep(2)

                                else:
                                    print(f"未知错误: {response.status_code}, {response.text}")
                                    break  # 避免死循环
                            return audiourl
                    except Exception as e:
                        logger.error(f"Error in processing event data: {e}")





#r=asyncio.run(huggingface_online_vits("先生,こんにちは,今日はどうでした","明月栞那",6))
#print(r)