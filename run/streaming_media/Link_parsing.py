import asyncio

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.Link_parsing import bilibili


def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def bilibili_link(event: GroupMessageEvent):
        await bilibili(event.raw_message,filepath='plugins/resource_search_plugin/Link_parsing/data/')
