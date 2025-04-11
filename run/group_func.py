import os
import re
from developTools.event.events import GroupMessageEvent
from plugins.core.Group_Message_DB import add_to_group
from developTools.message.message_components import Image, Text, Node
from plugins.random_pic.random_anime import delete_files, get_random_dongfangproject,get_random_pic_1, get_vv_pic,get_wap,get_random_cat,get_deskphoto,get_request,functions,get_text_number,doro,chaijun
from plugins.basic_plugin.get_sentence import get_en,get_common,get_news

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def add_message_to_db(event: GroupMessageEvent):
        if not config.api["llm"]["读取群聊上下文"]:
            return
        try:
            user_name=event.sender.nickname
        except:
            user_name=event.user_id
        try:
            message={"user_name":user_name,"user_id":event.user_id,"message":event.processed_message}
            await add_to_group(event.group_id,message)
        except Exception as e:
            bot.logger.error(f"group_mes database error {e}")

    @bot.on(GroupMessageEvent)
    async def send_pics(event: GroupMessageEvent):
        if event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("柴郡"):
            bot.logger.info("找一张柴郡表情包!")
            path=await chaijun()
            await bot.send(event,Image(file=path))
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("doro"):
            bot.logger.info("找一张doro表情包!")
            await bot.send(event,Image(file=await doro()))
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("二次元"):
            numbers  = await get_text_number(bot,config,event)
            bot.logger.info("找组随机二次元!")
            await get_request(bot,config,event,get_random_pic_1,numbers)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("东方"):
            numbers  = await get_text_number(bot,config,event)
            bot.logger.info("找组东方!")
            await get_request(bot,config,event,get_random_dongfangproject,numbers)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("涩图"):
            numbers  = await get_text_number(bot,config,event)
            bot.logger.info("找组涩图!")
            await get_request(bot,config,event,get_wap,numbers)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("猫猫"):
            numbers  = await get_text_number(bot,config,event)
            bot.logger.info("找组猫猫!")
            await get_request(bot,config,event,get_random_cat,numbers)
        '''elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("壁纸"):
            bot.logger.info("找组壁纸!")
            r = await get_deskphoto(functions())
            await bot.send(event,Node(content=r))'''
    
    @bot.on(GroupMessageEvent)
    async def send_text(event: GroupMessageEvent):
        if event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("英语") or event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith("荔枝"):
            bot.logger.info("找英语!")
            sentence = await get_en('https://api.vvhan.com/api/dailyEnglish?type=sj','en','zh')
            await bot.send(event,sentence)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('名句'):
            bot.logger.info("找名句!")
            sentence = await get_common('https://api.suyanw.cn/api/djt3.php')
            await bot.send(event,sentence)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('新闻'):
            bot.logger.info("新闻!")
            await get_news('https://api.suyanw.cn/api/60SReadWorld.php')
            await bot.send(event,Image(file='djt.png'))
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('KFC') or event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('疯狂星期四') or event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('kfc'):
            bot.logger.info("找KFC!")
            sentence = await get_common('https://api.suyanw.cn/api/kfcyl.php')
            await bot.send(event,sentence)
        elif event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('绕口令'):
            bot.logger.info("找绕口令!")
            sentence = await get_en('https://api.suyanw.cn/api/rao.php','title','Msg')
            await bot.send(event,sentence)

    @bot.on(GroupMessageEvent)
    async def get_vv(event: GroupMessageEvent):
        if event.message_chain.has(Text) and event.message_chain.get(Text)[0].text.startswith('vv'):
            bot.logger.info("找组vv!")
            if type(event.message_chain.get(Text)[0].text.split()[1])==str:
                keys = event.message_chain.get(Text)[0].text.split()[1]
            else:
                keys = '测试'
            if re.findall(r'\d+', event.pure_text):
                numbers = int(re.findall(r'\d+', event.pure_text)[0])
            else:
                numbers = 1
            path = get_vv_pic(keys,numbers)
            if numbers == 1:
                await bot.send(event,Image(file=f'{path}/{os.listdir(path)[0]}'))
                delete_files(path)
                return
            lst = []
            pics = os.listdir(path)
            for pic in pics:
                img = Image(file=f'{path}/{pic}')
                lst.append(img)
            await bot.send(event,Node(content=lst))
            delete_files(path)
    
