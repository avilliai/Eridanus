# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
import inspect
import re
import threading
import time
from asyncio import sleep

import httpx
import yaml
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Image, Reply, Text

from plugins.FragmentsCore import querys
from plugins.SignPicMaker import signPicMaker
from plugins.dataBase import user_exists, add_user, get_user_info, update_last_sign_in
from plugins.messageDataBase import user_exists_TextDataBase, add_text_TextDataBase
from plugins.toolkits import wash_cqCode, fileUrl


def main(bot, bus, logger):
    global operate_list
    operate_list=[]
    @bus.on(GroupMessageEvent)
    async def handle_userSign(event: GroupMessageEvent):
        global operate_list
        if wash_cqCode(event.raw_message)=="签到" or event.sender.user_id in operate_list:
            if user_exists(event.sender.user_id):
                user_info = get_user_info(event.sender.user_id)
                if datetime.strptime(user_info[7], '%Y-%m-%d %H:%M:%S').date() ==datetime.now().date() and event.sender.user_id!=bot.basicConfig["master"]:
                    await bot.send_group_message(event.group_id, [Text("您今天已经签到过了，请明天再来吧！"), Reply(str(event.message_id))])
                    return
            else:
                if event.sender.user_id not in operate_list:
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Text("请发送您所在的的城市名，以便于bot向您提供天气服务。")])
                    operate_list.append(event.sender.user_id)
                    return
                else:
                    city=wash_cqCode(event.raw_message)
                    add_user(event.sender.user_id, event.sender.nickname, event.sender.sex,city)
                    operate_list.remove(event.sender.user_id)
            user_info = get_user_info(event.sender.user_id)
            user_id = user_info[0]
            nickname = user_info[1]
            sex = user_info[2]
            sign_in_days = user_info[3]
            added_date = user_info[4]
            city = user_info[5]
            await bot.send_group_message(event.group_id,[Text("正在查询天气..."),Reply(str(event.message_id))])
            weather=await querys(city,bot.api["心知天气"])
            p=await signPicMaker(user_id, weather, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), sign_in_days, added_date)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(p),type='flash',url=""), Reply(str(event.message_id))])
            update_last_sign_in(event.sender.user_id) #更新签到时间
        #await signPicMaker()
        logger.info(f"发送者：{event.sender.nickname}({event.sender.user_id})")
        logger.info(event.sender)
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
        #logger.info(f"发送者：{event.sender.nickname}({event.sender.user_id})")
        #logger.info(event.sender)