import os

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Node, Text, File, Music
from plugins.core.userDB import get_user
from plugins.resource_search_plugin.asmr.asmr import ASMR_random, get_img, get_audio
from plugins.resource_search_plugin.zLibrary.zLib import search_book, download_book
from plugins.resource_search_plugin.zLibrary.zLibrary import Zlibrary

global Z
async def search_book_info(bot,event,config,info):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.controller["resource_search"]["z_library"]["search_operate_level"]:

        await bot.send(event, "正在搜索中，请稍候...")
        result = search_book(Z, info, config.api["z_library"]["search_num"])
        forward_list = []
        for r in result:
            forward_list.append(Node(content=[Text(r[0]), Image(file=r[1])]))
        await bot.send(event, forward_list)
        # await bot.send(event,Image(file=p)])
        # print(r)
    else:
        await bot.send(event, "你没有权限使用该功能")
async def call_asmr(bot,event,config,try_again=False):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.controller["resource_search"]["asmr"]["asmr_level"]:
        try:
            athor, title, video_id, length = await ASMR_random()
            imgurl =await get_img(video_id)
            audiopath =await get_audio(video_id)
            bot.logger.info(f"asmr\n标题:{title}\n频道:{athor}\n视频id:{video_id}\n视频时长:{length}\n视频封面:{imgurl}\n音频:{audiopath}")
            await bot.send(event, [Text(f"随机奥术\n频道: {athor}\n标题: {title}\n时长: {length}"), Image(file=imgurl)])
            await bot.send(event,File(file=audiopath))
        except Exception as e:
            bot.logger.error(f"asmr error:{e}")
            if try_again==False:
                bot.logger.warning("asmr try again!")
                await call_asmr(bot,event,config,try_again=True)
            if try_again==True:
                await bot.send(event, "失败了！要不再试一次？")
    else:
        await bot.send(event, "你没有权限使用该功能")


def main(bot,config):
    #实例化对象，进行进一步操作
    if config.api["z_library"]["email"]!="" and config.api["z_library"]["password"]!="":
        global Z
        Z = Zlibrary(email=config.api["z_library"]["email"], password=config.api["z_library"]["password"])
    @bot.on(GroupMessageEvent)
    async def book_resource_search(event):

        if str(event.raw_message).startswith("搜书"):
            book_name = str(event.raw_message).split("搜书")[1]
            await search_book_info(bot,event,config,book_name)

    @bot.on(GroupMessageEvent)
    async def book_resource_download(event):
        if str(event.raw_message).startswith("下载"):
            user_info = await get_user(event.user_id, event.sender.nickname)
            if user_info[6]>=config.controller["resource_search"]["z_library"]["download_operate_level"]:
                book_id = str(event.raw_message).split("下载")[1]
                await bot.send(event, "正在下载中，请稍后...")
                path=download_book(Z,book_id)
                print(path)
            else:
                await bot.send(event, "你没有权限使用该功能")
        elif event.raw_message=="随机奥术" or event.raw_message=="随机asmr" or event.raw_message=="随机奥数":
            await bot.send(event,Music(type="163",id=1916256128))
            #await call_asmr(bot,event,config)

