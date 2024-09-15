# -*- coding:utf-8 -*-
import os
import random
from pathlib import Path

from yiriob.event.events import GroupMessageEvent, PrivateMessageEvent
from yiriob.interface import SendGroupMessageInterface, SendGroupMessageParams, SendPrivateMessageInterface, \
    SendPrivateMessageParams
from yiriob.message import MessageChain, Text, At, Reply, Record, Image, Node, Forward

from plugins.tookits import check_cq_atcode, wash_cqCode, fileUrl


def main(bot,bus,logger):
    logger.info("example启动")

    @bus.on(GroupMessageEvent)
    async def tarotToday(event: GroupMessageEvent):
        if ("彩色小人" in wash_cqCode(event.raw_message) and check_cq_atcode(event.raw_message,
                                                                             bot.id) != False) or str(
                wash_cqCode(event.raw_message)) == "彩色小人":
            logger.info("彩色小人，启动！")
            colorfulCharacterList = os.listdir("data/pictures/colorfulAnimeCharacter")
            c = random.choice(colorfulCharacterList)
            p=f"{os.getcwd()}/data/pictures/colorfulAnimeCharacter/{c}"
            print(p)
            image_path = Path(p)
            file_url = image_path.as_uri()

            print(file_url)
            print(fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}"))
            file_url=fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}")
            await bot.send_group_message(event.group_id,[Image(file=fileUrl(f"data/pictures/colorfulAnimeCharacter/{c}"), type='flash', url=""),Reply(str(event.message_id))])

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
            #await bot.send_group_message(event.group_id,[At(str(event.sender.user_id)),Text("你好"),Reply(str(event.message_id))])
            node=[Node(id=str(event.message_id),user_id=str(bot.id),nickname="bot",content=MessageChain([Text("你好")]))]
            await bot.send_group_message(event.group_id,Forward(id=str(event.message_id)))
            #发送本地图片
            image_path = Path(f"{os.getcwd()}/plugins/NB2uR.png")
            file_url = image_path.as_uri()
            #await bot.send_group_message(event.group_id,[Image(file=file_url,type='flash',url="")])
            #发送网络图片
            #await bot.send_group_message(event.group_id, [Image(file="https_url", type='flash', url="")])
            '''

            #发送本地语音
            image_path = Path(f"{os.getcwd()}/plugins/output.wav")
            file_url = image_path.as_uri()
            await bot.send_group_message(event.group_id, [Record(file=file_url,url="")])
            #发送网络语音
            #await bot.send_group_message(event.group_id,[Record(file="https_url",url="")])'''

    @bus.on(PrivateMessageEvent)
    async def on_private_message(event: GroupMessageEvent) -> None:
        await bot.adapter.call_api(
            SendPrivateMessageInterface,
            SendPrivateMessageParams(
                user_id=event.user_id, message=MessageChain([Text("Hello World!")])
            ),
        )
