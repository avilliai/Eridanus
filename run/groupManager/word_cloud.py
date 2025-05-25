from developTools.event.events import GroupMessageEvent
from framework_common.database_util.Group import add_to_group


def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def add_message_to_db(event: GroupMessageEvent):
        if not config.ai_llm.config["llm"]["读取群聊上下文"]:
            return
        try:
            user_name=event.sender.nickname
        except:
            user_name=event.user_id
        try:
            message={"user_name":user_name,"user_id":event.user_id,"message":event.processed_message}
            await add_to_group(event.group_id,message)
        except Exception as e:
            bot.logger.error(f"group_mes database error {e}")
            
