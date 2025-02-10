from developTools.event.events import GroupMessageEvent
from plugins.core.Group_Message_DB import add_to_group


def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def add_message_to_db(event: GroupMessageEvent):
        try:
            user_name=event.sender.nickname
        except:
            user_name=event.user_id
        message={"user_name":user_name,"user_id":event.user_id,"message":event.processed_message}
        await add_to_group(event.group_id,message)