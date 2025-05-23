import random
import traceback

import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Record, Node, Text, Image, Music
from run.basic_plugin.service.anime_setu import anime_setu, anime_setu1
from run.basic_plugin.service.cloudMusic import cccdddm
from run.basic_plugin.service.divination import tarotChoice

from run.basic_plugin.service.weather_query import weather_query


from framework_common.database_util.User import get_user


from framework_common.utils.utils import download_img
from framework_common.utils.random_str import random_str





"""
供func call调用
"""
async def call_quit_chat(bot,event,config):
    return False
async def call_weather_query(bot,event,config,location=None):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if location is None:
        location = user_info.city
    r=await weather_query(config.common_config.basic_config["proxy"]["http_proxy"],config.basic_plugin.config["心知天气"]["api_key"],location)
    return  {"result": r}
async def call_setu(bot,event,config,tags,num=3):
    user_info = await get_user(event.user_id, event.sender.nickname)

    if user_info.permission >= config.basic_plugin.config["setu"]["setu_operate_level"]:
        try:
            r=await anime_setu(tags,num,config.basic_plugin.config["setu"]["r18mode"])
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
                    if config.basic_plugin.config["setu"]["download"]:
                        p=await download_img(url,path,config.basic_plugin.config["setu"]["gray_layer"],proxy=config.common_config.basic_config["proxy"]["http_proxy"])
                    else:
                        p=url
                    r = Node(content=[Text(f"link：{page}\n作者：{author}\nUID：{author_uid}\n标签：{tags}\n"),Image(file=p)])
                    fordMes.append(r)
                except Exception as e:
                    bot.logger.error(f"Error downloading: {e}")
                    continue
        except Exception as e:
            bot.logger.error(f"Error in setu: {e}")
            fordMes=[]
        if not fordMes:
            bot.logger.warning("No setu found.Change resource")
            r=await anime_setu1(tags,num,config.basic_plugin.config["setu"]["r18mode"])
            for i in r:
                try:
                    url=i["urls"]["regular"]
                    title=i["title"]
                    author=i["author"]
                    tags=i["tags"]
                    path = f"data/pictures/cache/{random_str()}.png"
                    bot.logger.info(f"Downloading {url} to {path}")
                    if config.basic_plugin.config["setu"]["download"]:
                        p = await download_img(url, path, config.basic_plugin.config["setu"]["gray_layer"],proxy=config.common_config.basic_config["proxy"]["http_proxy"])
                    else:
                        p=url
                    r = Node(content=[Text(f"标题：{title}\n作者：{author}\n标签：{tags}\nurl：{url}"), Image(file=p)])
                    fordMes.append(r)
                except Exception as e:

                    traceback.print_exc()
                    bot.logger.error(f"Error downloading: {e}")
                    try:
                        fordMes.append(Node(content=[Text(f"标题：{title}\n作者：{author}\n标签：{tags}\nurl：{url}")]))
                    except:
                        pass
        if not fordMes:
            await bot.send(event, "没有找到符合条件的涩图/或下载失败，换个标签试试吧")
            return
        await bot.send(event, fordMes)
    else:
        await bot.send(event, "权限不够呢.....")




async def call_tarot(bot,event,config):
    if config.basic_plugin.config["tarot"]["彩蛋牌"] and random.randint(1, 100) < \
            config.basic_plugin.config["tarot"]["彩蛋牌"]["probability"]:
        cards_ = config.basic_plugin.config["tarot"]["彩蛋牌"]["card_index"]
        card = random.choice(cards_)
        card_path, text = list(card.items())[0]
        if text=="": text="no description"
        await bot.send(event, [Text(f"{text}"), Image(file=card_path)])
        return {"text": "开出彩蛋牌，来源：jojo的奇妙冒险", "img": card_path}
    txt, img = tarotChoice(config.basic_plugin.config["tarot"]["mode"])
    await bot.send(event,[Text(txt),Image(file=img)])
    return {"text": txt,"img":img}
async def call_fortune(bot,event,config):
    r=random.randint(1,100)
    if r<=10:
        card_="data/pictures/Amamiya/谕吉.jpg"
    elif 10<r<=30:
        card_="data/pictures/Amamiya/大吉.jpg"
    elif 30<r<=60:
        card_="data/pictures/Amamiya/中吉.jpg"
    elif 60<r<=90:
        card_="data/pictures/Amamiya/小吉.jpg"
    else:
        card_="data/pictures/Amamiya/凶.jpg"
    await bot.send(event, [Text(f"{event.sender.nickname}今天的运势是："), Image(file=card_)])
async def call_pick_music(bot,event,config,aim):
    try:
        r=await cccdddm(aim)
        #print(r)
        await bot.send(event, Music(type="163", id=r[0][1]))
    except Exception as e:
        bot.logger.error(f"Error in pick_music: {e}")
        await bot.send(event, "出错了，再试一次看看？")
def main(bot,config):
    global avatar
    avatar=False
    @bot.on(GroupMessageEvent)
    async def weather_query(event: GroupMessageEvent):
        if event.pure_text.startswith("查天气"):
            #await bot.send(event, "已修改")
            remark = event.pure_text.split("查天气")[1].strip()
            r=await call_weather_query(bot,event,config,remark)
            await bot.send(event,str(r.get("result")))
            #await bot.set_friend_remark(event.user_id, remark)
    @bot.on(GroupMessageEvent)
    async def weather(event: GroupMessageEvent):
        if event.pure_text.startswith("/setu"):
            tags=event.pure_text.replace("/setu","").split(" ")
            try:
                await call_setu(bot,event,config,tags[2:],int(tags[1]))
            except Exception as e:
                bot.logger.error(f"Error in setu: {e}")
                await bot.send(event, "出错，格式请按照\n/setu 数量 标签 标签")




    @bot.on(GroupMessageEvent)
    async def cyber_divination(event: GroupMessageEvent):
        if event.pure_text=="今日塔罗":
            if config.basic_plugin.config["tarot"]["彩蛋牌"] and random.randint(1,100)<config.basic_plugin.config["tarot"]["彩蛋牌"]["probability"]:
                cards_=config.basic_plugin.config["tarot"]["彩蛋牌"]["card_index"]
                card=random.choice(cards_)
                card_path, text = list(card.items())[0]
                if text=="": text="no description"
                await bot.send(event, [Text(f"{text}"), Image(file=card_path)])
                return

            txt, img = tarotChoice(config.basic_plugin.config["tarot"]["mode"])
            await bot.send(event, [Text(txt), Image(file=img)]) #似乎没必要让这个也走ai回复调用
        elif event.pure_text=="抽象塔罗":
            txt, img = tarotChoice('AbstractImages')
            await bot.send(event, [Text(txt), Image(file=img)]) #似乎没必要让这个也走ai回复调用
        elif event.pure_text=="ba塔罗":
            txt, img = tarotChoice('blueArchive')
            await bot.send(event, [Text(txt), Image(file=img)]) #似乎没必要让这个也走ai回复调用
        elif event.pure_text=="bili塔罗" or event.pure_text=="2233塔罗":
            txt, img = tarotChoice('bilibili')
            await bot.send(event, [Text(txt), Image(file=img)]) #似乎没必要让这个也走ai回复调用
        elif event.pure_text=="运势":
            await call_fortune(bot,event,config)
            
    @bot.on(GroupMessageEvent)
    async def pick_music(event: GroupMessageEvent):
        if event.pure_text.startswith("点歌 "):
            song_name = event.pure_text.split("点歌 ")[1]
            await call_pick_music(bot, event, config, song_name)





