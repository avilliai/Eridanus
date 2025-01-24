import random

from plugins.core.aiReplyHandler.default import defaultModelRequest
from plugins.core.aiReplyHandler.gemini import geminiRequest, construct_gemini_standard_prompt
from plugins.core.aiReplyHandler.openai import openaiRequest, construct_openai_standard_prompt
from developTools.utils.logger import get_logger
from plugins.core.aiReplyHandler.tecentYuanQi import construct_tecent_standard_prompt, YuanQiTencent
from plugins.core.llmDB import get_user_history, update_user_history
from plugins.core.userDB import get_user



logger=get_logger()

async def aiReplyCore_shadow(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    reply_message = ""
    if not system_instruction:
        system_instruction = config.api["llm"]["system"]
        user_info = await get_user(user_id)
        system_instruction = system_instruction.replace("{用户}", user_info[1]).replace("{bot_name}",
                                                                                        config.basic_config["bot"][
                                                                                            "name"])
    try:
        if config.api["llm"]["model"]=="default":
            prompt, original_history = await construct_openai_standard_prompt(processed_message, system_instruction,
                                                                              user_id)
            response_message = await defaultModelRequest(
                prompt,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
            )
            reply_message = response_message['content']
        elif config.api["llm"]["model"] == "openai":
            prompt, original_history = await construct_openai_standard_prompt(processed_message,system_instruction, user_id,bot,func_result,event)
            response_message = await openaiRequest(
                prompt,
                config.api["llm"]["openai"]["quest_url"],
                random.choice(config.api["llm"]["openai"]["api_keys"]),
                config.api["llm"]["openai"]["model"],
                False,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
            )
            reply_message = response_message["content"]
            # print(response_message)
        elif config.api["llm"]["model"] == "gemini":
            prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, bot,
                                                                              func_result,event=event)

            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction)
            # print(response_message)
            try:
                reply_message = response_message["parts"][0]["text"]  # 函数调用可能不给你返回提示文本，只给你整一个调用函数。
            except:
                reply_message = None
        elif config.api["llm"]["model"]=="腾讯元器":
            prompt, original_history = await construct_tecent_standard_prompt(processed_message,user_id,bot,event)
            response_message = await YuanQiTencent(
                prompt,
                config.api["llm"]["腾讯元器"]["智能体ID"],
                config.api["llm"]["腾讯元器"]["token"],
                user_id,
            )
            reply_message = response_message["content"]
            response_message["content"] = [{"type": "text", "text": response_message["content"]}]
            await prompt_database_updata(user_id,response_message,config)


        # 更新数据库中的历史记录
        history = await get_user_history(user_id)
        if len(history) > config.api["llm"]["max_history_length"]:
            del history[0]
            del history[0]
        history.append(response_message)
        await update_user_history(user_id, history)
        # 处理工具调用，但没做完，一用gemini函数调用就给我RESOURCE_EXHAUSTED，受不了一点byd

        # print(f"funccall result:{r}")
        # return r
        # ask = await prompt_elements_construct(r)
        # response_message = await aiReplyCore(ask,user_id,config,tools=tools)
        logger.info(f"aiReplyCore returned: {reply_message}")
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        await update_user_history(user_id, original_history)
        logger.error(f"Error occurred: {e}")
        raise  # 继续抛出异常以便调用方处理
async def prompt_database_updata(user_id,response_message,config):
    history = await get_user_history(user_id)
    if len(history) > config.api["llm"]["max_history_length"]:
        del history[0]
        del history[0]
    history.append(response_message)
    await update_user_history(user_id, history)
#asyncio.run(openaiRequest("1"))