# -*- coding: utf-8 -*-
import asyncio
import inspect
import re
import threading
import time
from asyncio import sleep

import httpx
import yaml
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Image, Reply, Text

from plugins.dataBase import user_exists, add_user
from plugins.messageDataBase import user_exists_TextDataBase, add_text_TextDataBase
from plugins.tookits import wash_cqCode


def main(bot, bus, logger):
    @bus.on(GroupMessageEvent)
    async def handle_command(event: GroupMessageEvent):
        #文本数据库
        if user_exists_TextDataBase(event.sender.user_id):
            add_text_TextDataBase(event.sender.user_id, wash_cqCode(event.raw_message))
        else:
            add_text_TextDataBase(event.sender.user_id, wash_cqCode(event.raw_message))
        #用户数据库
        #if not user_exists(event.sender.user_id):
            #add_user(event.sender.user_id, event.sender.nickname,event.sender.sex,city="通辽")
        logger.info(f"发送者：{event.sender.nickname}({event.sender.user_id})")
        logger.info(event.sender)