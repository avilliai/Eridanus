import os
import random
import re
import traceback

from asyncio import sleep

import asyncio

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Record, Node, Text, Image, Music
from plugins.basic_plugin.anime_setu import anime_setu, anime_setu1
from plugins.basic_plugin.cloudMusic import cccdddm
from plugins.basic_plugin.divination import tarotChoice
from plugins.basic_plugin.image_search import fetch_results, automate_browser
from plugins.basic_plugin.weather_query import weather_query
from plugins.core.tts.modelscopeTTS import get_modelscope_tts_speakers
from plugins.core.tts.napcat_tts import napcat_tts_speakers
from plugins.core.tts.online_vits2 import get_huggingface_online_vits2_speakers
from plugins.core.tts.tts import get_acgn_ai_speaker_list, tts
from plugins.core.tts.vits import get_vits_speakers

from plugins.core.userDB import get_user


from plugins.utils.utils import download_img
from plugins.utils.random_str import random_str



image_search={}

"""
供func call调用
"""
async def call_quit_chat(bot,event,config):
    return False
async def call_weather_query(bot,event,config,location=None):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if location is None:
        location = user_info[5]
    r=await weather_query(config.api["proxy"]["http_proxy"],config.api["心知天气"]["api_key"],location)
    return  {"result": r}
async def call_setu(bot,event,config,tags,num=3):
    user_info = await get_user(event.user_id, event.sender.nickname)

    if user_info[6] >= config.controller["basic_plugin"]["setu_operate_level"]:
        try:
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
        except Exception as e:
            bot.logger.error(f"Error in setu: {e}")
            fordMes=[]
        if fordMes==[]:
            bot.logger.warning("No setu found.Change resource")
            r=await anime_setu1(tags,num,config.settings["basic_plugin"]["setu"]["r18mode"])
            for i in r:
                try:
                    url=i["urls"]["regular"]
                    title=i["title"]
                    author=i["author"]
                    tags=i["tags"]
                    path = f"data/pictures/cache/{random_str()}.png"
                    bot.logger.info(f"Downloading {url} to {path}")
                    p = await download_img(url, path, config.settings["basic_plugin"]["setu"]["gray_layer"])
                    r = Node(content=[Text(f"标题：{title}\n作者：{author}\n标签：{tags}\nurl：{url}"), Image(file=p)])
                    fordMes.append(r)
                except Exception as e:

                    traceback.print_exc()
                    bot.logger.error(f"Error downloading: {e}")
                    try:
                        fordMes.append(Node(content=[Text(f"标题：{title}\n作者：{author}\n标签：{tags}\nurl：{url}")]))
                    except:
                        pass
        if fordMes==[]:
            await bot.send(event, "没有找到符合条件的涩图/或下载失败，换个标签试试吧")
            return
        await bot.send(event, fordMes)
    else:
        await bot.send(event, "权限不够呢.....")
async def call_image_search(bot,event,config,image_url=None):
    user_info = await get_user(event.user_id, event.sender.nickname)
    bot.logger.info("接收来自 用户：" + str(event.sender.user_id) + " 的搜图指令")
    if not config.settings["basic_plugin"]["搜图"]["聚合搜图"] and not config.settings["basic_plugin"]["搜图"]["soutu_bot"]:
        await bot.send(event, "没有开启搜图功能")
        return
    await bot.send(event, "正在搜索图片，请等待结果返回.....")
    if user_info[6] >= config.controller["basic_plugin"]["search_image_resource_operate_level"]:
        if not image_url:
            img_url = event.get("image")[0]["url"]
        else:
            img_url = image_url
        """
        并发调用
        """
        functions = [
            call_image_search1(bot, event, config, img_url),
            call_image_search2(bot, event, config, img_url),
        ]

        for future in asyncio.as_completed(functions):
            try:
                await future
            except Exception as e:
                bot.logger.error(f"Error in image_search: {e}")


    else:
        await bot.send(event, "权限不够呢.....")
async def call_image_search1(bot,event,config,img_url):
    if not config.settings["basic_plugin"]["搜图"]["聚合搜图"]:
        return
    bot.logger.info("调用聚合接口搜索图片")
    results = await fetch_results(config.api["proxy"]["http_proxy"], img_url,
                                  config.api["image_search"]["sauceno_api_key"])
    forMeslist = []
    for name, result in results.items():
        if result and result[0] != "":
            bot.logger.info(f"{name} 成功返回: {result}")
            try:
                path = "data/pictures/cache/" + random_str() + ".png"
                imgpath = await download_img(result[0], path, proxy=config.api["proxy"]["http_proxy"])
                forMeslist.append(Node(content=[Text(result[1]), Image(file=imgpath)]))

            except Exception as e:
                bot.logger.error(f"预览图{name} 下载失败: {e}")
                forMeslist.append(Node(content=[Text(result[1])]))
        else:
            bot.logger.error(f"{name} 返回失败或无结果")
            forMeslist.append(Node(content=[Text(f"{name} 返回失败或无结果")]))
    await bot.send(event, forMeslist)
async def call_image_search2(bot,event,config,img_url):
    if not config.settings["basic_plugin"]["搜图"]["soutu_bot"]:
        return
    bot.logger.info("调用soutu.bot搜索图片")
    img_path = "data/pictures/cache/" + random_str() + ".png"
    await download_img(img_url, img_path)
    forMeslist=[]
    try:
        r,img=await automate_browser(img_path)
    except Exception as e:
        bot.logger.error(f"Error in automate_browser: {e}")
        return
    bot.logger.info(f"搜索结果：{r}")
    if not r:
        return
    forMeslist.append(Node(content=[Text(f"图片已经过处理，但不保证百分百不被吞。")]))
    for item in r:
        
        try:
            sst=f"标题:{item['title']}\n相似度:{item['similarity']}\n链接:{item['detail_page_url']}"
            sst_img=f"data/pictures/cache/{random_str()}.png"
            await download_img(item['image_url'], sst_img, True,proxy=config.api["proxy"]["http_proxy"])
            forMeslist.append(Node(content=[Text(sst), Image(file=sst_img)]))
        except:
            bot.logger.error("图片下载失败")
            forMeslist.append(Node(content=[Text(sst)]))
    await bot.send(event, forMeslist)
    await bot.send(event,[Image(file=img),Text(f"最高相似度:{r[0]['similarity']}\n标题：{r[0]['title']}\n链接：{r[0]['detail_page_url']}\n\n")],True)
    



async def call_tts(bot,event,config,text,speaker=None,mood="中立"):
    mode = config.api["tts"]["tts_engine"]
    if speaker is None:
        speaker=config.api["tts"][mode]["speaker"]
    all_speakers=await call_all_speakers(bot,event,config)
    all_speakers=all_speakers["speakers"]
    ncspk=all_speakers[0]
    acgnspk=all_speakers[1]
    modelscope_speakers=all_speakers[2]
    vits_speakers=all_speakers[3]
    online_vits2_speakers=all_speakers[4]
    if not ncspk and not acgnspk and not modelscope_speakers and not vits_speakers and not online_vits2_speakers:
        bot.logger.error("No speakers found")
        return
    lock=False
    if acgnspk:
        if speaker in acgnspk:
            lock=True
            mode = "acgn_ai"
        elif f"{speaker}【鸣潮】" in acgnspk:
            speaker=f"{speaker}【鸣潮】"
            lock=True
            mode = "acgn_ai"
        elif f"{speaker}【原神】" in acgnspk:
            speaker=f"{speaker}【原神】"
            lock=True
            mode = "acgn_ai"
        elif f"{speaker}【崩坏3】" in acgnspk:
            speaker=f"{speaker}【崩坏3】"
            lock=True
            mode = "acgn_ai"
        elif f"{speaker}【星穹铁道】" in acgnspk:
            speaker=f"{speaker}【星穹铁道】"
            lock=True
            mode = "acgn_ai"
    if ncspk and not lock:
        if speaker in ncspk:
            mode="napcat_tts"
            speaker=ncspk[speaker]
            lock=True
    if modelscope_speakers and not lock:
        if speaker in modelscope_speakers:
            mode="modelscope_tts"
            lock=True
    if vits_speakers and not lock:
        if speaker in vits_speakers:
            mode="vits"
            lock = True
    if online_vits2_speakers and not lock:
        if speaker in online_vits2_speakers:
            mode="online_vits2"
            lock = True
    else:
        mode=config.api["tts"]["tts_engine"]
    try:
        p=await tts(text=text,speaker=speaker,config=config,mood=mood,bot=bot,mode=mode)
        await bot.send(event, Record(file=p))
        return {"status":"success"}
    except:
        traceback.print_exc()
        pass

async def call_all_speakers(bot,event,config):
    try:
        nc_speakers=await napcat_tts_speakers(bot)
    except Exception as e:
        bot.logger.error(f"Error in napcat_tts_speakers: {e}")
        nc_speakers=None
    try:
        acgn_ai_speakers=await get_acgn_ai_speaker_list()
    except Exception as e:
        bot.logger.error(f"Error in get_acgn_ai_speaker_list: {e}")
        acgn_ai_speakers=None
    modelscope_speakers=get_modelscope_tts_speakers()
    try:
        vits_speakers=await get_vits_speakers(config.api["tts"]["vits"]["base_url"],None)
    except Exception as e:
        bot.logger.error(f"Error in get_vits_speakers: {e}")
        vits_speakers=None
    try:
        online_vits2_speakers=await get_huggingface_online_vits2_speakers()
    except Exception as e:
        bot.logger.error(f"Error in get_huggingface_online_vits2_speakers: {e}")
        online_vits2_speakers=None
    return {"speakers": [nc_speakers,acgn_ai_speakers,modelscope_speakers,vits_speakers,online_vits2_speakers]}
async def call_tarot(bot,event,config):
    if config.settings["basic_plugin"]["tarot"]["彩蛋牌"] and random.randint(1, 100) < \
            config.settings["basic_plugin"]["tarot"]["彩蛋牌"]["probability"]:
        cards_ = config.settings["basic_plugin"]["tarot"]["彩蛋牌"]["card_index"]
        card = random.choice(cards_)
        card_path, text = list(card.items())[0]
        if text=="": text="no description"
        await bot.send(event, [Text(f"{text}"), Image(file=card_path)])
        return {"text": "开出彩蛋牌，来源：jojo的奇妙冒险", "img": card_path}
    txt, img = tarotChoice(config.settings["basic_plugin"]["tarot"]["mode"])
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
    async def search_image(event):
        try:
            if str(event.pure_text) == "搜图" or (event.get("at") and event.get("at")[0]["qq"]==str(bot.id) and event.get("text")[0]=="搜图"):
                await bot.send(event, "请发送要搜索的图片")
                image_search[event.sender.user_id] = []
        except Exception as e:
            pass
        if ("搜图" in str(event.pure_text) or event.sender.user_id in image_search) and event.get('image'):
            try:
                image_search.pop(event.sender.user_id)
            except:
                pass
            try:
                await call_image_search(bot,event,config)
            finally:
                try:
                    image_search.pop(event.sender.user_id)
                except:
                    pass
    @bot.on(GroupMessageEvent)
    async def tts(event: GroupMessageEvent):
        if "说" in event.pure_text and event.pure_text.startswith("/"):
            speaker=event.pure_text.split("说")[0].replace("/","").strip()
            text=event.pure_text.split("说")[1].strip()
            r=await call_tts(bot,event,config,text,speaker)
            if r.get("audio"):
                await bot.send(event, Record(file=r.get("audio")))
        elif event.pure_text=="可用角色":
            #Node(content=[Text("可用角色：")]+[Text(i) for i in get_acgn_ai_speaker_list()])
            all_speakers = await call_all_speakers(bot, event, config)
            all_speakers = all_speakers["speakers"]
            f= all_speakers[0]
            e= all_speakers[1]
            c = all_speakers[2]
            b = all_speakers[3]
            a = all_speakers[4]
            if a:
                a='\n'.join(a)
            if b:
                b='\n'.join(b)
            if f:
                f='\n'.join(f)
            if e:
                e='\n'.join(e)
            if c:
                c='\n'.join(c)
            await bot.send(event, [
                Node(content=[Text(f"使用 /xx说xxxxx")]),
                Node(content=[Text(f"napcat_tts可用角色：\n{f}")]),
                Node(content=[Text(f"acgn_ai可用角色：\n{e}")]),
                Node(content=[Text(f"modelscope_tts可用角色：\n{c}")]),
                Node(content=[Text(f"vits可用角色：\n{b}")]),
                Node(content=[Text(f"online_vits2可用角色：\n{a}")])])

    @bot.on(GroupMessageEvent)
    async def cyber_divination(event: GroupMessageEvent):
        if event.pure_text=="今日塔罗":
            if config.settings["basic_plugin"]["tarot"]["彩蛋牌"] and random.randint(1,100)<config.settings["basic_plugin"]["tarot"]["彩蛋牌"]["probability"]:
                cards_=config.settings["basic_plugin"]["tarot"]["彩蛋牌"]["card_index"]
                card=random.choice(cards_)
                card_path, text = list(card.items())[0]
                if text=="": text="no description"
                await bot.send(event, [Text(f"{text}"), Image(file=card_path)])
                return

            txt, img = tarotChoice(config.settings["basic_plugin"]["tarot"]["mode"])
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





