import os
import shutil

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Record, Node, Text, Image
from plugins.basic_plugin.anime_setu import anime_setu
from plugins.basic_plugin.weather_query import weather_query
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import get_user
from plugins.core.utils import download_img
from plugins.utils.utils import random_str

"""
供func call调用
"""
async def call_weather_query(bot,event,config,location):
    r=await weather_query(config.api["proxy"]["http_proxy"],config.api["心知天气"]["api_key"],location)
    r = await aiReplyCore([{"text":f"请你为我播报接下来几天的天气{r}"}], event.user_id, config)
    await bot.send(event, str(r))
async def call_setu(bot,event,config,tags,num=3):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] > config.controller["basic_plugin"]["setu_operate_level"]:
        r=await anime_setu(tags,num,config.settings["basic_plugin"]["setu"]["r18mode"])
        fordMes=[]
        for i in r:
            try:
                url=i["url"].replace("i.pximg.net","i.pixiv.re")
                page=i["page"]
                author=i["author"]
                author_uid=i["author_uid"]
                tags=i["tags"]
                path=f"data/pictures/cache/{random_str()}.png"
                bot.logger.info(f"Downloading {url} to {path}")
                p=await download_img(url,path,config.settings["basic_plugin"]["setu"]["gray_layer"])
                r = Node(content=[Text(f"link：{page}\n作者：{author}\nUID：{author_uid}\n标签：{tags}\n"),Image(file=p)])
                fordMes.append(r)
            except Exception as e:
                bot.logger.error(f"Error downloading: {e}")
                continue
        await bot.send_group_forward_msg(event.group_id, fordMes)
        for i in fordMes:
            path=i.content[1].file
            os.remove(path.replace("file://",""))
            bot.logger.info(f"Deleted {path}")
    else:
        await bot.send(event, "权限不够呢.....")

def main(bot,config):
    global avatar
    avatar=False
    @bot.on(GroupMessageEvent)
    async def sendLike(event: GroupMessageEvent):
        if event.raw_message.startswith("查天气"):
            #await bot.send(event, "已修改")
            remark = event.raw_message.split("查天气")[1].strip()
            await bot.set_friend_remark(event.user_id, remark)
    @bot.on(GroupMessageEvent)
    async def weather(event: GroupMessageEvent):
        if event.raw_message.startswith("/setu"):
            tags=event.raw_message.replace("/setu","").split(" ")
            try:
                await call_setu(bot,event,config,tags[2:],int(tags[1]))
            except Exception as e:
                bot.logger.error(f"Error in setu: {e}")
                await bot.send(event, "出错，格式请按照\n/setu 数量 标签 标签")
