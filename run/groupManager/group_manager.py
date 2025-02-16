import re

from developTools.event.events import GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, GroupMessageEvent
from developTools.message.message_components import Node, Text
from plugins.core.aiReplyCore import aiReplyCore


def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def group_message(event: GroupMessageEvent):
        if event.get("text"):
            if event.get("text")[0].strip()=="射精" or event.get("text")[0].strip()=="设置精华" or event.get("text")[0].strip()=="设精" or event.get("text")[0].strip()=="精华" or event.get("text")[0].strip()=="设置精华消息":
                if event.get("reply"):
                    await bot.set_essence_msg(int(event.get("reply")[0]["id"]))
                    await bot.send(event, "设置成功")
            elif event.get("text")[0].strip()=="取消精华" or event.get("text")[0].strip()=="取消精华消息" or event.get("text")[0].strip()=="取消设精" or event.get("text")[0].strip()=="取消射精" or event.get("text")[0].strip()=="不射精":
                if event.get("reply"):
                    await bot.delete_essence_msg(int(event.get("reply")[0]["id"]))
                    await bot.send(event, "取消成功")

    @bot.on(GroupDecreaseNoticeEvent)
    async def group_decrease(event: GroupDecreaseNoticeEvent):
        if event.user_id != event.self_id:
            await bot.send_group_message(event.group_id, f"{event.user_id} 悄悄离开了")

    @bot.on(GroupIncreaseNoticeEvent)
    async def GroupIncreaseNoticeHandler(event: GroupIncreaseNoticeEvent):
        if event.user_id!=event.self_id:
            if config.api["llm"]["aiReplyCore"]:
                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                try:
                    name = data["data"]["nickname"]
                except:
                    name = "有新人"
                r = await aiReplyCore([{"text": f"{name}加入了群聊，为他发送入群欢迎语"}], event.group_id, config,bot=bot,
                                             tools=None)
                messages = r.split("<split>")
                for message in messages:
                    if message.strip():
                        await bot.send(event, message.strip())
            else:
                await bot.send(event, f"欢迎新群员{event.user_id}加入群聊")
