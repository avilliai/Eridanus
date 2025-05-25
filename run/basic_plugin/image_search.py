import asyncio

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Node, Image, Text
from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from framework_common.utils.random_str import random_str
from framework_common.utils.utils import download_img
from run.basic_plugin.service.imgae_search.image_search import automate_browser
from run.basic_plugin.service.imgae_search.image_search2 import fetch_results

image_search={}


async def call_image_search(bot, event, config, image_url=None):
    user_info = await get_user(event.user_id, event.sender.nickname)
    bot.logger.info("接收来自 用户：" + str(event.sender.user_id) + " 的搜图指令")
    if not config.basic_plugin.config["搜图"]["聚合搜图"] and not config.basic_plugin.config["搜图"]["soutu_bot"]:
        await bot.send(event, "没有开启搜图功能")
        return
    await bot.send(event, "正在搜索图片，请等待结果返回.....")
    if user_info.permission >= config.basic_plugin.config["搜图"]["search_image_resource_operate_level"]:
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


async def call_image_search1(bot, event, config, img_url):
    if not config.basic_plugin.config["搜图"]["聚合搜图"]:
        return
    bot.logger.info("调用聚合接口搜索图片")
    results = await fetch_results(config.common_config.basic_config["proxy"]["http_proxy"], img_url,
                                  config.basic_plugin.config["image_search"]["sauceno_api_key"])
    async def extract_data(name,result):
        node_list = []
        if name=="saucenao":
            for item in result:
                try:
                    path = "data/pictures/cache/" + random_str() + ".png"
                    imgpath = await download_img(item[0], path,proxy=config.common_config.basic_config["proxy"]["http_proxy"],gray_layer=True)
                    node_list.append(Node(content=[Image(file=imgpath),Text(item[1])]))
                except Exception as e:
                    bot.logger.error(f"Error in extract_data: {e}")
                    node_list.append(Node(content=[Text(item[1])]))
                    continue
        if name=="anime_trace":
            node_list.append(Node(content=[Text(f"ai创作检测：{result[2]}")]))
            node_list.append(Node(content=[Text(result[0])]))
            node_list.append(Node(content=[Text(result[1])]))
        return node_list

    forMeslist = []
    for name, result in results.items():
        if result and result[0] != "":
            bot.logger.info(f"{name} 成功返回: {result}")
            forMeslist.extend(await extract_data(name, result))
    await bot.send(event, forMeslist)


async def call_image_search2(bot, event, config, img_url):
    if not config.basic_plugin.config["搜图"]["soutu_bot"]:
        return
    bot.logger.info("调用soutu.bot搜索图片")
    img_path = "data/pictures/cache/" + random_str() + ".png"
    await download_img(img_url, img_path)
    forMeslist = []
    try:
        r, img = await automate_browser(img_path)
    except Exception as e:
        bot.logger.error(f"Error in automate_browser: {e}")
        return
    bot.logger.info(f"搜索结果：{r}")
    if not r:
        return
    forMeslist.append(Node(content=[Text(f"图片已经过处理，但不保证百分百不被吞。")]))
    for item in r:

        try:
            sst = f"标题:{item['title']}\n相似度:{item['similarity']}\n链接:{item['detail_page_url']}"
            sst_img = f"data/pictures/cache/{random_str()}.png"
            await download_img(item['image_url'], sst_img, True,
                               proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            forMeslist.append(Node(content=[Text(sst), Image(file=sst_img)]))
        except:
            bot.logger.error("图片下载失败")
            forMeslist.append(Node(content=[Text(sst)]))
    await bot.send(event, forMeslist)
    await bot.send(event, [Image(file=img), Text(
        f"最高相似度:{r[0]['similarity']}\n标题：{r[0]['title']}\n链接：{r[0]['detail_page_url']}\n\n")], True)


def main(bot: ExtendBot,config:YAMLManager):
    @bot.on(GroupMessageEvent)
    async def search_image(event):
        try:
            if str(event.pure_text) == "搜图" or (
                    event.get("at") and event.get("at")[0]["qq"] == str(bot.id) and event.get("text")[0] == "搜图"):
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
                await call_image_search(bot, event, config)
            finally:
                try:
                    image_search.pop(event.sender.user_id)
                except:
                    pass