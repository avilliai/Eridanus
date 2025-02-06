import random
import re

from developTools.message.message_components import Node, Text
from plugins.core.aiReplyHandler.default import defaultModelRequest
from plugins.core.aiReplyHandler.gemini import geminiRequest, construct_gemini_standard_prompt, \
    get_current_gemini_prompt
from plugins.core.aiReplyHandler.openai import openaiRequest, construct_openai_standard_prompt, \
    get_current_openai_prompt
from developTools.utils.logger import get_logger
from plugins.core.aiReplyHandler.tecentYuanQi import construct_tecent_standard_prompt, YuanQiTencent
from plugins.core.llmDB import get_user_history, update_user_history, delete_user_history
from plugins.core.userDB import get_user



logger=get_logger()

async def aiReplyCore_shadow(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False,recursion_times=0,lock_prompt=None): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    if recursion_times > config.api["llm"]["recursion_limit"]:
        logger.warning(f"roll back to original history, recursion times: {recursion_times}")
        return "Maximum recursion depth exceeded.Please try again later."
    reply_message = ""
    original_history = []
    if not system_instruction:
        system_instruction = config.api["llm"]["system"]
        user_info=await get_user(user_id)
        system_instruction=system_instruction.replace("{用户}",user_info[1]).replace("{bot_name}",config.basic_config["bot"]["name"])
    try:
        if config.api["llm"]["model"]=="default":
            prompt, original_history = await construct_openai_standard_prompt(processed_message, system_instruction,
                                                                              user_id)
            response_message = await defaultModelRequest(
                prompt,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
            )
            reply_message = response_message['content']
            await prompt_database_updata(user_id,response_message,config)

        elif config.api["llm"]["model"]=="openai":
            if processed_message:
                prompt, original_history = await construct_openai_standard_prompt(processed_message,system_instruction, user_id,bot,func_result,event)
            else:
                prompt=await get_current_openai_prompt(user_id)
            response_message = await openaiRequest(
                prompt,
                config.api["llm"]["openai"]["quest_url"],
                random.choice(config.api["llm"]["openai"]["api_keys"]),
                config.api["llm"]["openai"]["model"],
                False,
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                temperature=config.api["llm"]["openai"]["temperature"],
                max_tokens=config.api["llm"]["openai"]["max_tokens"]
            )
            if "content" in response_message:
                reply_message=response_message["content"]
                if reply_message is not None:
                    pattern_think = r"<think>\n(.*?)\n</think>"
                    match_think = re.search(pattern_think, reply_message, re.DOTALL)

                    if match_think:
                        think_text = match_think.group(1)
                        await bot.send(event,[Node(content=[Text(think_text)])])
                        pattern_rest = r"</think>\n\n(.*?)$"
                        match_rest = re.search(pattern_rest, reply_message, re.DOTALL)
                        if match_rest:
                            reply_message = match_rest.group(1)
            else:
                reply_message=None

            #检查是否存在函数调用，如果还有提示词就发

        elif config.api["llm"]["model"]=="gemini":
            if processed_message:
                prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, bot,func_result,event)
            elif lock_prompt:
                prompt=lock_prompt
            else:
                prompt=await get_current_gemini_prompt(user_id)
            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction,
                temperature=config.api["llm"]["gemini"]["temperature"],
                maxOutputTokens=config.api["llm"]["gemini"]["maxOutputTokens"]
            )
            #print(response_message)
            try:
                reply_message=response_message["parts"][0]["text"]  #函数调用可能不给你返回提示文本，只给你整一个调用函数。
            except:
                reply_message=None
            if reply_message is not None:
                if reply_message=="\n" or reply_message=="" or reply_message==" ":
                    raise Exception("Empty response。Gemini API返回的文本为空。")
            text_elements = [part for part in response_message['parts'] if 'text' in part]
            if text_elements!=[] and len(text_elements)>1:
                for i in text_elements:
                    await bot.send(event, i['text'].strip())
                reply_message=None

        elif config.api["llm"]["model"]=="腾讯元器":
            prompt, original_history = await construct_tecent_standard_prompt(processed_message,user_id,bot,event)
            response_message = await YuanQiTencent(
                prompt,
                config.api["llm"]["腾讯元器"]["智能体ID"],
                config.api["llm"]["腾讯元器"]["token"],
                user_id,
            )
            reply_message = response_message["content"]
            response_message["content"]=[{"type": "text", "text": response_message["content"]}]

            await prompt_database_updata(user_id,response_message,config)


        logger.info(f"aiReplyCore returned: {reply_message}")
        await prompt_length_check(user_id,config)
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        if recursion_times<=config.api["llm"]["recursion_limit"]:

            logger.warning(f"Recursion times: {recursion_times}")
            if recursion_times+1==config.api["llm"]["recursion_limit"] and config.api["llm"]["auto_clear_when_recursion_fail"]:
                bot.logger.warning(f"clear ai reply history for user: {event.user_id}")
                await delete_user_history(event.user_id)
            return await aiReplyCore_shadow(processed_message,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=func_result,recursion_times=recursion_times+1)
        else:
            logger.warning(f"roll back to original history, recursion times: {recursion_times}")
            await update_user_history(user_id, original_history)
            return "Maximum recursion depth exceeded.Please try again later."
async def prompt_database_updata(user_id,response_message,config):
    history = await get_user_history(user_id)
    if len(history) > config.api["llm"]["max_history_length"]:
        del history[0]
        del history[0]
    history.append(response_message)
    await update_user_history(user_id, history)
async def prompt_length_check(user_id,config):
    history = await get_user_history(user_id)
    if len(history) > config.api["llm"]["max_history_length"]:
        while history[0]["role"]!="user":
            del history[0]
    await update_user_history(user_id, history)