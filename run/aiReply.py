from developTools.event.events import GroupMessageEvent
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.llmDB import delete_user_history
from plugins.core.utils import prompt_elements_construct
from plugins.func_map import func_map



def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def aiReply(event):

        #print(event.processed_message)
        #print(event.get("image"))
        if event.get("at") and event.get("at")[0]["qq"]==str(bot.id):
            #print(f"接受艾特消息{event.processed_message}")
            #bot.logger.info(f"{event.get('at')[0]}")
            bot.logger.info(f"接受艾特消息{event.processed_message}")

            #print(ask)
            r=await aiReplyCore(event.processed_message,event.user_id,config)
            await bot.send(event,r["content"])
        if event.raw_message=="/clear":
            await delete_user_history(event.user_id)
            await bot.send(event,"历史记录已清除")