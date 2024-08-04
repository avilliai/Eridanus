from yiriob.event.events import GroupMessageEvent, PrivateMessageEvent
from yiriob.interface import SendGroupMessageInterface, SendGroupMessageParams, SendPrivateMessageInterface, \
    SendPrivateMessageParams
from yiriob.message import MessageChain, Text


def main(bot,bus,logger):
    logger.info("example启动")
    @bus.on(GroupMessageEvent)
    async def on_group_message(event: GroupMessageEvent) -> None:
        logger.info(event)
        if event.raw_message=="你好":
            logger.info("ok")
            await bot.adapter.call_api(
                SendGroupMessageInterface,
                SendGroupMessageParams(
                    group_id=event.group_id, message=MessageChain([Text("Hello World!")])
                ),
            )

    @bus.on(PrivateMessageEvent)
    async def on_private_message(event: GroupMessageEvent) -> None:
        await bot.adapter.call_api(
            SendPrivateMessageInterface,
            SendPrivateMessageParams(
                user_id=event.user_id, message=MessageChain([Text("Hello World!")])
            ),
        )