import random

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Record
from plugins.core.aiReplyCore import aiReplyCore, end_chat, judge_trigger, aireply_history_add
from plugins.core.llmDB import delete_user_history, clear_all_history, change_folder_chara, get_folder_chara, set_all_users_chara, clear_all_users_chara, clear_user_chara
from plugins.core.tts.tts import tts
from plugins.core.userDB import get_user
from plugins.func_map_loader import gemini_func_map, openai_func_map
from developTools.message.message_components import Record, Text, Node, At

input_text_list = {}

def clear_by_qq(data, target_qq):
    # 删除符合条件的子列表
    data[:] = [
        item for item in data
        if not any(
            user.get('user_info', '').find(f'qq号为{target_qq}') != -1
            for user in item
        )
    ]

def main(bot,config):
      # 持续注意用户发言
    if config.api["llm"]["func_calling"]:
        if config.api["llm"]["model"] == "gemini":
            tools = gemini_func_map()
        else:
            tools = openai_func_map()
    else:
        tools = None
    if config.api["llm"]["联网搜索"]:
        if config.api["llm"]["model"] == "gemini":
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
    '''@bot.on(GroupMessageEvent) #测试异步
    async def aiReplys(event):
        await sleep(10)
        await bot.send(event,"async task over")'''
    @bot.on(GroupMessageEvent)
    async def aiReply(event):
        #print(event.processed_message)
        #print(event.message_id,type(event.message_id))
        global input_text_list
        #print(event.processed_message)
        #print(event.message_id,type(event.message_id))
        user_info = await get_user(event.user_id, event.sender.nickname)
        if config.api["llm"]["上下文读取模式"] == 1:
            max_memory = int(config.api["llm"]["群聊临时记录消息数"])
            user_info_str = "qq号为{},昵称为{}".format(user_info[0], user_info[1])
            user_info_dict = {'user_info': user_info_str}
            processed_message_with_user_info = [user_info_dict] + event.processed_message + [{"msg_id": f"消息id为{str(event.message_id)}"}]
            if event.group_id not in input_text_list:
                input_text_list[event.group_id] = []
            input_text_list[event.group_id].append(processed_message_with_user_info)
            if len(input_text_list[event.group_id]) > max_memory:
                input_text_list[event.group_id].pop(0)
        if event.raw_message=="退出":
            await end_chat(event.user_id)
            if config.api["llm"]["上下文读取模式"] == 1:
                clear_by_qq(input_text_list[event.group_id], event.user_id)
            await bot.send(event,"那就先不聊啦~")
        elif event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            if config.api["llm"]["上下文读取模式"] == 1:
                clear_by_qq(input_text_list[event.group_id], event.user_id)
            await bot.send(event,"历史记录已清除",True)
        elif event.raw_message=="/clearall" and event.user_id == config.basic_config["master"]["id"]:
            await clear_all_history()
            if config.api["llm"]["上下文读取模式"] == 1:
                  input_text_list[event.group_id] = []
            await bot.send(event, "已清理所有用户的对话记录")
        elif event.raw_message.startswith("/clear") and event.user_id == config.basic_config["master"]["id"] and event.get("at"):
            if config.api["llm"]["上下文读取模式"] == 1:
                clear_by_qq(input_text_list[event.group_id], event.get("at")[0]["qq"])
            await bot.send(event, [Text("已清理"),At(event.get('at')[0]['qq']),Text(" 的对话记录")])
        elif event.raw_message.startswith("/切人设 ") and user_info[6] >= config.controller["core"]["ai_change_character"]:
            chara_file = str(event.raw_message).replace("/切人设 ", "")
            if chara_file == "0":
                reply = await clear_user_chara(event.user_id)
            else:
                reply = await change_folder_chara(chara_file, event.user_id)
            if config.api["llm"]["上下文读取模式"] == 1:
                clear_by_qq(input_text_list[event.group_id], event.user_id)
            await bot.send(event, reply, True)
        elif event.raw_message.startswith("/全切人设 ") and event.user_id == config.basic_config["master"]["id"]:
            chara_file = str(event.raw_message).replace("/全切人设 ", "")
            if chara_file == "0":
                reply = await clear_all_users_chara()
            else:
                reply = await set_all_users_chara(chara_file)
            if config.api["llm"]["上下文读取模式"] == 1:
                  input_text_list[event.group_id] = []
            await bot.send(event, reply, True)
        elif event.raw_message=="/查人设":
            chara_file = str(event.raw_message).replace("/查人设", "")
            all_chara = await get_folder_chara()
            await bot.send(event, all_chara)
        elif event.get("at") and event.get("at")[0]["qq"]==str(bot.id) or prefix_check(str(event.raw_message),config.api["llm"]["prefix"]):
            bot.logger.info(f"接受消息{event.processed_message}")
            user_info = await get_user(event.user_id, event.sender.nickname)
            if not user_info[6] >= config.controller["core"]["ai_reply_group"]:
                await bot.send(event,"你没有足够的权限使用该功能哦~")
                return
            if int(config.api["llm"]["上下文读取模式"]) ==0:
                reply_message=await aiReplyCore(event.processed_message,event.user_id,config,tools=tools,bot=bot,event=event)
            elif int(config.api["llm"]["上下文读取模式"]) == 1:
                if event.group_id not in input_text_list:
                    input_text_list[event.group_id] = []
                for item in input_text_list[event.group_id][:-1]:  # 使用切片操作排除最后一项
                    await aireply_history_add(
                        item,  # 这里将 item 作为参数传递给 aireply_history_add
                        event.user_id,
                        config,
                        tools=tools,
                        bot=bot,
                        event=event
                    )
                reply_message=await aiReplyCore(event.processed_message,event.user_id,config,tools=tools,bot=bot,event=event)
            if reply_message=="Maximum recursion depth exceeded.Please try again later.": await delete_user_history(event.user_id)
            if reply_message is not None:
                if random.randint(0,100)<config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path=await tts(reply_message,config=config,bot=bot)
                        await bot.send(event,Record(file=path))
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])

                else:
                    await bot.send(event,reply_message,config.api["llm"]["Quote"])
        else:
            reply_message = await judge_trigger(event.processed_message, event.user_id, config, tools=tools, bot=bot,event=event)
            if reply_message=="Maximum recursion depth exceeded.Please try again later.": await delete_user_history(event.user_id)
            if reply_message is not None:
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path = await tts(reply_message, config=config,bot=bot)
                        await bot.send(event, Record(file=path))
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])

                else:
                    await bot.send(event, reply_message, config.api["llm"]["Quote"])
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
      if event.raw_message == "/clear":
          await delete_user_history(event.user_id)
          await bot.send(event, "历史记录已清除", True)
      elif event.raw_message == "/clearall" and event.user_id == config.basic_config["master"]["id"]:
          await clear_all_history()
          await bot.send(event, "已清理所有用户的对话记录")
      else:
          bot.logger.info(f"私聊接受消息{event.processed_message}")
          user_info = await get_user(event.user_id, event.sender.nickname)
          if not user_info[6] >= config.controller["core"]["ai_reply_private"]:
              await bot.send(event, "你没有足够的权限使用该功能哦~")
              return
          reply_message = await aiReplyCore(event.processed_message, event.user_id, config, tools=tools, bot=bot,event=event)
          if reply_message is not None:
              if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                  if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])
                  try:
                      bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                      path = await tts(reply_message, config=config,bot=bot)
                      await bot.send(event, Record(file=path))
                  except Exception as e:
                      bot.logger.error(f"Error occurred when calling tts: {e}")
                  if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])

              else:
                  await bot.send(event, reply_message, config.api["llm"]["Quote"])
