import asyncio
from concurrent.futures import ThreadPoolExecutor

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.Link_parsing import bilibili


def main(bot,config):

    @bot.on(GroupMessageEvent)
    async def bilibili_link(event: GroupMessageEvent):
        url=event.raw_message
        if event.sender.user_id == 2684831639:return
        if not ('bili' in url or 'b23' in url): return
        #print(url)
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, asyncio.run, bilibili(url,filepath='plugins/resource_search_plugin/Link_parsing/data/',dynamicid=event.group_id))

        await bot.send(event, [Image(file=f'plugins/resource_search_plugin/Link_parsing/data/{event.group_id}.png')])
