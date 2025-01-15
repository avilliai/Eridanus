from developTools.event.events import GroupDecreaseNoticeEvent


def main(bot,config):

    @bot.on(GroupDecreaseNoticeEvent)
    async def group_decrease(event: GroupDecreaseNoticeEvent):
        if event.user_id != event.self_id:
            await bot.send_group_message(event.group_id, f"{event.user_id} 悄悄离开了")