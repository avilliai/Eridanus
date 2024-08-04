from pathlib import Path
from time import sleep
from pydantic import Field
from yiriob.event.events import GroupMessageEvent, PrivateMessageEvent
from yiriob.interface import SendGroupMessageInterface, SendGroupMessageParams, SendPrivateMessageInterface, \
    SendPrivateMessageParams
from yiriob.message import MessageChain, Text, At, Reply, Image, Record

from plugins.tookits import check_cq_atcode


def main(bot,bus,logger):
    logger.info("example启动")

    @bus.on(GroupMessageEvent)
    async def on_group_message(event: GroupMessageEvent) -> None:
        if event.sender.user_id!=1840094972:
            return
        logger.info(event)
        logger.info(event.message)
        logger.info(event.raw_message)
        print(check_cq_atcode(event.raw_message,bot.id)) #此函数用于检查是否包含at bot
        if event.raw_message=="你好":
            logger.info("ok")
            #几个参数分别是，艾特，文本，引用回复
            await bot.send_group_message(event.group_id,[At(str(event.sender.user_id)),Text("你好"),Reply(str(event.message_id))])
            #发送语音，说实话，我也没搞懂他是怎么用的，等有时间再说。
            #await bot.send_group_message(event.group_id,[Record(type="record",file=str(Path("./plugins/output.wav")))])
            #下面是发送图片，我暂时没弄明白
            #await bot.send_group_message(event.group_id,[Image(file="plugins/NB2uR.png")])
            #下面是原调用方式，我们不用这个
            '''await bot.adapter.call_api(
                SendGroupMessageInterface,
                SendGroupMessageParams(
                    group_id=event.group_id, message=MessageChain([At(str(event.sender.user_id)),Text("Hello World!")])
                ),
            )'''

    @bus.on(PrivateMessageEvent)
    async def on_private_message(event: GroupMessageEvent) -> None:
        await bot.adapter.call_api(
            SendPrivateMessageInterface,
            SendPrivateMessageParams(
                user_id=event.user_id, message=MessageChain([Text("Hello World!")])
            ),
        )