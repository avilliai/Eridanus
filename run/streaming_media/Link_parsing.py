import asyncio

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.core.login_core import ini_login_Link_Prising
from plugins.resource_search_plugin.Link_parsing.Link_parsing import link_prising

def main(bot,config):
    botname=config.basic_config["bot"]["name"]
    bili_login_check,douyin_login_check=ini_login_Link_Prising(type=0)
    if bili_login_check and douyin_login_check:
        bot.logger.info('链接解析功能已上线！')
    else:
        if not bili_login_check:
            bot.logger.error('B站session未能成功获取，部分功能将受到限制')
        else:
            bot.logger.info('B站session成功获取')
        if not douyin_login_check:
            bot.logger.error('未能获取到设置抖音的ck，将无法解析抖音视频！')
        else:
            bot.logger.info('抖音的ck成功获取！')
    @bot.on(GroupMessageEvent)
    async def Link_Prising_search(event: GroupMessageEvent):
        url=event.raw_message
        if event.sender.user_id == 2684831639:return
        dy_file_path,url_check=await link_prising(url,filepath='data/pictures/cache/')
        if dy_file_path is not None:
            await bot.send(event, [f'{botname}识别结果：\n',Image(file=dy_file_path)])
