import re
import traceback

from httpx import AsyncClient

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Node, Text


async def call_character_identify(bot, event,config,image_url,model_name):
    bot.logger.info(f"接收来自用户{event.user_id}的识别指令")

    # 发送请求
    ai_detect = "True"
    url=f"https://api.animetrace.com/v1/search"
    data={
        "is_multi": 0,
        "model": model_name,
        "ai_detect": ai_detect,
        "url": image_url
    }
    #url = f"https://aiapiv2.animedb.cn/ai/api/detect?force_one=1&model={model_name}&ai_detect={ai_detect}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    }
    forward_meslist = []

    try:
        async with AsyncClient(trust_env=False) as client:
            res = await client.post(url=url, headers=headers, data=data, timeout=30)
            content = res.json()
            result_lines = []
            forward_meslist.append(Node(content=[Text(f"识别结果如下")]))
            if "ai" in content:
                if content["ai"]:
                    forward_meslist.append(Node(content=[Text(f"ai创作？：{content['ai']}")]))
            for item in content['data']:
                for character in item['character']:
                    result_lines.append(f"{character['work']} - {character['character']}")
            forward_meslist.append(Node(content=[Text("\n".join(result_lines))]))

            bot.logger.info("角色识别成功")
            await bot.send(event, forward_meslist)
            return {"result": "\n".join(result_lines)}

    except Exception as e:
        bot.logger.error(f"角色识别出错：{e}")
        await bot.send(event, f"出错啦,请稍后再试~", True)
        traceback.print_exc()



def main(bot ,config):

    global image_identify_list
    image_identify_list = {}

    @bot.on(GroupMessageEvent)
    async def startYouridentify(event :GroupMessageEvent):
        global image_identify_list
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

            




            
