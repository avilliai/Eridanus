# -*- coding:utf-8 -*-

from yiriob.event.events import GroupMessageEvent, PrivateMessageEvent
from yiriob.interface import SendGroupMessageInterface, SendGroupMessageParams, SendPrivateMessageInterface, \
    SendPrivateMessageParams
from yiriob.message import MessageChain, Text, At, Reply, Record, Image

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
        print(check_cq_atcode(event.raw_message,bot.id)) #此函数用于检查是否包含at bot,有艾特则去除CQ码并返回文本(可能为空文本)
        if event.raw_message=="测试":
            logger.info("ok")
            #几个参数分别是，艾特，文本，引用回复
            await bot.send_group_message(event.group_id,[At(str(event.sender.user_id)),Text("你好"),Reply(str(event.message_id))])
            #发送图片(目前file参数似乎只能用url)
            await bot.send_group_message(event.group_id,[Image(file="https://api.lolimi.cn/API/dmtx/api.php",type='flash',url="")])
            #发送语音(目前file参数似乎只能用url)
            await bot.send_group_message(event.group_id,[Record(file="https://s5k.cn/api/v1/studio/gally16/Bert-VITS21.x/gradio/file=/tmp/gradio/477121418d2334350e6cdc8cbf57094ab6801712/audio.wav",url="")])
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
