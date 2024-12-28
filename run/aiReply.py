import os
import random
import time
from asyncio import sleep
from collections import defaultdict

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Reply, Record
from plugins.core.aiReplyCore import aiReplyCore, end_chat, judge_trigger
from plugins.core.llmDB import delete_user_history
from plugins.core.aiReply_utils import prompt_elements_construct
from plugins.core.tts import tts
from plugins.func_map_loader import func_map, gemini_func_map




def main(bot,config):
      # 持续注意用户发言
    if config.api["llm"]["func_calling"]:
        if config.api["llm"]["model"] == "gemini":
            tools = gemini_func_map()
        else:
            tools = func_map()
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
        elif event.get("at") and event.get("at")[0]["qq"]==str(bot.id) or prefix_check(str(event.raw_message),config.api["llm"]["prefix"]):
            bot.logger.info(f"接受消息{event.processed_message}")

            reply_message=await aiReplyCore(event.processed_message,event.user_id,config,tools=tools,bot=bot,event=event)
            if reply_message:
                if random.randint(0,100)<config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path=await tts(reply_message,config=config)
                        await bot.send(event,Record(file=path))
                        os.remove(path) # 删除临时文件
                    except Exception as e:
                        bot.logger.error(f"Error occurred when calling tts: {e}")
                    if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])

                else:
                    await bot.send(event,reply_message,config.api["llm"]["Quote"])

        elif event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            await bot.send(event,"历史记录已清除",True)
        else:
            reply_message = await judge_trigger(event.processed_message, event.user_id, config, tools=tools, bot=bot,
                                              event=event)
            if reply_message:
                if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                    if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                        await bot.send(event, reply_message, config.api["llm"]["Quote"])
                    try:
                        bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                        path = await tts(reply_message, config=config)
                        await bot.send(event, Record(file=path))
                        os.remove(path)  # 删除临时文件
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
      else:
          bot.logger.info(f"私聊接受消息{event.processed_message}")

          reply_message = await aiReplyCore(event.processed_message, event.user_id, config, tools=tools, bot=bot,
                                            event=event)
          if reply_message:
              if random.randint(0, 100) < config.api["llm"]["语音回复几率"]:
                  if config.api["llm"]["语音回复附带文本"] and not config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])
                  try:
                      bot.logger.info(f"调用语音合成 任务文本：{reply_message}")
                      path = await tts(reply_message, config=config)
                      await bot.send(event, Record(file=path))
                      os.remove(path)  # 删除临时文件
                  except Exception as e:
                      bot.logger.error(f"Error occurred when calling tts: {e}")
                  if config.api["llm"]["语音回复附带文本"] and config.api["llm"]["文本语音同时发送"]:
                      await bot.send(event, reply_message, config.api["llm"]["Quote"])

              else:
                  await bot.send(event, reply_message, config.api["llm"]["Quote"])
