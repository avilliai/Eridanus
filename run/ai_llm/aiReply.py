import asyncio

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from framework_common.database_util.Group import clear_group_messages
from framework_common.framework_util.yamlLoader import YAMLManager
from run.ai_llm.service.aiReplyCore import aiReplyCore, end_chat, judge_trigger, send_text ,count_tokens_approximate
from framework_common.database_util.llmDB import delete_user_history, clear_all_history, change_folder_chara, get_folder_chara, set_all_users_chara, clear_all_users_chara, clear_user_chara

from framework_common.database_util.User import get_user,update_user

from framework_common.framework_util.func_map_loader import gemini_func_map, openai_func_map
from developTools.message.message_components import Text, At


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
                tools=[

                    { "googleSearch": {} },
                    ]
            else:
                tools=[
                    { "googleSearch": {} },
                    tools
                ]
                print(tools)


    locks = {}
    queues = {}
    '''@bot.on(GroupMessageEvent) #测试异步
    async def aiReplys(event):
        await sleep(10)
        await bot.send(event,"async task over")'''
    @bot.on(GroupMessageEvent)
    async def aiReply(event: GroupMessageEvent):
        if event.message_chain.has(Text):
            t=event.message_chain.get(Text)[0].text.strip()
        else:
            t=""
        #print(event.processed_message)
        #print(event.message_id,type(event.message_id))
        user_info = await get_user(event.user_id, event.sender.nickname)
        if event.pure_text=="退出":
            await end_chat(event.user_id)
            await bot.send(event,"退出聊天~")
        elif event.pure_text=="/clear" or t=="/clear":
            await delete_user_history(event.user_id)
            await clear_group_messages(event.group_id)

            await bot.send(event,"历史记录已清除",True)
        elif event.pure_text=="/clear group":
            await clear_group_messages(event.group_id)
            await bot.send(event,"本群消息已清除",True)
        elif event.pure_text=="/clearall" and event.user_id == config.config.basic_config["master"]["id"]:
            await clear_all_history()
            await bot.send(event, "已清理所有用户的对话记录")
        elif event.pure_text.startswith("/clear") and event.user_id == config.config.basic_config["master"]["id"] and event.get("at"):
            await delete_user_history(event.get("at")[0]["qq"])
            await bot.send(event, [Text("已清理"),At(event.get('at')[0]['qq']),Text(" 的对话记录")])
        elif event.pure_text.startswith("/切人设 ") and user_info.permission >= config.ai_llm.config["core"]["ai_change_character"]:
            chara_file = str(event.pure_text).replace("/切人设 ", "")
            if chara_file == "0":
                reply = await clear_user_chara(event.user_id)
            else:
                reply = await change_folder_chara(chara_file, event.user_id)
            await bot.send(event, reply, True)
        elif event.pure_text.startswith("/全切人设 ") and event.user_id == config.config.basic_config["master"]["id"]:
            chara_file = str(event.pure_text).replace("/全切人设 ", "")
            if chara_file == "0":
                reply = await clear_all_users_chara()
            else:
                reply = await set_all_users_chara(chara_file)
            await bot.send(event, reply, True)
        elif event.pure_text=="/查人设":
            chara_file = str(event.pure_text).replace("/查人设", "")
            all_chara = await get_folder_chara()
            await bot.send(event, all_chara)
        elif event.get("at") and event.get("at")[0]["qq"]==str(bot.id) or prefix_check(str(event.pure_text),config.ai_llm.config["llm"]["prefix"]) or await judge_trigger(event.processed_message, event.user_id, config, tools=tools, bot=bot,event=event):
            bot.logger.info(f"接受消息{event.processed_message}")
            user_info = await get_user(event.user_id, event.sender.nickname)
            if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_group"]:
                await bot.send(event,"你没有足够的权限使用该功能哦~")
                return
            if not user_info.permission >= config.ai_llm.config["core"]["ai_token_limt"]:
                if user_info.ai_token_record >= config.ai_llm.config["core"]["ai_token_limt_token"]:
                    await bot.send(event,"您的ai对话token已用完，请耐心等待下一次刷新～～")
                    return

            #锁机制
            if event.user_id not in locks:
                locks[event.user_id] = asyncio.Lock()
                queues[event.user_id] = asyncio.Queue()
            await queues[event.user_id].put(event)
            if locks[event.user_id].locked():
                bot.logger.info(f"用户{event.user_id}正在处理消息，放入队列")
                return

            # 处理队列中的请求
            async with locks[event.user_id]:  # 只有一个协程能执行
                while not queues[event.user_id].empty():
                    current_event = await queues[event.user_id].get()  # 取出排队中的请求
                    reply_message = await aiReplyCore(
                        current_event.processed_message,
                        current_event.user_id,
                        config,
                        tools=tools,
                        bot=bot,
                        event=current_event,
                    )
                    if reply_message is None or '' == str(reply_message) or 'Maximum recursion depth' in reply_message:
                        return
                    #print(f'reply_message:{reply_message}')
                    if "call_send_mface(summary='')" in reply_message:
                        reply_message = reply_message.replace("call_send_mface(summary='')", '')
                    #print(f"{current_event.processed_message[1]['text']}\n{reply_message}")
                    try:
                        tokens_total=count_tokens_approximate(current_event.processed_message[1]['text'],reply_message,user_info.ai_token_record)
                        await update_user(user_id=event.user_id, ai_token_record=tokens_total)
                    except:
                        pass
                    await send_text(bot,event,config,reply_message.strip())



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
      elif event.pure_text == "/clearall" and event.user_id == config.config.basic_config["master"]["id"]:
          await clear_all_history()
          await bot.send(event, "已清理所有用户的对话记录")
      else:
          if event.user_id == 1270858640: return
          bot.logger.info(f"私聊接受消息{event.processed_message}")
          user_info = await get_user(event.user_id, event.sender.nickname)
          if not user_info.permission >= config.ai_llm.config["core"]["ai_reply_private"]:
              await bot.send(event, "你没有足够的权限使用该功能哦~")
              return
            # 锁机制
          if event.user_id not in locks:
              locks[event.user_id] = asyncio.Lock()
              queues[event.user_id] = asyncio.Queue()
          await queues[event.user_id].put(event)
          if locks[event.user_id].locked():
              bot.logger.info(f"用户{event.user_id}正在处理消息，放入队列")
              return
          async with locks[event.user_id]:  # 只有一个协程能执行
              while not queues[event.user_id].empty():
                  current_event = await queues[event.user_id].get()  # 取出排队中的请求
                  reply_message = await aiReplyCore(
                      current_event.processed_message,
                      current_event.user_id,
                      config,
                      tools=tools,
                      bot=bot,
                      event=current_event,
                  )
                  # reply_message=await aiReplyCore(event.processed_message,event.user_id,config,tools=tools,bot=bot,event=event)
                  if reply_message is not None:
                      await send_text(bot,event,config,reply_message.strip())

