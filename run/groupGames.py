# -*- coding:utf-8 -*-
'''
疑似暂未提供禁言对应接口

'''
import random

import yaml
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Text

from plugins.tookits import wash_cqCode

Roulette = {}


def main(bus,bot, logger):
    with open('config/GroupGameSettings.yaml', 'r', encoding='utf-8') as file:
        ggs = yaml.load(file, Loader=yaml.FullLoader)
    RouletteGGS = ggs.get("RouletteGame")

    @bus.on(GroupMessageEvent)
    async def startRoulette(event: GroupMessageEvent):
        if wash_cqCode(event.raw_message).startswith("/赌 "):
            if event.group_id in Roulette:
                await bot.send(event, random.choice(RouletteGGS.get("prohibited")))
                return
            else:
                try:
                    bullet = int(wash_cqCode(event.raw_message).replace("/赌 ", ""))
                except:
                    await bot.send_group_message(event.group_id, [Text("无效的指令，请发送/赌 数字 开启赌局，例如 /赌 4")])
                    return
                if bullet < 7:
                    magazine = []
                    while len(magazine) < 6:
                        while len(magazine) < bullet:
                            magazine.append(1)
                        magazine.append(0)
                    Roulette[event.group_id] = magazine
                    logger.info(str(magazine))

                    await bot.send_group_message(event.group_id, [Text("装填弹药" + str(bullet) + "\n请发送s参与游戏")])
                else:
                    await bot.send_group_message(event.group_id, [Text("无效的指令，请发送/赌 数字 开启赌局，例如 /赌 4")])

    @bus.on(GroupMessageEvent)
    async def runningRoulette(event: GroupMessageEvent):
        if wash_cqCode(event.raw_message) == "s" and event.group_id in Roulette:
            a = random.choice(Roulette.get(event.group_id))
            logger.info("===========")
            logger.info(a)
            logger.info(Roulette.get(event.group_id))
            if a == 1:
                logger.info("禁言")

                try:
                    await bot.mute()
                    #await bot.mute(target=event.sender.group.id, member_id=event.sender.id,
                                   #time=RouletteGGS.get("bantime"))

                    await bot.send_group_message(event.group_id, [Text( random.choice(RouletteGGS.get("muteWord")))])
                except:
                    await bot.send_group_message(event.group_id,[Text( random.choice(RouletteGGS.get("muteFailed")))])
            else:
                logger.info("不禁言")
                await bot.send_group_message(event.group_id, [Text(random.choice(RouletteGGS.get("unmute")))])
            lia = Roulette.get(event.group_id)
            try:
                lia.remove(a)
            except:
                pass
            logger.info(lia)

            if len(lia) < 1 or not lia.count(1):
                Roulette.pop(event.group_id)
                # print("赌局结束")
                await bot.send_group_message(event.group_id, [Text("赌局结束")])
                return
            Roulette[event.group_id] = lia
