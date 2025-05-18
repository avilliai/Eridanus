from developTools.message.message_components import Image, Text
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja

ninja=Lexburner_Ninja()

async def random_ninjutsu(bot: ExtendBot,event,config: YAMLManager):
    ninjutsu=ninja.random_ninjutsu()
    tags=""
    for tag in ninjutsu['tags']:
        tags+=f"{tag['name']}"
    parse_message=f"忍术名称:{ninjutsu['name']}\n忍术介绍:{ninjutsu['description']}\n忍术标签:{tags}\n忍术教学:{ninjutsu['videoLink']}"
    await bot.send(event,[Image(file=ninjutsu['imageUrl']),Text(parse_message)])