import base64
import re
import traceback
from io import BytesIO
from urllib.parse import quote

from PIL import Image as Image1
from httpx import AsyncClient

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Node, Text, Image
from plugins.utils.random_str import random_str


async def call_character_identify(bot, event,config,image_url,model_name):
    bot.logger.info(f"接收来自用户{event.user_id}的识别指令")

    async with AsyncClient(trust_env=False) as client:
        res = await client.get(image_url)
    files = {"image": None}
    base_img = Image1.open(BytesIO(res.content)).convert("RGB")
    img_path = f"data/pictures/cache/{random_str()}.png"  # 保存图片到本地
    base_img.save(img_path)
    files["image"] = open(img_path, "rb")

    # 发送请求
    ai_detect = "False"
    url = f"https://aiapiv2.animedb.cn/ai/api/detect?force_one=1&model={model_name}&ai_detect={ai_detect}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
    }
    forward_meslist = []

    try:
        async with AsyncClient(trust_env=False) as client:
            res = await client.post(url=url, headers=headers, data=None, files=files, timeout=30)
            content = res.json()
            # print(content)
        if content["code"] != 0:
            await bot.send(event, f"出错啦~可能是图里角色太多了~\ncontent:{content}", True)
            return
        data = content["data"]
        if len(data) == 0:
            await bot.send(event, "没有识别到任何角色", True)
            return

        st = f'共识别到{len(data)}个角色\n当前模型:{model_name}\n更多模型请访问:https://ai.animedb.cn'

        forward_meslist.append(Node(content=[Text(st)]))
        for item in data:
            width, height = base_img.size
            box = item["box"]
            box = (box[0] * width, box[1] * height, box[2] * width, box[3] * height)

            item_img = base_img.crop(box)
            filename = f"data/pictures/cache/{random_str()}.png"
            item_img.save(filename, format="JPEG", quality=int(item["box"][4] * 100))  # 保存到本地

            # 构造消息
            st1 = f"该角色可能为：\n\n"
            for char in item['char'][0:3]:
                st1 += (
                    f"{char['name']}\n"
                    f"出自作品：{char['cartoonname']}\n"
                    f"萌娘百科：zh.moegirl.org.cn/index.php?search={quote(char['name'])}\n"
                    f"bing搜索：www.bing.com/images/search?q={quote(char['name'])}\n\n")
            forward_meslist.append(Node(content=[Text(st1),Image(file=filename)]))



        bot.logger.info("角色识别成功")
        await bot.send(event, forward_meslist)
        return {"result": st1}

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
        if event.pure_text=="识别" or (event.get("at") and event.get("at")[0]["qq"] == str(bot.id) and event.get("text")[0]=="识别"):
            image_identify_list[event.user_id] ={'model' :"anime_model_lovelive"}
            if re.search(r"(?:gal|galgame|游戏)", event.pure_text, re.IGNORECASE):     # 匹配字符串，忽略大小写
                image_identify_list[event.user_id]['model'] ="game_model_kirakira"
            await bot.send(event, "请发送要识别的图片")


        if ((event.get("text") is not None and event.get("text")[0]=="识别") or (event.user_id in image_identify_list)) and event.get('image') is not None:

            if event.user_id not in image_identify_list:
                if re.search(r"(?:gal|galgame|游戏)", event.pure_text, re.IGNORECASE):
                    model_name="game_model_kirakira"
                else:
                    model_name="game_model_kirakira"
                await bot.send(event,"未指定识别类型，可能影响识别精度")
            else:
                model_name = image_identify_list[event.user_id]['model']

            image_url = event.get('image')[0]['url']
            try:
                image_identify_list.pop(event.user_id)
            except:
                pass

            await call_character_identify(bot, event,config,image_url,model_name)

            




            
