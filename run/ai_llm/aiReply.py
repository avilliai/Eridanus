import asyncio
import datetime
import traceback

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from framework_common.database_util.Group import clear_group_messages
from run.ai_llm.service.aiReplyCore import aiReplyCore, end_chat, judge_trigger, send_text ,count_tokens_approximate
from framework_common.database_util.llmDB import delete_user_history, clear_all_history, change_folder_chara, \
    get_folder_chara, set_all_users_chara, clear_all_users_chara, clear_user_chara, get_user_history, \
    delete_latest2_history

from framework_common.database_util.User import get_user,update_user
from framework_common.database_util.Group import get_group_messages
from run.ai_llm.service.auto_talk import check_message_similarity

from framework_common.framework_util.func_map_loader import gemini_func_map, openai_func_map
from developTools.message.message_components import Text, At
import random

def main(bot,config):

      # 持续注意用户发言
    if config.ai_llm.config["llm"]["func_calling"]:
        if config.ai_llm.config["llm"]["model"] == "gemini":
            tools = gemini_func_map()
        else:
            tools = openai_func_map()

    else:
        tools = None
    if config.ai_llm.config["llm"]["联网搜索"]:
      if config.ai_llm.config["llm"]["model"] == "gemini":
          if tools is None:
              tools = [

                  {"googleSearch": {}},
              ]
          else:
              tools = [
                  {"googleSearch": {}},
                  tools
              ]
      else:
          if tools is None:
              tools = [{"type": "function", "function": {"name": "googleSearch"}}]
          else:
              tools = [
                  {"type": "function", "function": {"name": "googleSearch"}},
                  tools
              ]

    global user_state
    user_state = {}



    @bot.on(GroupMessageEvent)
    async def aiReply(event: GroupMessageEvent):
        await check_commands(event)
        if (event.message_chain.has(At) and event.message_chain.get(At)[0].qq==bot.id
                or prefix_check(str(event.pure_text),config.ai_llm.config["llm"]["prefix"])  #前缀判断
                or await judge_trigger(event.processed_message, event.user_id, config, tools=tools, bot=bot,event=event)): #触发cd判断
            bot.logger.info(f"接受消息{event.processed_message}")

            ## 权限判断
            user_info = await get_user(event.user_id, event.sender.nickname)
            if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_group"]:
                await bot.send(event,"你没有足够的权限使用该功能~")
                return
            if event.group_id==913122269 and not user_info.permission >= 66:
                #await bot.send(event,"你没有足够的权限使用该功能哦~")
                return
            if not user_info.permission >= config.ai_llm.config["core"]["ai_token_limt"]:
                if user_info.ai_token_record >= config.ai_llm.config["core"]["ai_token_limt_token"]:
                    await bot.send(event,"您的ai对话token已用完，请耐心等待下一次刷新～～")
                    return
            await handle_message(event)
        
        elif (config.ai_llm.config["llm"]["仁济模式"]["随机回复概率"] > 0): # 仁济模式第一层(随机)
            if random.randint(1, 100) < config.ai_llm.config["llm"]["仁济模式"]["随机回复概率"]:
                bot.logger.info(f"接受消息{event.processed_message}")

                ## 权限判断
                user_info = await get_user(event.user_id, event.sender.nickname)
                if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_group"]:
                    return
                if event.group_id==913122269 and not user_info.permission >= 66:
                    return
                if not user_info.permission >= config.ai_llm.config["core"]["ai_token_limt"]:
                    if user_info.ai_token_record >= config.ai_llm.config["core"]["ai_token_limt_token"]:
                        return
                await handle_message(event)
        
        elif (config.ai_llm.config["llm"]["仁济模式"]["算法回复"]["enable"]): # 仁济模式第二层(算法判断)
            sentences = await get_group_messages(event.group_id, config.ai_llm.config["llm"]["可获取的群聊上下文长度"])
            if await check_message_similarity(str(event.pure_text),sentences,similarity_threshold = config.ai_llm.config["llm"]["仁济模式"]["算法回复"]["相似度阈值"],frequency_threshold = config.ai_llm.config["llm"]["仁济模式"]["算法回复"]["频率阈值"],min_list_size = config.ai_llm.config["llm"]["仁济模式"]["算法回复"]["消息列表最小长度"],entropy_threshold = config.ai_llm.config["llm"]["仁济模式"]["算法回复"]["信息熵阈值"]):
                bot.logger.info(f"接受消息{event.processed_message}")

                ## 权限判断
                user_info = await get_user(event.user_id, event.sender.nickname)
                if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_group"]:
                    return
                if event.group_id==913122269 and not user_info.permission >= 66:
                    return
                if not user_info.permission >= config.ai_llm.config["core"]["ai_token_limt"]:
                    if user_info.ai_token_record >= config.ai_llm.config["core"]["ai_token_limt_token"]:
                        return
                await handle_message(event)

    async def handle_message(event):
        global user_state
        # 锁机制
        uid = event.user_id
        user_info = await get_user(event.user_id)
        # 初始化该用户的状态
        if uid not in user_state:
            user_state[uid] = {
                "queue": asyncio.Queue(),
                "running": False
            }

        await user_state[uid]["queue"].put(event)

        if user_state[uid]["running"]:
            bot.logger.info(f"用户{uid}正在处理中，已放入队列")
            return

        async def process_user_queue(uid):
            user_state[uid]["running"] = True
            try:

                current_event = await user_state[uid]["queue"].get()
                try:
                    reply_message = await aiReplyCore(
                        current_event.processed_message,
                        current_event.user_id,
                        config,
                        tools=tools,
                        bot=bot,
                        event=current_event,
                    )
                    if reply_message is None or '' == str(
                            reply_message) or 'Maximum recursion depth' in reply_message:
                        return
                    # print(f'reply_message:{reply_message}')
                    if "call_send_mface(summary='')" in reply_message:
                        reply_message = reply_message.replace("call_send_mface(summary='')", '')
                    # print(f"{current_event.processed_message[1]['text']}\n{reply_message}")
                    try:
                        tokens_total = count_tokens_approximate(current_event.processed_message[1]['text'],
                                                                reply_message, user_info.ai_token_record)
                        await update_user(user_id=event.user_id, ai_token_record=tokens_total)
                    except:
                        pass
                    await send_text(bot, event, config, reply_message.strip())
                except Exception as e:
                    bot.logger.exception(f"用户 {uid} 处理出错: {e}")
                finally:
                    user_state[uid]["queue"].task_done()
                    #print(user_state[uid]["queue"])
                    """
                    总结用户特征，伪长期记忆人格
                    """
                    if config.ai_llm.config["llm"]["长期记忆"]:
                        if user_info.portrait_update_time=="" or (datetime.datetime.now()-datetime.datetime.fromisoformat(user_info.portrait_update_time)).total_seconds()>config.ai_llm.config["llm"]["记忆更新间隔"]:
                            bot.logger.info(f"更新用户 {event.user_id} 设定")
                            reply_message = await aiReplyCore(
                                [{'text':'system: 对以上聊天内容做出总结，描绘出当前对话的用户画像，总结出当前用户的人物性格特征以及偏好。不要回复，直接给出结果'}],
                                current_event.user_id,
                                config,
                                bot=bot,
                                event=current_event,
                            )
                            await update_user(event.user_id,user_portrait=reply_message.strip())
                            await update_user(event.user_id, portrait_update_time=datetime.datetime.now().isoformat())
                            await delete_latest2_history(event.user_id)
                    if not user_state[uid]["queue"].empty():
                        asyncio.create_task(process_user_queue(uid))
            finally:
                user_state[uid]["running"] = False


        asyncio.create_task(process_user_queue(uid))





    async def check_commands(event):
        if event.message_chain.has(Text):
            t=event.message_chain.get(Text)[0].text.strip()
        else:
            t=""
        user_info = await get_user(event.user_id)
        if event.pure_text == "退出":
            await end_chat(event.user_id)
            await bot.send(event, "退出聊天~")
        elif event.pure_text == "/clear" or t == "/clear":
            await delete_user_history(event.user_id)
            await clear_group_messages(event.group_id)
            await bot.send(event, "历史记录已清除", True)
        elif event.pure_text == "/clear group":
            await clear_group_messages(event.group_id)
            await bot.send(event, "本群消息已清除", True)
        elif event.pure_text == "/clearall" and event.user_id == config.common_config.basic_config["master"]["id"]:
            await clear_all_history()
            await bot.send(event, "已清理所有用户的对话记录")
        elif event.pure_text.startswith("/clear") and event.user_id == config.common_config.basic_config["master"]["id"] and event.get("at"):
            await delete_user_history(event.get("at")[0]["qq"])
            await bot.send(event, [Text("已清理与目标用户的对话记录")])
        elif event.pure_text.startswith("/切人设 ") and user_info.permission >= config.ai_llm.config["core"]["ai_change_character"]:
            chara_file = str(event.pure_text).replace("/切人设 ", "")
            if chara_file == "0":
                reply = await clear_user_chara(event.user_id)
            else:
                reply = await change_folder_chara(chara_file, event.user_id)
            await bot.send(event, reply, True)
        elif event.pure_text.startswith("/全切人设 ") and event.user_id == config.common_config.basic_config["master"][
            "id"]:
            chara_file = str(event.pure_text).replace("/全切人设 ", "")
            if chara_file == "0":
                reply = await clear_all_users_chara()
            else:
                reply = await set_all_users_chara(chara_file)
            await bot.send(event, reply, True)
        elif event.pure_text == "/查人设":
            chara_file = str(event.pure_text).replace("/查人设", "")
            all_chara = await get_folder_chara()
            await bot.send(event, all_chara)
    def prefix_check(message:str,prefix:list):
        for p in prefix:
            if message.startswith(p):
                bot.logger.info(f"消息{message}匹配到关键词{p}")
                return True
        return False

    @bot.on(PrivateMessageEvent)
    async def aiReply(event):
      # print(event.processed_message)
      # print(event.message_id,type(event.message_id))
      if event.pure_text == "/clear":
          await delete_user_history(event.user_id)
          await bot.send(event, "历史记录已清除", True)
      elif event.pure_text == "/clearall" and event.user_id == config.common_config.basic_config["master"]["id"]:
          await clear_all_history()
          await bot.send(event, "已清理所有用户的对话记录")
      else:

          bot.logger.info(f"私聊接受消息{event.processed_message}")
          user_info = await get_user(event.user_id, event.sender.nickname)
          if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_private"]:
              await bot.send(event, "你没有足够的权限使用该功能哦~")
              return
            # 锁机制
          await handle_message(event)

