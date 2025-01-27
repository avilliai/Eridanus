
import json
import random
import time
from collections import defaultdict


from developTools.message.message_components import Record
from developTools.utils.logger import get_logger
from plugins.core.aiReplyHandler.default import defaultModelRequest
from plugins.core.aiReplyHandler.gemini import geminiRequest, construct_gemini_standard_prompt, \
    add_gemini_standard_prompt,  get_current_gemini_prompt
from plugins.core.aiReplyHandler.openai import openaiRequest, construct_openai_standard_prompt, \
    get_current_openai_prompt, add_openai_standard_prompt
from plugins.core.aiReplyHandler.tecentYuanQi import construct_tecent_standard_prompt, YuanQiTencent
from plugins.core.llmDB import get_user_history, update_user_history
from plugins.core.tts.tts import tts
from plugins.core.userDB import get_user
from plugins.func_map import call_func
last_trigger_time = defaultdict(float)

logger=get_logger()
async def judge_trigger(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False):
    trigger = False
    if event.user_id in last_trigger_time:
        bot.logger.info(f"last_trigger_time: {last_trigger_time.get(event.user_id)}")
        if (time.time() - last_trigger_time.get(event.user_id)) <= config.api["llm"]["focus_time"]:
            trigger = True
        else:
            last_trigger_time.pop(event.user_id)
            trigger = False
    if trigger:
        r=await aiReplyCore(processed_message,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=func_result)
        return r
    else:
        return None
async def end_chat(user_id):
    try:
        last_trigger_time.pop(user_id)
    except:
        print("end_chat error。已不存在对应trigger")
async def aiReplyCore(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False,recursion_times=0): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    reply_message = ""
    original_history = []
    if not system_instruction:
        system_instruction = config.api["llm"]["system"]
        user_info=await get_user(user_id)
        system_instruction=system_instruction.replace("{用户}",user_info[1]).replace("{bot_name}",config.basic_config["bot"]["name"])
    try:
        last_trigger_time[user_id] = time.time()
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
            )
            reply_message=response_message["content"]
            #检查是否存在函数调用，如果还有提示词就发
            status=False
            if "tool_calls" in response_message:
                status=True
            generate_voice=False
            if status and reply_message is not None: #有函数调用且有回复，就发回复和语音
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
                    generate_voice=True
                else:
                    await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])

            #在函数调用之前触发更新上下文。

            #函数调用
            temp_history=[]
            if "tool_calls" in response_message:
                func_call=False
                for part in response_message['tool_calls']:
                    func_call=True
                    func_name = part['function']["name"]
                    args = part['function']['arguments']
                    try:
                        r=await call_func(bot, event, config,func_name, json.loads(args)) #真是到处都不想相互兼容。
                        if r==False:
                            await end_chat(user_id)
                        if r:
                            temp_history.append({
                                "role": "tool",
                                "content": json.dumps(r),
                                # Here we specify the tool_call_id that this result corresponds to
                                "tool_call_id": part['id']
                            })
                        else:
                            temp_history.append({
                                "role": "tool",
                                "content": json.dumps({"status":"succeed"}),
                                # Here we specify the tool_call_id that this result corresponds to
                                "tool_call_id": part['id']
                            })
                    except Exception as e:
                        #logger.error(f"Error occurred when calling function: {e}")
                        raise Exception(f"Error occurred when calling function: {e}")

                    #函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message=None
                temp_history.insert(0,response_message)
                for history_part in temp_history:
                    await prompt_database_updata(user_id, history_part, config)
                if func_call:
                    final_response = await aiReplyCore(None, user_id, config, tools=tools, bot=bot, event=event,
                                                       system_instruction=system_instruction, func_result=True)
                    return final_response
                if generate_voice and reply_message:
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path = await tts(reply_message, config=config,bot=bot)
                        await bot.send(event, Record(file=path))
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
            #print(response_message)
        elif config.api["llm"]["model"]=="gemini":
            if processed_message:
                prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, bot,func_result,event)
            else:
                prompt=await get_current_gemini_prompt(user_id)
            response_message = await geminiRequest(
                prompt,
                config.api["llm"]["gemini"]["base_url"],
                random.choice(config.api["llm"]["gemini"]["api_keys"]),
                config.api["llm"]["gemini"]["model"],
                config.api["proxy"]["http_proxy"] if config.api["llm"]["enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction)
            #print(response_message)
            try:
                reply_message=response_message["parts"][0]["text"]  #函数调用可能不给你返回提示文本，只给你整一个调用函数。
            except:
                reply_message=None

            #检查是否存在函数调用，如果还有提示词就发
            status=False
            for part in response_message["parts"]:
                if "functionCall" in part:
                    status=True
            generate_voice=False
            if status and reply_message is not None: #有函数调用且有回复，就发回复和语音
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
                    generate_voice=True
                else:
                    await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])

            #在函数调用之前触发更新上下文。
            await prompt_database_updata(user_id,response_message,config)
            #函数调用
            for part in response_message["parts"]:
                new_func_prompt=[]
                if "functionCall" in part:
                    func_name = part['functionCall']["name"]
                    args = part['functionCall']['args']
                    try:
                         #只能在这里导入，否则会循环导入，解释器会不给跑。
                        r=await call_func(bot, event, config,func_name, args)
                        if r==False:
                            await end_chat(user_id)
                        if r:
                            func_r={
                                "functionResponse": {
                                    "name": func_name,
                                    "response": r
                                }
                            }
                            new_func_prompt.append(func_r)
                    except Exception as e:
                        #logger.error(f"Error occurred when calling function: {e}")
                        raise Exception(f"Error occurred when calling function: {e}")

                    #函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message=None
                if new_func_prompt!=[]:
                    new_func_prompt.append({"text": " "})
                    await add_gemini_standard_prompt({"role": "user","parts": new_func_prompt},user_id)# 更新prompt
                    final_response=await aiReplyCore(None,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=True)
                    return final_response
            if generate_voice and reply_message is not None:
                try:
                    bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                    path = await tts(reply_message, config=config,bot=bot)
                    await bot.send(event, Record(file=path))
                except Exception as e:
                    bot.logger.error(f"Error occurred when calling tts: {e}")
                if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                    await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
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
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        if recursion_times<=config.api["llm"]["recursion_limit"]:

            logger.warning(f"Recursion times: {recursion_times}")
            return await aiReplyCore(processed_message,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=func_result,recursion_times=recursion_times+1)
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







#asyncio.run(openaiRequest("1"))
