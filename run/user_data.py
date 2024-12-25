from developTools.event.events import GroupMessageEvent
from plugins.core.userDB import add_user


def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def handle_group_message(event):
        if event.raw_message == "注册":
            data=await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            r=await add_user(
                data["data"]["user_id"],
                data["data"]["nickname"],
                data["data"]["card"],
                data["data"]["sex"],
                data["data"]["age"],
                data["data"]["area"])
            await bot.send(event, r)