# 语音合成接口
import re

from developTools.utils.logger import get_logger
from framework_common.framework_util.yamlLoader import YAMLManager
from framework_common.utils.ai_translate import Translator
from run.ai_voice.service.blue_archive_tts import get_huggingface_blue_archive_speakers, huggingface_blue_archive_tts
from run.ai_voice.service.modelscopeTTS import modelscope_tts, get_modelscope_tts_speakers
from run.ai_voice.service.napcat_tts import napcat_tts_speak, napcat_tts_speakers
from run.ai_voice.service.online_vits import huggingface_online_vits
from run.ai_voice.service.online_vits2 import huggingface_online_vits2, get_huggingface_online_vits2_speakers
from run.ai_voice.service.ottoTTS import OttoTTS
from run.ai_voice.service.vits import vits, get_vits_speakers
import httpx
import requests




async def translate(text, mode="ZH_CN2JA"):
    try:
        URL = f"https://api.pearktrue.cn/api/translate/?text={text}&type={mode}"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(URL)
            #print(r.json()["data"]["translate"])
            return r.json()["data"]["translate"]
    except:
        if mode != "ZH_CN2JA":
            return text
    try:
        url = f"https://findmyip.net/api/translate.php?text={text}&target_lang=ja"
        r = requests.get(url=url, timeout=10)
        return r.json()["data"]["translate_result"]
    except:
        pass
    try:
        url = f"https://translate.appworlds.cn?text={text}&from=zh-CN&to=ja"
        r = requests.get(url=url, timeout=10, verify=False)
        return r.json()["data"]
    except:
        pass
    return text

logger=get_logger()
class TTS:
    def __init__(self):
        self.config = YAMLManager.get_instance()
        self.translator=Translator()

    async def tts(self,text, speaker=None, config=None,mood=None,bot=None,mode=None):
        pattern = re.compile(r'[\(\（][^\(\)（）（）]*?[\)\）]')

        # 去除括号及其中的内容
        cleaned_text = pattern.sub('', text)
        text = cleaned_text.replace("·", "").replace("~", "").replace("-", "")
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)


        text=text.replace('```', '').strip()
        if config is None:
            config = self.config
        if len(text) > config.ai_voice.config["tts"]["length_limit"]:
            raise ValueError("文本长度超出限制")
        """
        语言类型转换
        """
        if mode is None:
            mode = config.ai_voice.config["tts"]["tts_engine"]
        if config.ai_voice.config["tts"]["lang_type"]=="ja" or mode=="blue_archive":
            if config.ai_voice.config["tts"]["ai_translator"]:
                text=await self.translator.translate(text)
            else:
                text=await translate(text)  #默认就是转日文
            print(f"翻译后的文本：{text}")


        logger.info_func(f"语音合成任务：文本：{text}，发音人：{speaker}，模式：{mode}")
        if mode=="napcat_tts":
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
            proxy=config.common_config.basic_config["proxy"]["http_proxy"]
            return await huggingface_online_vits(text,speaker,fn_index,proxy)
        elif mode=="online_vits2":
            if speaker is None:
                speaker=config.ai_voice.config["tts"]["online_vits2"]["speaker"]
            if config.ai_voice.config["tts"]["lang_type"] == "ja":
                lang="日本語"
            else:
                lang="简体中文"
            return await huggingface_online_vits2(text,speaker,lang)
        elif mode=="blue_archive":
            if speaker is None:
                speaker=config.ai_voice.config["tts"]["blue_archive"]["speaker"]
            return await huggingface_blue_archive_tts(text, speaker)
        elif mode=="OttoTTS":
            otto=OttoTTS()
            return await otto.speak(text)
        else:
            pass
    async def get_speakers(self,bot=None):
        async def fetch_speakers(func, *args, error_msg):
            try:
                return await func(*args)
            except Exception as e:
                bot.logger.error(f"{error_msg}: {e}")
                return None
        nc_speakers = await fetch_speakers(napcat_tts_speakers, bot, error_msg="Error in napcat_tts_speakers")
        modelscope_speakers = get_modelscope_tts_speakers()
        vits_speakers = await fetch_speakers(
            get_vits_speakers,
            self.config.ai_voice.config["tts"]["vits"]["base_url"], None,
            error_msg="Error in get_vits_speakers"
        )
        online_vits2_speakers = await fetch_speakers(
            get_huggingface_online_vits2_speakers,
            error_msg="Error in get_huggingface_online_vits2_speakers"
        )
        blue_archive_speakers=await fetch_speakers(get_huggingface_blue_archive_speakers,error_msg="Error in get_huggingface_blue_archive_speakers")
        return {"speakers": [nc_speakers, modelscope_speakers, vits_speakers, online_vits2_speakers,blue_archive_speakers,["otto"]]}




