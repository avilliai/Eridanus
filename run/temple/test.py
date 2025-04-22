from developTools.event.events import GroupMessageEvent
from framework_common.database_util.User import get_user, User


def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def on_group_message(event: GroupMessageEvent):
        if event.sender.user_id ==config.basic_config["master"]["id"]:
            user: User=await get_user(event.sender.user_id)
            print(user)