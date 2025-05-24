import re
import traceback

from httpx import AsyncClient

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Node, Text
from run.basic_plugin.service.imgae_search.anime_trace import anime_trace


async def call_character_identify(bot, event,config,image_url,model_name):
    bot.logger.info(f"接收来自用户{event.user_id}的识别指令")
    try:
        res=await anime_trace(image_url)
        forward_meslist = [Node(content=[Text(str(res[0]))]), Node(content=[Text(str(res[1]))]),
                           Node(content=[Text(f"AI识别：{str(res[2])}")])]
        bot.logger.info("角色识别成功")
        await bot.send(event, forward_meslist)
        return {"result": str(res)}

    except Exception as e:
        bot.logger.error(f"角色识别出错：{e}")
        await bot.send(event, f"出错啦,请稍后再试~", True)
        traceback.print_exc()



def main(bot ,config):

    image_identify_list = {}

    @bot.on(GroupMessageEvent)
    async def startYouridentify(event :GroupMessageEvent):
        nonlocal image_identify_list
        if event.pure_text=="识别" or (event.get("at") and event.get("at")[0]["qq"] == str(bot.id) and event.get("text") is not None and "识别" in event.get("text")[0]):
            image_identify_list[event.user_id] ={'model' :"anime_model_lovelive"}
            if re.search(r"(?:gal|galgame|游戏)", event.pure_text, re.IGNORECASE):     # 匹配字符串，忽略大小写
                image_identify_list[event.user_id]['model'] ="full_game_model_kira"
            await bot.send(event, "请发送要识别的图片")

        if ((event.get("text") is not None and "识别" in event.get("text")[0]) or (event.user_id in image_identify_list)) and event.get('image') is not None:

            if event.user_id not in image_identify_list:
                if re.search(r"(?:gal|galgame|游戏)", event.pure_text, re.IGNORECASE):
                    model_name="full_game_model_kira"
                else:
                    model_name="full_game_model_kira"
                await bot.send(event,"未指定识别类型，可能影响识别精度")
            else:
                model_name = image_identify_list[event.user_id]['model']

            image_url = event.get('image')[0]['url']
            try:
                image_identify_list.pop(event.user_id)
            except:
                pass

            await call_character_identify(bot, event,config,image_url,model_name)

            




            
