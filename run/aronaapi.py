# -*- coding: utf-8 -*-
import asyncio
import inspect
import re
import threading
import time
from asyncio import sleep

import httpx
import yaml
from yiriob.event.events import GroupMessageEvent
from yiriob.message import Image, Reply, Text

# 1
from plugins.aronaBa import stageStrategy
from plugins.toolkits import wash_cqCode, fileUrl


async def pushAronaData(baMonitor,bot,logger):
    while baMonitor:
        logger.info("检查arona订阅更新")
        with open("data/text/aronaSub.yaml", 'r', encoding='utf-8') as f:
            result9 = yaml.load(f.read(), Loader=yaml.FullLoader)
            for i in result9:
                for ia in result9.get(i).get("hash"):
                    logger.info("检查" + ia + "更新")
                    await sleep(25)
                    url1 = "https://arona.diyigemt.com/api/v2/image?name=" + ia
                    async with httpx.AsyncClient(timeout=100) as client:  # 100s超时
                        try:
                            r = await client.get(url1)  # 发起请求
                        except Exception as e:
                            logger.error(e)
                            continue
                        r = r.json()
                        newHash = r.get("data")[0].get("hash")
                    if str(newHash) != result9.get(i).get("hash").get(ia):
                        p = await stageStrategy(ia)
                        alreadySend = []
                        for iss in result9.get(i).get("groups"):
                            if iss in alreadySend:
                                continue
                            try:
                                await bot.send_group_message(int(iss), [Text("获取到" + ia + "数据更新"),
                                                                        Image(file=fileUrl(p), type='flash', url="")])
                                alreadySend.append(iss)
                            except:
                                logger.error("向" + str(iss) + "推送更新失败")
                                alreadySend.append(iss)
                        result9[i]["hash"][ia] = str(newHash)
                        with open('data/text/aronaSub.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(result9, file, allow_unicode=True)
        await sleep(600)  # 600秒更新一次

def main(bot, bus, logger):
    logger.info("arona loaded")
    baMonitor=bot.controller.get("碧蓝档案").get("订阅与推送")
    def run_push_arona_data():
        asyncio.run(pushAronaData(baMonitor, bot, logger))

    thread = threading.Thread(target=run_push_arona_data, daemon=True)
    thread.start()
    def load_command_rules(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    command_rules = load_command_rules('config/commands.yaml')['bluearchive']

    async def selectMission(event,message):
        current_function_name = inspect.currentframe().f_code.co_name
        url=""
        for rule in command_rules[current_function_name]["rules"]:
            rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')
            url = message.replace(rule_content, '')
        logger.info("查询攻略：" + url)
        try:
            p = await stageStrategy(url)
            await bot.send_group_message(event.group_id, [Image(file=fileUrl(p), type='flash', url=""),Reply(str(event.message_id))])
        except Exception as e:
            logger.error(e)
            logger.error("无效的角色或网络连接错误")
            await bot.send_group_message(event.group_id, [Reply(str(event.message_id)),Text("无效的角色 或网络连接出错")])

    async def addSUBgroup(event,message):
        message=message.replace(" ","")
        if message == "/订阅日服":
            a = "日服"
        elif message == "/订阅国际服":
            a = "国际服"
        elif message == "/订阅国服":
            a = "国服"
        else:
            if message.startswith("/订阅"):
                await bot.send_group_message(event.group_id,
                                             [Reply(str(event.message_id)), Text("无效的服务器订阅")])
                return
            else:
                return
        with open("data/text/aronaSub.yaml", 'r', encoding='utf-8') as f:
            result9 = yaml.load(f.read(), Loader=yaml.FullLoader)
            bsg = result9.get(a).get("groups")
            if event.group_id in bsg:
                await bot.send_group_message(event.group_id,[Reply(str(event.message_id)), Text("本群已订阅")])
                return
            bsg.append(event.group_id)
            result9[a]["groups"] = bsg
            with open('data/text/aronaSub.yaml', 'w', encoding="utf-8") as file:
                yaml.dump(result9, file, allow_unicode=True)
            bss = result9.get(a).get("hash")
            for i in bss:
                p = await stageStrategy(i)
                await bot.send_group_message(event.group_id, [Text("获取到" + i + "数据"), Image(file=fileUrl(p), type='flash', url="")])
            logger.info(str(event.group_id) + "新增订阅")
            await bot.send_group_message(event.group_id, [Text("成功订阅")])


    async def aronad(event,message):
        url = "杂图"
        logger.info("查询攻略：" + url)
        try:
            p = await stageStrategy(url)
            await bot.send_group_message(event.group_id, [Text("根据图中列出的项目，发送/arona 项目 即可查询，不需要艾特\n示例如下：\n/arona 国服人权\n/arona H11-2"),Image(file=fileUrl(p), type='flash', url=""),
                                                          Reply(str(event.message_id))])

        except:
            logger.error("无效的角色或网络连接错误")

            await bot.send_group_message(event.group_id, [Text("无效的角色 或网络连接出错")])

    command_map = {
        "selectMission": selectMission,
        "addSUBgroup": addSUBgroup,
        "aronad": aronad
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

    def validate_rule(message, rule):
        # 绕过引号的影响
        message = message.strip('"\'')  # 移除消息两端的引号
        rule = rule.strip()  # 移除规则两端的空白字符

        # 如果规则是正则表达式
        if rule.startswith("re.match("):
            pattern = rule.split('(', 1)[1][:-1]  # 提取正则表达式
            return bool(re.match(pattern, message))  # 返回匹配结果

        # 处理其他规则
        rule_content = rule.split('(')[1][:-1].replace('"', '').replace("'", '')  # 移除规则中的引号

        if rule.startswith("endswith(") and message.endswith(rule_content):
            return True
        elif rule.startswith("startswith(") and message.startswith(rule_content):
            return True
        elif rule.startswith("fullmatch(") and message == rule_content:
            return True

        return False