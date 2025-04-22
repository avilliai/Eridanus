# 语音合成接口
import asyncio
import random
import re
import threading

import httpx
import requests

from ruamel.yaml import YAML

from developTools.utils.logger import get_logger
from plugins.core.tts.modelscopeTTS import modelscope_tts
from plugins.core.tts.napcat_tts import napcat_tts_speak, napcat_tts_speakers
from plugins.core.tts.online_vits import huggingface_online_vits
from plugins.core.tts.online_vits2 import huggingface_online_vits2
from plugins.core.tts.vits import vits
from framework_common.utils.random_str import random_str
from framework_common.utils.translate import translate

from framework_common.framework_util.yamlLoader import YAMLManager
manager = YAMLManager("run")
yamlmanager = YAMLManager.get_instance()
local_config = yamlmanager.ai_voice.config

logger=get_logger()
global GPTSOVITS_SPEAKERS
GPTSOVITS_SPEAKERS={}
async def tts(text, speaker=None, config=None,mood=None,bot=None,mode=None):
    pattern = re.compile(r'[\(\（][^\(\)（）（）]*?[\)\）]')

    # 去除括号及其中的内容
    cleaned_text = pattern.sub('', text)
    text = cleaned_text.replace("·", "").replace("~", "").replace("-", "")
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    

    text=text.replace('```', '').strip()
    if config is None:
        config = YAMLManager(["config/settings.yaml", "config/basic_config.yaml", "config/api.yaml",
                              "config/controller.yaml"])  # 这玩意用来动态加载和修改配置文件
    if len(text) > config.ai_voice.config["tts"]["length_limit"]:
        raise ValueError("文本长度超出限制")
    """
    语言类型转换
    """
    if config.ai_voice.config["tts"]["lang_type"]=="ja":
        text=await translate(text)  #默认就是转日文
        print(f"翻译后的文本：{text}")
    if mode is None:
        mode = config.ai_voice.config["tts"]["tts_engine"]
    logger.info_func(f"语音合成任务：文本：{text}，发音人：{speaker}，模式：{mode}")
    if mode == "acgn_ai":
        if speaker is None:
            speaker=config.ai_voice.config["tts"]["acgn_ai"]["speaker"]
        return await acgn_ai_tts(random.choice(config.ai_voice.config["tts"]["acgn_ai"]["token"]), config, text, speaker,mood)
    elif mode=="napcat_tts":
        if speaker is None:
            speaker=config.ai_voice.config["tts"]["napcat_tts"]["character_name"]
        spkss=await napcat_tts_speakers(bot)
        if speaker in spkss:
            speaker=spkss[speaker]
        return await napcat_tts_speak(bot, config, text, speaker)
    elif mode=="modelscope_tts":
        if speaker is None:
            speaker=config.ai_voice.config["tts"]["modelscope_tts"]["speaker"]
        return await modelscope_tts(text,speaker)
    elif mode=="vits":
        if speaker is None:
            speaker=config.ai_voice.config["tts"]["vits"]["speaker"]
        base_url=config.ai_voice.config["tts"]["vits"]["base_url"]
        return await vits(text,speaker,base_url)
    elif mode=="online_vits":
        if speaker is None:
            speaker=config.ai_voice.config["tts"]["online_vits"]["speaker"]
        fn_index=config.ai_voice.config["tts"]["online_vits"]["fn_index"]
        proxy=config.config.api["proxy"]["http_proxy"]
        return await huggingface_online_vits(text,speaker,fn_index,proxy)
    elif mode=="online_vits2":
        if speaker is None:
            speaker=config.ai_voice.confi["tts"]["online_vits2"]["speaker"]
        if config.ai_voice.confi["tts"]["lang_type"] == "ja":
            lang="日本語"
        else:
            lang="简体中文"
        return await huggingface_online_vits2(text,speaker,lang)
    else:
        pass


def gptVitsSpeakers():
    global GPTSOVITS_SPEAKERS
    model_url="https://gsv.ai-lab.top/models"
    try:
        models=requests.get(model_url).json()
        for model in models:
            url=f"https://gsv.ai-lab.top/spks"
            response=requests.post(url,json={"model": model}).json()
            for spk in response["speakers"]:
                GPTSOVITS_SPEAKERS[spk]=model
    except:
        GPTSOVITS_SPEAKERS=None


try:
    if local_config["tts"]["tts_engine"] == "acgn_ai" and local_config["tts"]["acgn_ai"]["token"]!= "":
        r=threading.Thread(target=gptVitsSpeakers, daemon=True).start()
except:
    print("GPTSOVITS_SPEAKERS获取失败")

async def get_acgn_ai_speaker_list(a=None,b=None,c=None):
    global GPTSOVITS_SPEAKERS
    spks=list(GPTSOVITS_SPEAKERS.keys())
    return spks
async def acgn_ai_tts(token, config, text, speaker,inclination="中立_neutral"):
    global GPTSOVITS_SPEAKERS
    if speaker not in GPTSOVITS_SPEAKERS:
        speaker = config.ai_voice.confi["tts"]["acgn_ai"]["speaker"]


    url = "https://gsv.ai-lab.top/infer_single"
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.post(url, json={
          "access_token": token,
          "model_name": GPTSOVITS_SPEAKERS[speaker],
          "speaker_name": speaker,
          "prompt_text_lang": "中文",
          "emotion": inclination,
          "text": text,
          "text_lang": "中文",
          "top_k": 10,
          "top_p": 1,
          "temperature": 1,
          "text_split_method": "按标点符号切",
          "batch_size": 1,
          "batch_threshold": 0.75,
          "split_bucket": True,
          "speed_facter": 1,
          "fragment_interval": 0.3,
          "media_type": "wav",
          "parallel_infer": True,
          "repetition_penalty": 1.35,
          "seed": -1
        })
    async with httpx.AsyncClient(timeout=100) as client:
        r = await client.get(r.json()['audio_url'])
    p = "data/voice/cache/" + random_str() + '.wav'
    with open(p, "wb") as f:
        f.write(r.content)
    return p

if __name__ == '__main__':
    from framework_common.framework_util.yamlLoader import YAMLManager
    config = YAMLManager(["config/settings.yaml", "config/basic_config.yaml", "config/api.yaml",
                          "config/controller.yaml"])  # 这玩意用来动态加载和修改配置文件
    # http_server地址，access_token
    r=asyncio.run(tts("你好，欢迎使用语音合成服务，请说出你想说的话。", "玲可【星穹铁道】", config))
    print(r)
