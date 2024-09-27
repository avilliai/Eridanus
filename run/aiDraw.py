import threading

import yaml
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Image, Reply, Text

from plugins.aiDrawer import SdDraw, draw2, airedraw, draw1, draw3, tiktokredraw, draw5, draw4, draw6, fluxDrawer
from plugins.bingImageCreater.bingDraw import bingCreate
from plugins.tookits import random_str, fileUrl, wash_cqCode, validate_rule


def load_command_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


command_aiDraw_rules = load_command_rules('config/commands.yaml')['aiDraw']["aiDraw"]
def check_command_rules(message):
    for rule in command_aiDraw_rules['rules']:
        if validate_rule(message, rule):
            return True
    return False
def bingImageCreator(bus,bot, logger):
    logger.info("bingai绘画 enabled")
    resulttr = bot.api
    sock5proxy = resulttr.get("sock5-proxy")
    bing_image_creator_key = resulttr.get("bing-image-creator")
    @bus.on(GroupMessageEvent)
    async def msDrawer(event: GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)):
            tag = ""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            list1 = ["sex", "nsfw", "性交", "做爱", "pussy", "奴隶", "调教", "中出", "后入", "颜射", "阴道", "NSFW",
                     "SEX", "Sex"]
            for i in list1:
                if i in tag:
                    await bot.send_group_message(event.group_id, [Text("审核策略生效，请检查并去除prompt中违规内容")])
                    return
            if bing_image_creator_key.get("_U") != "" and bing_image_creator_key.get("KievRPSSecAuth") != "":
                try:
                    logger.info(f"bing接口发起请求:{tag}")
                    p = await bingCreate(sock5proxy, tag, bing_image_creator_key.get("_U"),
                                         bing_image_creator_key.get("KievRPSSecAuth"))
                    plist = []
                    for i in p:
                        plist.append(Image(file=fileUrl(i), type='flash', url=""))
                    await bot.send_group_message(event.group_id, plist, True)
                except Exception as e:
                    logger.error(e)
                    await bot.send_group_message(event.group_id, [Text("出错，请重试；可能是bing cookie过期，请检查")])

def main(bot, bus,logger):
    logger.info("聚合ai绘画 enabled")
    result=bot.api
    sdUrl = result.get("sdUrl")


    controller = bot.controller
    aiDrawController = controller.get("ai绘画")
    negative_prompt = aiDrawController.get("negative_prompt")
    positive_prompt = aiDrawController.get("positive_prompt")
    global redraw
    redraw = {}


    bing_image_creator_key = bot.api.get("bing-image-creator")
    if bing_image_creator_key.get("_U") != "" and bing_image_creator_key.get("KievRPSSecAuth") != "":

        thread = threading.Thread(target=bingImageCreator(bus,bot, logger), daemon=True)
        thread.start()
    else:
        logger.info("bing接口未配置，ai绘画功能将无法使用")


    @bus.on(GroupMessageEvent)
    async def msDrawer(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("modelscopeSD"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")

            logger.info("发起modelscope SDai绘画请求，prompt:" + tag)
            try:
                p = await fluxDrawer(tag)
                await bot.send_group_message(event.group_id, [Image(file=p, type='flash', url=""),Reply(str(event.message_id))])

            except Exception as e:
                logger.error(e)
                logger.error("modelscope Drawer出错")

    @bus.on(GroupMessageEvent)
    async def AiSdDraw(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("sd接口"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = f"data/pictures/cache/{random_str()}.png"
            logger.info(f"发起SDai绘画请求，path:{path}|prompt:{tag}")
            try:
                # 没啥好审的，controller直接自个写了。
                p = await SdDraw(tag + positive_prompt, negative_prompt, path, sdUrl)
                # logger.error(str(p))
                await bot.send_group_message(event.group_id, [Image(file=fileUrl(path), type='flash', url=""),Reply(str(event.message_id))])
                # logger.info("success")
            except Exception as e:
                logger.error(e)

    @bus.on(GroupMessageEvent)
    async def aidrawf1(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口1"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:" + path + "|prompt:" + tag)
            i = 1
            while i < 8:
                try:
                    logger.info(f"接口1绘画中......第{i}次请求....")
                    p = await draw1(tag, path)
                    logger.error(str(p))
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(p[0]), type='flash', url=""),Image(file=fileUrl(p[1]), type='flash', url=""),Image(file=fileUrl(p[2]), type='flash', url=""),Image(file=fileUrl(p[3]), type='flash', url="")])
                except Exception as e:
                    logger.error(e)
                    logger.error("接口1绘画失败.......")
                    i += 1
                    # await bot.send(event,"接口1绘画失败.......")

    @bus.on(GroupMessageEvent)
    async def aidrawff2(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口2"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口2绘画中......")
                p = await draw2(tag, path)
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(path), type='flash', url="")])
            except Exception as e:
                logger.error(e)
                logger.error("接口2绘画失败.......")
                # await bot.send(event,"接口2绘画失败.......")

    @bus.on(GroupMessageEvent)
    async def aidrawff3(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口3"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            if len(tag) > 100:
                return
            try:
                logger.info("接口3绘画中......")
                p = await draw3(tag, path)
                
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(path), type='flash', url="")])
            except Exception as e:
                logger.error(e)
                logger.error("接口3绘画失败.......")

    @bus.on(GroupMessageEvent)
    async def aidrawff4(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口5"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口5绘画中......")
                p = await draw5(tag, path)
                
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(path), type='flash', url="")])
            except Exception as e:
                logger.error(e)
                logger.error("接口5绘画失败.......")

    @bus.on(GroupMessageEvent)
    async def aidrawff4(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口6"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            i = 0
            while i < 5:
                try:
                    logger.info("接口6绘画中......")
                    p = await draw6(tag, path)
                    
                    await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(path), type='flash', url="")])
                    return
                except Exception as e:
                    logger.error(e)
                    logger.error("接口6绘画失败.......")
                    i += 1

    @bus.on(GroupMessageEvent)
    async def aidrawff5(event:GroupMessageEvent):
        if check_command_rules(wash_cqCode(event.raw_message)) and aiDrawController.get("接口4"):
            tag=""
            for rule in command_aiDraw_rules["rules"]:
                rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
                tag = wash_cqCode(event.raw_message).replace(rule_content, "")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                logger.info("接口4绘画中......")
                p = await draw4(tag, path)
                await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Image(file=fileUrl(path), type='flash', url="")])
            except Exception as e:
                logger.error(e)
                logger.error("接口4绘画失败.......")

    '''@bus.on(GroupMessageEvent)
    async def rededd(event:GroupMessageEvent):
        global redraw
        if wash_cqCode(event.raw_message).startswith("以图生图 ") and aiDrawController.get("ai重绘"):
            await bot.send(event, "请发送图片，bot随后将开始绘制")
            redraw[event.sender.id] = wash_cqCode(event.raw_message).replace("以图生图 ", "")

    @bus.on(GroupMessageEvent)
    async def redrawStart(event:GroupMessageEvent):
        global redraw
        if event.message_chain.count(Image) and event.sender.id in redraw:
            prompt = redraw.get(event.sender.id)
            lst_img = event.message_chain.get(Image)
            url1 = lst_img[0].url
            logger.info(f"以图生图,prompt:{prompt} url:{url1}")
            path = "data/pictures/cache/" + random_str() + ".png"
            try:
                p = await airedraw(prompt, url1, path)
                await bot.send(event, Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event, "接口1绘画出错")
            try:
                p = await tiktokredraw(prompt, url1, path)
                await bot.send(event, Image(path=p))
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event, "接口2绘画出错")
            redraw.pop(event.sender.id)'''
