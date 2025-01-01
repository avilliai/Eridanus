import os
import random
import time
from asyncio import sleep
from collections import defaultdict

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Reply, Record
from plugins.core.aiReplyCore import aiReplyCore, end_chat, judge_trigger
from plugins.core.llmDB import delete_user_history, clear_all_history
from plugins.core.aiReply_utils import prompt_elements_construct
from plugins.core.tts import tts
from plugins.core.userDB import get_user
from plugins.func_map_loader import func_map, gemini_func_map, openai_func_map


def main(bot,config):
      # 持续注意用户发言
    if config.api["llm"]["func_calling"]:
        if config.api["llm"]["model"] == "gemini":
            tools = gemini_func_map()
        else:
            tools = openai_func_map()
    else:
        tools = None
    '''@bot.on(GroupMessageEvent) #测试异步
    async def aiReplys(event):
        await sleep(10)
        await bot.send(event,"async task over")'''
    @bot.on(GroupMessageEvent)
    async def aiReply(event):
        #print(event.processed_message)
        #print(event.message_id,type(event.message_id))
        if event.raw_message=="退出":
            await end_chat(event.user_id)
            await bot.send(event,"那就先不聊啦~")
        elif event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            await bot.send(event,"历史记录已清除",True)
        elif event.raw_message=="/clearall" and event.user_id == config.basic_config["master"]["id"]:
            await clear_all_history()
            await bot.send(event, "已清理所有用户的对话记录")
        elif event.get("at") and event.get("at")[0]["qq"]==str(bot.id) or prefix_check(str(event.raw_message),config.api["llm"]["prefix"]):
            bot.logger.info(f"接受消息{event.processed_message}")
            user_info = await get_user(event.user_id, event.sender.nickname)
            if not user_info[6] >= config.controller["core"]["ai_reply_group"]:
                await bot.send(event,"你没有足够的权限使用该功能哦~")
                return
            reply_message=await aiReplyCore(event.processed_message,event.user_id,config,tools=tools,bot=bot,event=event)
            if reply_message is not None:
                if random.randint(0,100)<config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path=await tts(reply_message,config=config)
                        await bot.send(event,Record(file=path))
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])

                else:
                    await bot.send(event,reply_message,config.api["llm"]["Quote"])
        else:
            reply_message = await judge_trigger(event.processed_message, event.user_id, config, tools=tools, bot=bot,event=event)
            if reply_message is not None:
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path = await tts(reply_message, config=config)
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
                bot.logger.info(f"消息{message}匹配到前缀{p}")
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
          reply_message = await aiReplyCore(event.processed_message, event.user_id, config, tools=tools, bot=bot,
                                            event=event)
          if reply_message is not None:
              if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                  if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])
                  try:
                      bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                      path = await tts(reply_message, config=config)
                      await bot.send(event, Record(file=path))
                  except Exception as e:
                      bot.logger.error(f"Error occurred when calling tts: {e}")
                  if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])

              else:
                  await bot.send(event, reply_message, config.api["llm"]["Quote"])
