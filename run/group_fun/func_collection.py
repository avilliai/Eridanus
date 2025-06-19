from developTools.message.message_components import Image, Text
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from run.group_fun.service.lex_burner_Ninja import Lexburner_Ninja
from run.streaming_media.youtube import download_video

ninja = Lexburner_Ninja()


async def random_ninjutsu(bot: ExtendBot, event, config: YAMLManager):
    bot.logger.info("随机获取忍术")
    ninjutsu = await ninja.random_ninjutsu()
    tags = ""
    for tag in ninjutsu['tags']:
        tags += f"{tag['name']},"
    parse_message = f"忍术名称: {ninjutsu['name']}\n忍术介绍: {ninjutsu['description']}\n忍术标签: {tags}\n忍术教学: {ninjutsu['videoLink']}\n更多忍术请访问: https://wsfrs.com/"
    if not ninjutsu.get('imageUrl'):
        messages = [Image(file="run/group_fun/service/img.png"), Text("啊没图使\n"), Text(parse_message)]
    else:
        messages = [Image(file=ninjutsu['imageUrl']), Text(parse_message)]
    try:
        await bot.send(event, messages)
    except Exception as e:
        await bot.send(event, [Image(file="run/group_fun/service/img.png"), Text("啊没图使\n"), Text(parse_message)])
    if ninjutsu['videoLink']:
        await download_video(bot, event, config, ninjutsu['videoLink'], platform="bilibili")


async def query_ninjutsu(bot: ExtendBot, event, config: YAMLManager, name):
    bot.logger.info(f"查询忍术: {name}")
    try:
        ninjutsu = await ninja.query_ninjutsu(name)
        parse_message = f"忍术名称: {ninjutsu['title']}\n忍术介绍: {ninjutsu['description']}\n忍术标签: {ninjutsu['tags']}\n忍术教学: {ninjutsu['videoLink']}"
        await bot.send(event, [Image(file="run/group_fun/service/img.png"), Text("啊没图使\n"), Text(parse_message)])
        if ninjutsu['videoLink']:
            await download_video(bot, event, config, ninjutsu['videoLink'], platform="bilibili")
    except Exception as e:
        bot.logger.error(f"忍术查询失败: {e}")
        await bot.send(event, [Image(file="run/group_fun/service/img.png"), Text("啊没图使\n"),
                               Text("找不到这个忍术，请检查拼写或重新输入")])
