
from developTools.event.events import GroupMessageEvent
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from run.group_fun.func_collection import random_ninjutsu, query_ninjutsu
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja


def main(bot: ExtendBot,config: YAMLManager):
    @bot.on(GroupMessageEvent)
    async def handle_group_message(event: GroupMessageEvent):
        if event.pure_text=="随机忍术":
            await random_ninjutsu(bot,event,config)
        if event.pure_text.startswith("查询忍术"):
            name=event.pure_text.replace("查询忍术","")
            await query_ninjutsu(bot,event,config,name)
