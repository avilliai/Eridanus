import datetime
import json
import random
import re
import time
import traceback
from collections import defaultdict
import os

import asyncio

from developTools.message.message_components import Record, Text, Node, Image
from developTools.utils.logger import get_logger
from framework_common.database_util.Group import get_last_20_and_convert_to_prompt, add_to_group
from run.ai_llm.service.aiReplyHandler.default import defaultModelRequest
from run.ai_llm.service.aiReplyHandler.gemini import geminiRequest, construct_gemini_standard_prompt, \
    get_current_gemini_prompt
from run.ai_llm.service.aiReplyHandler.openai import openaiRequest, construct_openai_standard_prompt, \
    get_current_openai_prompt, construct_openai_standard_prompt_old_version, \
    openaiRequest_official
from run.ai_llm.service.aiReplyHandler.tecentYuanQi import construct_tecent_standard_prompt, YuanQiTencent
from framework_common.database_util.llmDB import get_user_history, update_user_history, delete_user_history, read_chara, \
    use_folder_chara

from framework_common.database_util.User import get_user, update_user
import importlib

from run.ai_voice.service.tts import TTS

Tts = TTS()


def call_func(*args, **kwargs):
    # 运行时动态导入，避免循环导入
    func_map = importlib.import_module("framework_common.framework_util.func_map")
    return func_map.call_func(*args, **kwargs)


last_trigger_time = defaultdict(float)

logger = get_logger()


async def judge_trigger(processed_message, user_id, config, tools=None, bot=None, event=None, system_instruction=None,
                        func_result=False):
    trigger = False
    if event.user_id in last_trigger_time:
        bot.logger.info(f"last_trigger_time: {last_trigger_time.get(event.user_id)}")
        if (time.time() - last_trigger_time.get(event.user_id)) <= config.ai_llm.config["llm"]["focus_time"]:
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


async def aiReplyCore(processed_message, user_id, config, tools=None, bot=None, event=None, system_instruction=None,
                      func_result=False, recursion_times=0, do_not_read_context=False):  # 后面几个函数都是供函数调用的场景使用的
    logger.info(f"aiReplyCore called with message: {processed_message}")
    """
    递归深度约束
    """
    if recursion_times > config.ai_llm.config["llm"]["recursion_limit"]:
        logger.warning(f"roll back to original history, recursion times: {recursion_times}")
        return "Maximum recursion depth exceeded.Please try again later."
    """
    初始值
    """
    reply_message = ""
    original_history = []
    mface_files = None
    if tools is not None and config.ai_llm.config["llm"]["表情包发送"]:
        tools = await add_send_mface(tools, config)
    if not system_instruction:
        if config.ai_llm.config["llm"]["system"]:
            system_instruction = await read_chara(user_id, config.ai_llm.config["llm"]["system"])
        else:
            system_instruction = await read_chara(user_id, await use_folder_chara(
                config.ai_llm.config["llm"]["chara_file_name"]))
        user_info = await get_user(user_id)
        system_instruction = system_instruction.replace("{用户}", user_info.nickname).replace("{bot_name}",
                                                                                              config.common_config.basic_config["bot"])
    """
    用户设定读取
    """
    if config.ai_llm.config["llm"]["长期记忆"]:
        temp_user=await get_user(user_id)
        system_instruction+=f"\n以下为当前用户的用户画像：{temp_user.user_portrait}"

    try:
        if recursion_times == 0 and processed_message:
            last_trigger_time[user_id] = time.time()
        if config.ai_llm.config["llm"]["model"] == "default":
            prompt, original_history = await construct_openai_standard_prompt(processed_message, system_instruction,
                                                                              user_id)
            response_message = await defaultModelRequest(
                prompt,
                config.common_config.basic_config["proxy"]["http_proxy"] if config.ai_llm.config["llm"][
                    "enable_proxy"] else None,
            )
            reply_message = response_message['content']
            await prompt_database_updata(user_id, response_message, config)

        elif config.ai_llm.config["llm"]["model"] == "openai":
            if processed_message:
                if config.ai_llm.config["llm"]["openai"]["使用旧版prompt结构"]:
                    prompt, original_history = await construct_openai_standard_prompt_old_version(processed_message,
                                                                                                  system_instruction,
                                                                                                  user_id, bot,
                                                                                                  func_result, event)
                else:
                    prompt, original_history = await construct_openai_standard_prompt(processed_message,
                                                                                      system_instruction, user_id, bot,
                                                                                      func_result, event)
            else:
                prompt = await get_current_openai_prompt(user_id)
            if processed_message is None:  # 防止二次递归无限循环
                tools = None
            """
            读取上下文
            """
            if not do_not_read_context:
                p = await read_context(bot, event, config, prompt)
                if p:
                    prompt = p
            kwargs = {
                "ask_prompt": prompt,
                "url": config.ai_llm.config["llm"]["openai"].get("quest_url") or config.ai_llm.config["llm"][
                    "openai"].get("base_url"),
                "apikey": random.choice(config.ai_llm.config["llm"]["openai"]["api_keys"]),
                "model": config.ai_llm.config["llm"]["openai"]["model"],
                "stream": False,
                "proxy": config.common_config.basic_config["proxy"]["http_proxy"] if config.ai_llm.config["llm"][
                    "enable_proxy"] else None,
                "tools": tools,
                "temperature": config.ai_llm.config["llm"]["openai"]["temperature"],
                "max_tokens": config.ai_llm.config["llm"]["openai"]["max_tokens"]
            }
            if config.ai_llm.config["llm"]["openai"]["enable_official_sdk"]:
                response_message = await openaiRequest_official(**kwargs)
            else:
                response_message = await openaiRequest(**kwargs)
            if "content" in response_message:
                reply_message = response_message["content"]
                if reply_message is not None:
                    reply_message, mface_files = remove_mface_filenames(reply_message, config)  # 去除表情包文件名
                    pattern_think = r"<think>\n(.*?)\n</think>"
                    match_think = re.search(pattern_think, reply_message, re.DOTALL)

                    if match_think:
                        think_text = match_think.group(1)
                        if config.ai_llm.config["llm"]["openai"]["CoT"]:
                            await bot.send(event, [Node(content=[Text(think_text)])])
                        pattern_rest = r"</think>\n\n(.*?)$"
                        match_rest = re.search(pattern_rest, reply_message, re.DOTALL)
                        if match_rest:
                            reply_message = match_rest.group(1)
                    else:
                        if "reasoning_content" in response_message:
                            if config.ai_llm.config["llm"]["openai"]["CoT"]:
                                await bot.send(event, [Node(content=[Text(response_message["reasoning_content"])])])
                            response_message.pop("reasoning_content")
            else:
                reply_message = None

            # 检查是否存在函数调用，如果还有提示词就发
            status = False
            if "tool_calls" in response_message and response_message['tool_calls'] is not None:
                status = True

            if status and reply_message is not None:
                await send_text(bot, event, config, reply_message)
                reply_message = None

            # 函数调用
            temp_history = []
            func_call = False

            if mface_files != [] and mface_files is not None:
                for mface_file in mface_files:
                    await bot.send(event, Image(file=mface_file))
                mface_files = []

            if "tool_calls" in response_message and response_message['tool_calls'] is not None:
                for part in response_message['tool_calls']:
                    func_name = part['function']["name"]
                    args = part['function']['arguments']
                    if func_name == "call_send_mface" and mface_files == []:
                        temp_history.append({
                            "role": "tool",
                            "content": json.dumps({"status": "succeed"}),
                            "name": "call_send_mface",
                            # Here we specify the tool_call_id that this result corresponds to
                            "tool_call_id": part['id']
                        })
                    else:
                        try:
                            r = await call_func(bot, event, config, func_name, json.loads(args))  # 真是到处都不想相互兼容。
                            if r == False:
                                await end_chat(user_id)
                            if r:
                                func_call = True
                                temp_history.append({
                                    "role": "tool",
                                    "content": json.dumps(r),
                                    "name": func_name,
                                    # Here we specify the tool_call_id that this result corresponds to
                                    "tool_call_id": part['id']
                                })
                            else:
                                temp_history.append({
                                    "role": "tool",
                                    "content": json.dumps({"status": "succeed"}),
                                    "name": func_name,
                                    # Here we specify the tool_call_id that this result corresponds to
                                    "tool_call_id": part['id']
                                })
                        except Exception as e:
                            # logger.error(f"Error occurred when calling function: {e}")
                            logger.error(f"Error occurred when calling function: {e}")
                            traceback.print_exc()
                            temp_history.append({
                                "role": "tool",
                                "content": json.dumps({"status": "failed to call function"}),
                                "name": func_name,
                                # Here we specify the tool_call_id that this result corresponds to
                                "tool_call_id": part['id']
                            })

                    # 函数成功调用，如果函数调用有附带文本，则把这个b文本改成None。
                    reply_message = None

            await prompt_database_updata(user_id, response_message, config)
            for i in temp_history:
                await prompt_database_updata(user_id, i, config)
            if func_call:
                final_response = await aiReplyCore(None, user_id, config, tools=tools, bot=bot, event=event,
                                                   system_instruction=system_instruction, func_result=True)
                return final_response

            # print(response_message)
        elif config.ai_llm.config["llm"]["model"] == "gemini":
            if processed_message:
                prompt, original_history = await construct_gemini_standard_prompt(processed_message, user_id, bot,
                                                                                  func_result, event)
                if not do_not_read_context:
                    p = await read_context(bot, event, config, prompt)
                    if p:
                        prompt = p
            else:
                prompt = await get_current_gemini_prompt(user_id)
                if not do_not_read_context:
                    p = await read_context(bot, event, config, prompt)
                    if p:
                        prompt = p
            if processed_message is None:  # 防止二次递归无限循环
                tools = None
            # 这里是需要完整报错的，不用try catch，否则会影响自动重试。
            response_message = await geminiRequest(
                prompt,
                config.ai_llm.config["llm"]["gemini"]["base_url"],
                random.choice(config.ai_llm.config["llm"]["gemini"]["api_keys"]),
                config.ai_llm.config["llm"]["gemini"]["model"],
                config.common_config.basic_config["proxy"]["http_proxy"] if config.ai_llm.config["llm"][
                    "enable_proxy"] else None,
                tools=tools,
                system_instruction=system_instruction,
                temperature=config.ai_llm.config["llm"]["gemini"]["temperature"],
                maxOutputTokens=config.ai_llm.config["llm"]["gemini"]["maxOutputTokens"]
            )

            # print(response_message)
            try:
                reply_message = response_message["parts"][0]["text"]  # 函数调用可能不给你返回提示文本，只给你整一个调用函数。
                reply_message, mface_files = remove_mface_filenames(reply_message, config)  # 去除表情包文件名
            except Exception as e:
                logger.error(f"Error occurred when processing gemini response: {e}")
                reply_message = None
            if reply_message is not None:
                if reply_message == "\n" or reply_message == "" or reply_message == " ":
                    raise Exception("Empty response。Gemini API返回的文本为空。")
            """
            gemini返回多段回复处理
            """
            try:
                text_elements = [part for part in response_message['parts'] if 'text' in part]
                if text_elements != [] and len(text_elements) > 1:
                    self_rep = []
                    for i in text_elements:
                        if i["text"] != "\n" and i["text"] != "":
                            tep_rep_message, mface_files = remove_mface_filenames(i['text'].strip(), config)  # 去除表情包文件名
                            self_rep.append({"text": tep_rep_message})
                            await send_text(bot, event, config, tep_rep_message)
                            reply_message = None
                            if mface_files != [] and mface_files is not None:
                                for mface_file in mface_files:
                                    await bot.send(event, Image(file=mface_file))
                                mface_files = []
                    self_message = {"user_name": config.common_config.basic_config["bot"], "user_id": 0000000,
                                    "message": self_rep}
                    if hasattr(event, "group_id"):
                        await add_to_group(event.group_id, self_message)
                    reply_message = None
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Error occurred when processing gemini response2: {e}")
            # 检查是否存在函数调用，如果还有提示词就发
            status = False

            for part in response_message["parts"]:
                if "functionCall" in part and config.ai_llm.config["llm"]["func_calling"]:
                    status = True

            if status and reply_message is not None:  # 有函数调用且有回复，就发回复和语音
                await send_text(bot, event, config, reply_message)
                reply_message = None

            if mface_files != [] and mface_files is not None:
                for mface_file in mface_files:
                    await bot.send(event, Image(file=mface_file))
                mface_files = []

            # 在函数调用之前触发更新上下文。
            await prompt_database_updata(user_id, response_message, config)
            # 函数调用
            new_func_prompt = []
            for part in response_message["parts"]:
                if "functionCall" in part:
                    func_name = part['functionCall']["name"]
                    args = part['functionCall']['args']
                    """
                    进行对表情包功能的特殊处理
                    """
                    if func_name == "call_send_mface" and mface_files == []:
                        pass
                    else:
                        """
                        正常调用函数
                        """
                        try:

                            r = await call_func(bot, event, config, func_name, args)
                            if r == False:
                                await end_chat(user_id)
                            if r:
                                func_r = {
                                    "functionResponse": {
                                        "name": func_name,
                                        "response": r
                                    }
                                }
                                new_func_prompt.append(func_r)
                        except Exception as e:
                            # logger.error(f"Error occurred when calling function: {e}")
                            logger.error(f"Error occurred when calling function: {func_name}")
                            traceback.print_exc()
                    await add_self_rep(bot, event, config, reply_message)
                    reply_message = None
            if new_func_prompt != []:
                await prompt_database_updata(user_id, {"role": "function", "parts": new_func_prompt}, config)
                # await add_gemini_standard_prompt({"role": "function","parts": new_func_prompt},user_id)# 更新prompt
                final_response = await aiReplyCore(None, user_id, config, tools=tools, bot=bot, event=event,
                                                   system_instruction=system_instruction, func_result=True)
                return final_response

        elif config.ai_llm.config["llm"]["model"] == "腾讯元器":
            prompt, original_history = await construct_tecent_standard_prompt(processed_message, user_id, bot, event)
            response_message = await YuanQiTencent(
                prompt,
                config.ai_llm.config["llm"]["腾讯元器"]["智能体ID"],
                config.ai_llm.config["llm"]["腾讯元器"]["token"],
                user_id,
            )
            reply_message = response_message["content"]
            response_message["content"] = [{"type": "text", "text": response_message["content"]}]

            await prompt_database_updata(user_id, response_message, config)

        logger.info(f"aiReplyCore returned: {reply_message}")
        await prompt_length_check(user_id, config)
        if reply_message is not None:
            reply_message = re.sub(r'```tool_code.*?```', '', reply_message, flags=re.DOTALL)
            reply_message = reply_message.replace('```', '').strip()
            return reply_message.strip()
        else:
            return reply_message
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        traceback.print_exc()
        logger.warning(f"roll back to original history, recursion times: {recursion_times}")
        await update_user_history(user_id, original_history)
        if recursion_times <= config.ai_llm.config["llm"]["recursion_limit"]:

            logger.warning(f"Recursion times: {recursion_times}")
            if recursion_times + 3 == config.ai_llm.config["llm"]["recursion_limit"] and config.ai_llm.config["llm"][
                "auto_clear_when_recursion_failed"]:
                logger.warning(f"clear ai reply history for user: {event.user_id}")
                await delete_user_history(event.user_id)
            if recursion_times+2 == config.ai_llm.config["llm"]["recursion_limit"]:
                logger.warning(f"update user portrait for user: {event.user_id}")
                await update_user(event.user_id, user_portrait="normal_user")
                await update_user(event.user_id, portrait_update_time=datetime.datetime.now().isoformat())
            return await aiReplyCore(processed_message, user_id, config, tools=tools, bot=bot, event=event,
                                     system_instruction=system_instruction, func_result=func_result,
                                     recursion_times=recursion_times + 1, do_not_read_context=True)
        else:
            return "Maximum recursion depth exceeded.Please try again later."


async def send_text(bot, event, config, text):
    text = re.sub(r'```tool_code.*?```', '', text, flags=re.DOTALL)
    text = text.replace('```', '').strip()
    if random.randint(0, 100) < config.ai_llm.config["llm"]["语音回复几率"]:
        if config.ai_llm.config["llm"]["语音回复附带文本"]:
            await bot.send(event, text.strip(), config.ai_llm.config["llm"]["Quote"])

        await tts_and_send(bot, event, config, text)
    else:
        await bot.send(event, text.strip(), config.ai_llm.config["llm"]["Quote"])


async def tts_and_send(bot, event, config, reply_message):
    async def _tts_and_send():
        try:
            bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
            path = await Tts.tts(reply_message, config=config, bot=bot)
            await bot.send(event, Record(file=path))
        except Exception as e:
            bot.logger.error(f"Error occurred when calling tts: {e}")
            if not config.ai_llm.config["llm"]["语音回复附带文本"]:
                await bot.send(event, reply_message.strip(), config.ai_llm.config["llm"]["Quote"])

    asyncio.create_task(_tts_and_send())


async def prompt_database_updata(user_id, response_message, config):
    history = await get_user_history(user_id)
    if len(history) > config.ai_llm.config["llm"]["max_history_length"]:
        del history[0]
        del history[0]
    history.append(response_message)
    await update_user_history(user_id, history)


async def prompt_length_check(user_id, config):
    history = await get_user_history(user_id)
    if len(history) > config.ai_llm.config["llm"]["max_history_length"]:
        while history[0]["role"] != "user":
            del history[0]
    await update_user_history(user_id, history)


async def read_context(bot, event, config, prompt):
    try:
        if event is None:
            return None
        if config.ai_llm.config["llm"]["读取群聊上下文"] == False or not hasattr(event, "group_id"):
            return None
        if config.ai_llm.config["llm"]["model"] == "gemini":
            group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id, config.ai_llm.config["llm"][
                "可获取的群聊上下文长度"], "gemini", bot)
        elif config.ai_llm.config["llm"]["model"] == "openai":
            if config.ai_llm.config["llm"]["openai"]["使用旧版prompt结构"]:
                group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id,
                                                                            config.ai_llm.config["llm"][
                                                                                "可获取的群聊上下文长度"],
                                                                            "old_openai", bot)
            else:
                group_messages_bg = await get_last_20_and_convert_to_prompt(event.group_id,
                                                                            config.ai_llm.config["llm"][
                                                                                "可获取的群聊上下文长度"],
                                                                            "new_openai", bot)
        else:
            return None
        bot.logger.info(f"群聊上下文消息：已读取")
        insert_pos = max(len(prompt) - 2, 0)  # 保证插入位置始终在倒数第二个元素之前
        if config.ai_llm.config["llm"]["model"] == "openai":  # 必须交替出现
            while prompt[insert_pos - 1]["role"] != "assistant":
                insert_pos += 1
        prompt = prompt[:insert_pos] + group_messages_bg + prompt[insert_pos:]
        return prompt
    except:
        return None


async def add_self_rep(bot, event, config, reply_message):
    if event is None or reply_message is None:
        return None
    if not config.ai_llm.config["llm"]["读取群聊上下文"] and not hasattr(event, "group_id"):
        return None
    try:
        self_rep = [{"text": reply_message.strip()}]
        message = {"user_name": config.basic_config["bot"], "user_id": 0000000, "message": self_rep}
        if hasattr(event, "group_id"):
            await add_to_group(event.group_id, message)
    except Exception as e:
        logger.error(f"Error occurred when adding self-reply: {e}")


def remove_mface_filenames(reply_message, config, directory="data/pictures/Mface"):
    try:
        """
        去除文本中的表情包文件名，并允许用户输入 () {} <> 的括号，最终匹配 [] 格式。
        现在支持 .gif 和 .png 文件。

        :param reply_message: 输入文本
        :param directory: 表情包目录
        :return: 处理后的文本和匹配的文件名列表（始终使用[]格式）
        """
        mface_list = os.listdir(directory)
        # 仅保留 [xxx].gif, [xxx].png, [xxx].jpg 格式的文件名
        mface_dict = {}
        for filename in mface_list:
            if filename.startswith("[") and (
                    filename.endswith("].gif") or filename.endswith("].png") or filename.endswith("].jpg")):
                core_name = filename[1:-5]
                mface_dict[core_name] = filename

        brackets = "\(\[\{\<"  # 开括号
        brackets_close = "\)\]\}\>"  # 闭括号
        pattern = rf"[{brackets}]([^\[\](){{}}<>]+)[{brackets_close}]\.(gif|png|jpg)"

        matched_files = []

        def replace_match(match):
            core_name, ext = match.groups()
            if core_name in mface_dict:
                file_path = os.path.normpath(os.path.join(directory, mface_dict[core_name])).replace("\\", "/")
                matched_files.append(file_path)
                return ""
            return ""

        cleaned_text = re.sub(pattern, replace_match, reply_message).strip()

        if matched_files:
            matched_files = matched_files[:config.ai_llm.config["llm"]["单次发送表情包数量"]]
            logger.info(f"mface 匹配到的文件名: {matched_files}")

        logger.info(f"mface 处理后的文本: {cleaned_text}")
        if matched_files == []:
            return cleaned_text, []
        return cleaned_text, matched_files
    except Exception as e:
        logger.error(f"Error occurred when removing mface filenames: {e}")
        traceback.print_exc()
        return reply_message, []


async def add_send_mface(tools, config):
    mface_list = os.listdir("data/pictures/Mface")
    if config.ai_llm.config["llm"]["model"] == "gemini":
        tools["function_declarations"] = [
            func for func in tools["function_declarations"]
            if func.get("name") != "call_send_mface"
        ]

        tools["function_declarations"].append({
            "name": "call_send_mface",
            "description": "根据当前聊天内容选择一张表情包，只可从给定列表选取，只可选择一张，建议尽可能多地使用此函数，即使用户没有要求你也要调用此函数选择表情包。表情包仅可通过此函数发送给用户，选择的表情包名称不能出现在回复消息中。不要通过send函数发送表情包。请勿在回复文本中混入表情包，例如 你好呀[你好].gif 是无效的且不被允许的组合方式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": f"表情包。可选{mface_list}，将选择的结果输入此函数以记录并发送。"
                    }
                },
                "required": [
                    "summary"
                ]
            }
        }, )
    else:
        tools = [
            tool for tool in tools
            if not (tool.get("function", {}).get("name") == "call_send_mface")
        ]
        tools.append({
            "type": "function",
            "function": {
                "name": "call_send_mface",
                "description": "根据当前聊天内容选择一张表情包，只可从给定列表选取，只可选择一张，建议尽可能多地使用此函数，即使用户没有要求你也要调用此函数选择表情包。表情包仅可通过此函数发送给用户，选择的表情包名称不能出现在回复消息中。不要通过send函数发送表情包。请勿在回复文本中混入表情包，例如 你好呀[你好].gif 是无效的且不被允许的组合方式。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": f"表情包。可选{mface_list}，将选择的结果输入此函数以记录并发送。"
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


# asyncio.run(openaiRequest("1"))
def count_tokens_approximate(input_text, output_text, token_ori=None):
    """
    后续使用api调用返回的tokens计数。
    """

    def tokenize(text):
        # 英文和数字：按空格分词，同时考虑标点符号和特殊符号
        english_tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        # 中文：每个汉字单独作为一个 token
        chinese_tokens = re.findall(r'[\u4e00-\u9fff]', text)
        # 合并英文和中文 token
        tokens = english_tokens + chinese_tokens
        return tokens

    input_tokens = tokenize(input_text)
    output_tokens = tokenize(output_text)
    add_token = len(input_tokens) + len(output_tokens)
    if token_ori is not None:
        total_token = add_token + token_ori
    else:
        total_token = add_token
    return total_token
