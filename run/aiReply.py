import time
from collections import defaultdict

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Reply
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.llmDB import delete_user_history
from plugins.core.aiReply_utils import prompt_elements_construct
from plugins.func_map import func_map



def main(bot,config):
    last_trigger_time = defaultdict(float) #持续注意用户发言
    @bot.on(GroupMessageEvent)
    async def aiReply(event):

        #print(event.processed_message)
        #print(event.message_id,type(event.message_id))

        trigger=False
        if event.user_id in last_trigger_time:
            if (time.time() - last_trigger_time.get(event.user_id)) <= config.api["llm"]["focus_time"]:
                trigger=True
            else:
                last_trigger_time.pop(event.user_id)
                trigger=False

        if event.raw_message=="退出" and event.user_id in last_trigger_time:
            last_trigger_time.pop(event.user_id)
        elif event.get("at") and event.get("at")[0]["qq"]==str(bot.id) or trigger:
            bot.logger.info(f"接受消息{event.processed_message}")
            r=await aiReplyCore(event.processed_message,event.user_id,config)
            await bot.send(event,r,config.api["llm"]["Quote"])
            last_trigger_time[event.user_id] = time.time()
        elif event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            await bot.send(event,"历史记录已清除",True)
