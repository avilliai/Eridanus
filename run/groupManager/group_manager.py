from developTools.event.events import GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent
from plugins.core.aiReplyCore_without_funcCall import aiReplyCore_shadow


def main(bot,config):

    @bot.on(GroupDecreaseNoticeEvent)
    async def group_decrease(event: GroupDecreaseNoticeEvent):
        if event.user_id != event.self_id:
            await bot.send_group_message(event.group_id, f"{event.user_id} 悄悄离开了")

    @bot.on(GroupIncreaseNoticeEvent)
    async def GroupIncreaseNoticeHandler(event: GroupIncreaseNoticeEvent):
        if event.user_id!=event.self_id:
            if config.api["llm"]["aiReplyCore"]:
                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                name = data["data"]["nickname"]
                r = await aiReplyCore_shadow([{"text": f"{name}加入了群聊，为他发送入群欢迎语"}], event.group_id, config,
                                             func_result=True)
                await bot.send(event, str(r))
            else:
                await bot.send(event, f"欢迎新群员{event.user_id}加入群聊")