
from developTools.event.events import GroupMessageEvent
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja


def main(bot: ExtendBot,config: YAMLManager):
    ninja=Lexburner_Ninja()
    @bot.on(GroupMessageEvent)
    async def handle_group_message(event: GroupMessageEvent):
        if event.pure_text=="随机忍术":
            await bot.send(event,"Hello World!")