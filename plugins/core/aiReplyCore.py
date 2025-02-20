
import json
import random
import re
import time
import traceback
from collections import defaultdict
import os


from developTools.message.message_components import Record, Text, Node
from developTools.utils.logger import get_logger
from plugins.core.Group_Message_DB import get_last_20_and_convert_to_prompt, add_to_group
from plugins.core.aiReplyHandler.default import defaultModelRequest
from plugins.core.aiReplyHandler.gemini import geminiRequest, construct_gemini_standard_prompt, \
    add_gemini_standard_prompt, get_current_gemini_prompt, query_and_insert_gemini
from plugins.core.aiReplyHandler.openai import openaiRequest, construct_openai_standard_prompt, \
    get_current_openai_prompt, add_openai_standard_prompt, construct_openai_standard_prompt_old_version
from plugins.core.aiReplyHandler.tecentYuanQi import construct_tecent_standard_prompt, YuanQiTencent
from plugins.core.llmDB import get_user_history, update_user_history, delete_user_history, clear_all_history, change_folder_chara, read_chara, use_folder_chara
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
    return trigger

async def end_chat(user_id):
    try:
        last_trigger_time.pop(user_id)
    except:
        print("end_chat error。已不存在对应trigger")

async def aiReplyCore(processed_message,user_id,config,tools=None,bot=None,event=None,system_instruction=None,func_result=False,recursion_times=0): #后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    if recursion_times > config.api["llm"]["recursion_limit"]:
        logger.warning(f"roll back to original history, recursion times: {recursion_times}")
        return "Maximum recursion depth exceeded.Please try again later."
    reply_message = ""
    original_history = []
    if tools is not None and config.api["llm"]["表情包发送"]:
        tools=await add_send_mface(tools,config)
    if not system_instruction:
        if config.api["llm"]["system"]:
            system_instruction = await read_chara(user_id, config.api["llm"]["system"])
        else:
            system_instruction = await read_chara(user_id, await use_folder_chara(config.api["llm"]["chara_file_name"]))
        user_info=await get_user(user_id)
        system_instruction=system_instruction.replace("{用户}",user_info[1]).replace("{bot_name}",config.basic_config["bot"]["name"])
    try:
        if recursion_times==0 and processed_message:
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
                if config.api["llm"]["openai"]["使用旧版prompt结构"]:
                    prompt, original_history = await construct_openai_standard_prompt_old_version(processed_message,
                                                                                      system_instruction, user_id, bot,
                                                                                      func_result, event)
                else:
                    prompt, original_history = await construct_openai_standard_prompt(processed_message,system_instruction, user_id,bot,func_result,event)
            else:
                prompt=await get_current_openai_prompt(user_id)
            if processed_message is None:  #防止二次递归无限循环
                tools=None
            """
            读取上下文
            """
            p = await read_context(bot, event, config, prompt)
            if p:
                prompt = p
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
                if reply_message is not None and config.api["llm"]["openai"]["CoT"]:
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
                        if "reasoning_content" in response_message:
                            await bot.send(event, [Node(content=[Text(response_message["reasoning_content"])])])
                            response_message.pop("reasoning_content")
            else:
                reply_message=None

            #检查是否存在函数调用，如果还有提示词就发
            status=False
            if "tool_calls" in response_message and response_message['tool_calls'] is not None:
                status=True
            generate_voice=False
            if status and reply_message is not None: #有函数调用且有回复，就发回复和语音
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        if reply_message.strip()=="" or reply_message.strip()=="\n":
                            logger.error("gemini返回了空回复，不发送。")
                        await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])
                    generate_voice=True
                else:
                    await bot.send(event, reply_message.strip(), config.api["llm"]["Quote"])

            #函数调用
            temp_history=[]
            func_call = False
            if "tool_calls" in response_message and response_message['tool_calls'] is not None:

                for part in response_message['tool_calls']:
                    func_name = part['function']["name"]
                    args = part['function']['arguments']
                    try:
                        r=await call_func(bot, event, config,func_name, json.loads(args)) #真是到处都不想相互兼容。
                        if r==False:
                            await end_chat(user_id)
                        if r:
                            func_call = True
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
                        logger.error(f"Error occurred when calling function: {e}")
                        traceback.print_exc()
                        temp_history.append({
                            "role": "tool",
                            "content": json.dumps({"status": "failed to call function"}),
                            # Here we specify the tool_call_id that this result corresponds to
                            "tool_call_id": part['id']
                        })

                    #函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message=None

            await prompt_database_updata(user_id, response_message, config)
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
                p=await read_context(bot,event,config,prompt)
                if p:
                    prompt=p
            else:
                prompt=await get_current_gemini_prompt(user_id)
                p = await read_context(bot, event, config, prompt)
                if p:
                    prompt = p
            if processed_message is None:  #防止二次递归无限循环
                tools=None
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
                self_rep=[]
                for i in text_elements:
                    self_rep.append({"text":i['text'].strip()})
                    await bot.send(event, i['text'].strip())
                self_message = {"user_name": config.basic_config["bot"]["name"], "user_id": 0000000, "message": self_rep}
                if hasattr(event, "group_id"):
                    await add_to_group(event.group_id, self_message)
                reply_message=None
            #检查是否存在函数调用，如果还有提示词就发
            status=False

            for part in response_message["parts"]:
                if "functionCall" in part and config.api["llm"]["func_calling"]:
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
            await prompt_database_updata(user_id, response_message, config)
            #函数调用
            new_func_prompt = []
            for part in response_message["parts"]:
                if "functionCall" in part:
                    func_name = part['functionCall']["name"]
                    args = part['functionCall']['args']
                    try:

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
                        logger.error(f"Error occurred when calling function: {func_name}")
                        traceback.print_exc()
                    await add_self_rep(bot,event,config,reply_message)
                    reply_message=None
            if new_func_prompt!=[]:

                await prompt_database_updata(user_id, {"role": "function", "parts": new_func_prompt}, config)
                #await add_gemini_standard_prompt({"role": "function","parts": new_func_prompt},user_id)# 更新prompt
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
        await prompt_length_check(user_id,config)
        if reply_message is not None:
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        traceback.print_exc()
        logger.warning(f"roll back to original history, recursion times: {recursion_times}")
        await update_user_history(user_id, original_history)
        if recursion_times<=config.api["llm"]["recursion_limit"]:

            logger.warning(f"Recursion times: {recursion_times}")
            if recursion_times+1==config.api["llm"]["recursion_limit"] and config.api["llm"]["auto_clear_when_recursion_failed"]:
                logger.warning(f"clear ai reply history for user: {event.user_id}")
                await delete_user_history(event.user_id)
            return await aiReplyCore(processed_message,user_id,config,tools=tools,bot=bot,event=event,system_instruction=system_instruction,func_result=func_result,recursion_times=recursion_times+1)
        else:
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

async def read_context(bot,event,config,prompt):
    try:
        if event is None:
            return None
        if config.api["llm"]["读取群聊上下文"]==False or not hasattr(event, "group_id"):
            return None
        if config.api["llm"]["model"]=="gemini":
            group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id,config.api["llm"]["可获取的群聊上下文长度"],"gemini",bot)
        elif config.api["llm"]["model"]=="openai":
            if config.api["llm"]["openai"]["使用旧版prompt结构"]:
                group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id,
                                                                            config.api["llm"]["可获取的群聊上下文长度"],
                                                                            "old_openai", bot)
            else:
                group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id,
                                                                            config.api["llm"]["可获取的群聊上下文长度"],
                                                                            "new_openai", bot)
        else:
            return None
        bot.logger.info(f"群聊上下文消息：已读取")
        insert_pos = max(len(prompt) - 2, 0)  # 保证插入位置始终在倒数第二个元素之前
        prompt = prompt[:insert_pos] + group_messages_bg + prompt[insert_pos:]
        return prompt
    except:
        return None

async def add_self_rep(bot,event,config,reply_message):
    if event is None or reply_message is None:
        return None
    if not config.api["llm"]["读取群聊上下文"] and not hasattr(event, "group_id"):
        return None
    try:
        self_rep = [{"text":reply_message.strip()}]
        message = {"user_name": config.basic_config["bot"]["name"], "user_id": 0000000, "message": self_rep}
        if hasattr(event, "group_id"):
            await add_to_group(event.group_id, message)
    except Exception as e:
        logger.error(f"Error occurred when adding self-reply: {e}")


async def add_send_mface(tools,config):
    mface_list = os.listdir("data/pictures/Mface")
    if config.api["llm"]["model"] == "gemini":

        tools["function_declarations"].append({
            "name": "call_send_mface",
            "description": "根据当前聊天内容发送一张表情包，建议尽可能多地使用此功能，增加聊天趣味性。即使用户没有要求你也要发送表情包。",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": f"表情包。可选{mface_list}"
                    }
                },
                "required": [
                    "summary"
                ]
            }
        }, )
    else:
        tools.append({
            "type": "function",
            "function": {
                "name": "call_send_mface",
                "description": "根据当前聊天内容发送一张表情包，建议尽可能多地使用此功能，增加聊天趣味性。即使用户没有要求你也要发送表情包。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": f"表情包。可选{mface_list}"
                        }
                    },
                    "required": [
                        "summary"
                    ],
                    "additionalProperties": False
                }
            }
        })
    return tools

#asyncio.run(openaiRequest("1"))