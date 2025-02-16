import asyncio
import re
from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.music_parsing.music_link_parsing import netease_music_link_parse

def main(bot, config):
    botname = config.basic_config["bot"]["name"]
    bot.logger.info('网易云音乐链接解析功能已上线！')

    @bot.on(GroupMessageEvent)
    async def Music_Link_Prising_search(event: GroupMessageEvent):
        proxy = config.api["proxy"]["http_proxy"]
        url = event.raw_message
        if "music.163.com" not in url:
            return
        link_parsing_json = await netease_music_link_parse(url, filepath='data/pictures/cache/')
        if link_parsing_json['status']:
            bot.logger.info('网易云音乐链接解析成功，开始推送~~~')
            await bot.send(event, Image(file=link_parsing_json['pic_path']))
        else:
            if link_parsing_json['reason']:
                bot.logger.error(f'netease_music_link_error: {link_parsing_json["reason"]}')