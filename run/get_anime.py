from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image, Text, Node, File
from plugins.chaijun.chaijun import chaijun
from plugins.doro_anime.doro import doro
from plugins.random_pic.random_anime import get_random,get_all_pic,get_random_dongfangproject,get_random_pic_1,get_random_pic_2,get_random_json,get_random_meng,get_sex,get_wap,get_web
import asyncio
import random
import time 
import re

async def get_request(bot,config,event,func,num):
    functions = [func(i) for i in range(1,num+1)]
    try:
        r = await asyncio.gather(*functions)
        await bot.send(event,Node(content=r))
    except Exception as e:
        bot.logger.error(f"Error in get_anime: {e}")

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def get_anime(event: GroupMessageEvent):
        if event.pure_text=="柴郡":
            bot.logger.info("找一张柴郡表情包!")
            path=await chaijun()
            await bot.send(event,Image(file=path))
        elif event.pure_text=="doro":
            bot.logger.info("找一张doro表情包!")
            await bot.send(event,Image(file=await doro()))
        elif event.message_chain.get(Text)[0].text.startswith("二次元") or event.message_chain.get(Text)[0].text.startswith("动漫"):
            if re.findall(r'\d+', event.pure_text):
                numbers = int(re.findall(r'\d+', event.pure_text)[0])
            else:
                numbers = 3
            bot.logger.info("找组随机二次元!")
            await get_request(bot,config,event,get_random_pic_1,numbers)
        elif event.message_chain.get(Text)[0].text.startswith("东方"):
            if re.findall(r'\d+', event.pure_text):
                numbers = int(re.findall(r'\d+', event.pure_text)[0])
            else:
                numbers = 3
            bot.logger.info("找组东方!")
            await get_request(bot,config,event,get_random_dongfangproject,numbers)
        elif event.message_chain.get(Text)[0].text.startswith("涩图") or event.message_chain.get(Text)[0].text.startswith("来张涩图"):
            if re.findall(r'\d+', event.pure_text):
                numbers = int(re.findall(r'\d+', event.pure_text)[0])
            else:
                numbers = 3
            bot.logger.info("找组涩图!")
            await get_request(bot,config,event,get_sex,numbers)