import asyncio

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.Link_parsing import bilibili


def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def bilibili_link(event: GroupMessageEvent):
        url=event.raw_message
        if event.sender.user_id == 2684831639:return
        if not ('bili' in url or 'b23' in url): return
        print(url)
        await bilibili(url,filepath='plugins/resource_search_plugin/Link_parsing/data/')
        await bot.send(event, [f' 枫与岚识别结果：\n',
                               Image(file='plugins/resource_search_plugin/Link_parsing/data/result.png')])
