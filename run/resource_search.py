import os

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text
from plugins.core.userDB import get_user
from plugins.resource_search_plugin.zLibrary.zLib import search_book, download_book
from plugins.resource_search_plugin.zLibrary.zLibrary import Zlibrary


def main(bot,config):
    #实例化对象，进行进一步操作
    Z = Zlibrary(email=config.api["z_library"]["email"], password=config.api["z_library"]["password"])

    @bot.on(GroupMessageEvent)
    async def book_resource_search(event):

        if str(event.raw_message).startswith("搜书"):
            user_info = await get_user(event.user_id, event.sender.nickname)
            if user_info[6]>=config.controller["z_library"]["search_operate_level"]:
                book_name = str(event.raw_message).split("搜书")[1]
                await bot.send(event, "正在搜索中，请稍后...")
                result=search_book(Z,book_name)
                forward_list=[]
                for r in result:
                    forward_list.append(Node(content=[Text(r[0]),Image(file=r[1])]))
                await bot.send_group_forward_msg(event.group_id, forward_list)
                #await bot.send(event,Image(file=p)])
                #print(r)
            else:
                await bot.send(event, "你没有权限使用该功能")
    @bot.on(GroupMessageEvent)
    async def book_resource_download(event):
        if str(event.raw_message).startswith("下载"):
            user_info = await get_user(event.user_id, event.sender.nickname)
            if user_info[6]>=config.controller["z_library"]["download_operate_level"]:
                book_id = str(event.raw_message).split("下载")[1]
                await bot.send(event, "正在下载中，请稍后...")
                path=download_book(Z,book_id)
                print(path)
            else:
                await bot.send(event, "你没有权限使用该功能")

