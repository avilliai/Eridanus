# -*- coding: utf-8 -*-


from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from run.acg_infromation.func_collection import anime_game_service_func_collection


def main(bot, config):
    @bot.on(GroupMessageEvent)
    async def query_game(event: GroupMessageEvent):
        if event.pure_text.startswith("steam查询 "):
            game_name = event.pure_text.split(" ")[1]
            await anime_game_service_func_collection(bot,event,config,"steam",game_name)
