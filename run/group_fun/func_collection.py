from developTools.message.message_components import Image, Text,Node
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja

ninja=Lexburner_Ninja()





async def random_ninjutsu(bot: ExtendBot,event,config: YAMLManager):
    ninjutsu=await ninja.random_ninjutsu()
    tags=""
    for tag in ninjutsu['tags']:
        tags+=f"{tag['name']}"
    parse_message=f"忍术名称: {ninjutsu['name']}\n忍术介绍: {ninjutsu['description']}\n忍术标签: {tags}\n忍术教学: {ninjutsu['videoLink']}"
    if ninjutsu['imageUrl']=="":
        messages=[Image(file="https://wsfrs.com/_next/image?url=%2Fninja.png&w=128&q=75"),Text("啊没图使"),Text(parse_message)]
    else:
        messages=[Image(file=ninjutsu['imageUrl']),Text(parse_message)]
    await bot.send(event,messages)
