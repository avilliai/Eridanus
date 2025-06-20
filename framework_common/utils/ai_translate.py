import random
import traceback

from developTools.utils.logger import get_logger
from framework_common.framework_util.yamlLoader import YAMLManager
from run.ai_llm.service.aiReplyHandler.default import defaultModelRequest
from run.ai_llm.service.aiReplyHandler.gemini import geminiRequest
from run.ai_llm.service.aiReplyHandler.openai import openaiRequest_official, openaiRequest
from run.ai_llm.service.aiReplyHandler.tecentYuanQi import YuanQiTencent


class Translator:
    def __init__(self):
        self.config = YAMLManager.get_instance()
        self.system_instruction="请翻译以下内容为日文，直接给出结果，不要有回应之类的内容。需要翻译的文本为："
        self.logger=get_logger()
    async def translate(self, text):
        return await self.aiReplyCore(text, self.config, self.system_instruction)
    async def aiReplyCore(self,text,config,system_instruction=None,recursion_times=0):  # 后面几个函数都是供函数调用的场景使用的
        logger = self.logger
        logger.info(f"translator called with message: {text}")
        """
        递归深度约束
        """
        if recursion_times > config.ai_llm.config["llm"]["recursion_limit"]:
            logger.warning(f"roll back to original history, recursion times: {recursion_times}")
            return text

        try:
            if config.ai_llm.config["llm"]["model"] == "default":
                prompt=[
                    {"role": "user", "content": system_instruction+text},
                ]
                response_message = await defaultModelRequest(
                    prompt,
                    config.common_config.basic_config["proxy"]["http_proxy"] if config.ai_llm.config["llm"][
                        "enable_proxy"] else None,
                )
                reply_message = response_message['content']


            elif config.ai_llm.config["llm"]["model"] == "openai":

                if config.ai_llm.config["llm"]["openai"]["使用旧版prompt结构"]:
                    prompt = [
                        {"role": "user", "content": system_instruction + text},
                    ]
                else:
                    prompt=[{"role": "system", "content": [{"type": "text", "text": system_instruction+text}]}]

                kwargs = {
                    "ask_prompt": prompt,
                    "url": config.ai_llm.config["llm"]["openai"].get("quest_url") or config.ai_llm.config["llm"]["openai"].get("base_url"),
                    "apikey": random.choice(config.ai_llm.config["llm"]["openai"]["api_keys"]),
                    "model": config.ai_llm.config["llm"]["openai"]["model"],
                    "stream": False,
                    "proxy": config.common_config.basic_config["proxy"]["http_proxy"] if
                    config.ai_llm.config["llm"][
                        "enable_proxy"] else None,
                    "tools": None,
                    "temperature": config.ai_llm.config["llm"]["openai"]["temperature"],
                    "max_tokens": config.ai_llm.config["llm"]["openai"]["max_tokens"]
                }
                if config.ai_llm.config["llm"]["openai"]["enable_official_sdk"]:
                    response_message = await openaiRequest_official(**kwargs)
                else:
                    response_message = await openaiRequest(**kwargs)
                response_message = response_message["choices"][0]["message"]
                reply_message = response_message["content"]
            elif config.ai_llm.config["llm"]["model"] == "gemini":
                prompt = [
                    {
                        "parts": [
                            {
                                "text": system_instruction+text,
                            }
                        ],
                        "role": "user"
                    },
                ]

                # 这里是需要完整报错的，不用try catch，否则会影响自动重试。
                response_message = await geminiRequest(
                    prompt,
                    config.ai_llm.config["llm"]["gemini"]["base_url"],
                    random.choice(config.ai_llm.config["llm"]["gemini"]["api_keys"]),
                    config.ai_llm.config["llm"]["gemini"]["model"],
                    config.common_config.basic_config["proxy"]["http_proxy"] if config.ai_llm.config["llm"][
                        "enable_proxy"] else None,
                    tools=None,
                    system_instruction="请你扮演翻译官，我给你要翻译的文本，你直接给我结果，不需要回应。",
                    temperature=config.ai_llm.config["llm"]["gemini"]["temperature"],
                    maxOutputTokens=config.ai_llm.config["llm"]["gemini"]["maxOutputTokens"]
                )
                response_message = response_message['candidates'][0]["content"]
                # print(response_message)
                reply_message = response_message["parts"][0]["text"]  # 函数调用可能不给你返回提示文本，只给你整一个调用函数。

            elif config.ai_llm.config["llm"]["model"] == "腾讯元器":
                prompt=[{"role": "user", "content": [{"type": "text", "text": system_instruction+text}]}]
                response_message = await YuanQiTencent(
                    prompt,
                    config.ai_llm.config["llm"]["腾讯元器"]["智能体ID"],
                    config.ai_llm.config["llm"]["腾讯元器"]["token"],
                    random.randint(1, 100),
                )
                reply_message = response_message["content"]
                response_message["content"] = [{"type": "text", "text": response_message["content"]}]
            logger.info(f"aiReplyCore returned: {reply_message}")
            if reply_message is not None:
                return reply_message.strip()
            else:
                return reply_message
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            traceback.print_exc()
            logger.warning(f"roll back to original history, recursion times: {recursion_times}")
            if recursion_times <= config.ai_llm.config["llm"]["recursion_limit"]:
                logger.warning(f"Recursion times: {recursion_times}")
                return await self.aiReplyCore(text, config, system_instruction, recursion_times + 1)
            else:
                return text