# -*- coding: utf-8 -*-
import inspect
import os
import random

import yaml
import httpx
from bs4 import BeautifulSoup
from fuzzywuzzy import process

from yiriob.event.events import GroupMessageEvent
from yiriob.message import Record, Text

from plugins.cloudMusic import newCloudMusicDown, cccdddm
from plugins.toolkits import wash_cqCode, validate_rule, fileUrl


def load_command_rules(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


command_rules = load_command_rules('config/commands.yaml')['musicPick']

def main(bot,bus, logger):
    logger.warning("语音点歌 loaded")
    global musicTask
    musicTask = {}
    
    controller = bot.controller
    downloadMusicUrl = controller.get("点歌").get("下载链接")
    musicToVoice = controller.get("点歌").get("musicToVoice")


    async def dianzibofangqi(event,message):
        logger.info("电梓播放器，启动！")
        p = os.listdir("data/music/audio")
        purchase = random.choice(p)
        await bot.send_group_message(event.group_id, [Record(file=fileUrl("data/music/audio/" + purchase),url="")])
        await bot.send_group_message(event.group_id, f"正在播放：{purchase}")


    async def dianzibofangqiPick(event,message):
        current_function_name = inspect.currentframe().f_code.co_name
        aim = ""
        for rule in command_rules[current_function_name]["rules"]:
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            aim = message.replace(rule_content, '')
        logger.info("电梓播放器，启动！")
        p = os.listdir("./data/music/audio")
        ha = process.extractBests(aim, p, limit=3)
        logger.info(ha[0][0])
        p = "data/music/audio/" + ha[0][0]
        await bot.send_group_message(event.group_id, [Record(file=fileUrl(p),url="")])


    async def selectMusic(event,message):
        global musicTask
        current_function_name = inspect.currentframe().f_code.co_name
        aim = ""
        for rule in command_rules[current_function_name]["rules"]:
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            aim = message.replace(rule_content, '')
        musicName = aim
        logger.info("点歌：" + musicName)
        if musicToVoice:
            ffs = await cccdddm(musicName)
            if ffs is None:
                await bot.send_group_message(event.group_id, "连接出错，或无对应歌曲")
            else:
                musicTask[event.sender.user_id] = ffs
                musicL = ""
                count1 = 1
                for ib in ffs:
                    musicL += f"{count1} {ib[0]} {ib[2]}\n"
                    count1 += 1
                await bot.send_group_message(event.group_id, [Text(f"请发送对应歌曲的序号:\n{musicL}")])
        else:
            ffs = await cccdddm(musicName)
            if ffs is None:
                await bot.send_group_message(event.group_id, "连接出错，或无对应歌曲")
            else:
                musicTask[event.sender.user_id] = ffs
                # print(ffs)
                t = "请发送序号："
                i = 1
                for sf in ffs:
                    t += f"\n{i} {sf[0]}  |  {sf[2]}"
                    i += 1
                await bot.send_group_message(event.group_id, t)

    @bus.on(GroupMessageEvent)
    async def select11Music(event: GroupMessageEvent):
        global musicTask
        if event.sender.user_id in musicTask:
            try:
                if musicToVoice:
                    try:
                        order = int(wash_cqCode(event.raw_message))
                    except:
                        await bot.send_group_message(event.group_id, "点歌失败！不规范的操作\n请输入数字。")
                        musicTask.pop(event.sender.user_id)
                        return
                    if order < 1:
                        order = 1
                    musiclist = musicTask.get(event.sender.user_id)
                    logger.info(f"获取歌曲：{musiclist[order - 1]}")
                    musicTask.pop(event.sender.user_id)
                    if downloadMusicUrl:
                        p, MusicUrlDownLoad = await newCloudMusicDown(musiclist[order - 1][1], True)
                        await bot.send_group_message(event.group_id, f"下载链接(mp3)：{MusicUrlDownLoad}")
                    else:
                        p = await newCloudMusicDown(musiclist[order - 1][1])
                    logger.info(f"已下载目标单曲：{p}")
                    await bot.send_group_message(event.group_id, [Record(file=fileUrl(p),url="")])
                else:
                    '''ass = musicTask.get(event.sender.user_id)[int(wash_cqCode(event.raw_message)) - 1]
                    logger.info("获取歌曲：" + ass[0])

                    client = httpx.Client(headers=get_headers())
                    url = f'https://music.163.com/song?id={ass[1]}'
                    response = client.get(url)
                    musicTask.pop(event.sender.user_id)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    imgurl = soup.find('img', class_='j-img')['data-src']
                    await bot.send_group_message(event.group_id, MusicShare(kind="QQMusic", title=ass[0],
                                                     summary=ass[2],
                                                     jump_url=f"https://y.music.163.com/m/song?id={ass[1]}&uct2=jkZ3LZNLyka9TmygfSgqeQ%3D%3D&dlt=0846&app_version=9.0.95",
                                                     picture_url=imgurl,
                                                     music_url=f"http://music.163.com/song/media/outer/url?id={ass[1]}",
                                                     brief=ass[2]))'''

            except Exception as e:
                logger.error(e)
                try:
                    musicTask.pop(event.sender.user_id)
                except:
                    pass
                await bot.send_group_message(event.group_id, e)
    command_map={
        "dianzibofangqi": dianzibofangqi,
        "dianzibofangqiPick": dianzibofangqiPick,
        "selectMusic": selectMusic
    }
    @bus.on(GroupMessageEvent)
    async def handle_command(event: GroupMessageEvent):
        message = wash_cqCode(event.raw_message)
        for function_name, rules in command_rules.items():
            if rules['enable']:  # 检查功能是否启用
                for rule in rules['rules']:
                    if validate_rule(message, rule):
                        await command_map[function_name](event, message)  # 通过命令映射调用处理函数
                        return
