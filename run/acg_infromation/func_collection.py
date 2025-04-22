
"""
供函数调用的同类接口集合
"""
from developTools.message.message_components import Image
from run.acg_infromation.service.arona_api import stageStrategy
from run.acg_infromation.service.steam import steam_query_game


async def anime_game_service_func_collection(bot,event,config,m_type,query_target):
    if m_type == "blue_archive":
        try:
            p = await stageStrategy(query_target)
            await bot.send(event, Image(file=p))
        except Exception as e:
            bot.logger.error(f"无效的角色或网络连接错误{e}")
            await bot.send(event, "无效的角色 或网络连接出错")
    elif m_type=="steam":
        try:
            bot.logger.info(f"查询游戏{query_target}")
            result_dict = await steam_query_game(query_target)
            if result_dict is None:
                await bot.send(event, "没有找到哦，试试其他名字~")
                return
            bot.logger.info(result_dict)
            text = "游戏："
            text = text + result_dict['name'] + f"({result_dict['name_cn']})" + "\n游戏id：" + str(result_dict[
                                                                                                      'app_id']) + "\n游戏描述：" + f"{result_dict['description']}\nSteamUrl：" + f"{result_dict['steam_url']}"
            await bot.send(event, [Image(file=result_dict['path']), text])
        except Exception as e:
            bot.logger.error(e)
            bot.logger.exception("详细错误如下：")
            await bot.send(event, "查询失败")