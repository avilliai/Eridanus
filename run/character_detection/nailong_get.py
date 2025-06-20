import asyncio
import base64
import json
import random
from concurrent.futures import ThreadPoolExecutor

import httpx

from developTools.event.events import GroupMessageEvent
from framework_common.database_util.llmDB import use_folder_chara
from run.ai_llm.service.aiReplyCore import aiReplyCore
from run.character_detection.func_collection import operate_group_censor


def main(bot, config):
    sets = config.character_detection.config["抽象检测"]
    chehui1 = sets["奶龙撤回"]
    mute1 = sets["奶龙禁言"]
    attack1 = sets["骂奶龙"]
    chehui2 = sets["doro撤回"]
    mute2 = sets["doro禁言"]
    attack2 = sets["骂doro"]
    if_nailong = sets["奶龙检测"]
    if_doro = sets["doro检测"]
    if_nanniang = sets["男娘检测"]
    if not if_nailong and not if_doro and not if_nanniang:
        bot.logger.info("Character Detection: No character detection service is enabled.")
        return
    else:
        from run.character_detection.service.nailong11.nailong import main as nailong_main
        from run.character_detection.service.doro.doro import main as doro_main
        from run.character_detection.service.nanniang.nn import main as nn_main

    nailong_groups = config.character_detection.nailong['whitelist']
    doro_groups = config.character_detection.doro['whitelist']
    nanniang_groups = config.character_detection.nanniang['whitelist']
    chehui3 = sets["男娘撤回"]
    mute3 = sets["男娘禁言"]
    attack3 = sets["骂男娘"]

    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.pure_text.startswith("/开启奶龙审核 "):
            target_id = event.pure_text.split(" ")[1]
            await operate_group_censor(bot, event, config, target_id, "开启奶龙审核")
        elif event.pure_text.startswith("/关闭奶龙审核 "):
            target_id = event.pure_text.split(" ")[1]
            await operate_group_censor(bot, event, config, target_id, "关闭奶龙审核")
        elif event.pure_text.startswith("/开启doro审核 "):
            target_id = event.pure_text.split(" ")[1]
            await operate_group_censor(bot, event, config, target_id, "开启doro审核")
        elif event.pure_text.startswith("/关闭doro审核 "):
            target_id = event.pure_text.split(" ")[1]
            await operate_group_censor(bot, event, config, target_id, "关闭doro审核")

    async def get_group_member_info(group_id: int, user_id: int):
        url = "http://localhost:3000/get_group_member_info"
        payload = {
            "group_id": group_id,
            "user_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ff',
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    async def is_group_admin(group_id: int, user_id: int) -> bool:
        try:
            member_info = await get_group_member_info(group_id, user_id)
            role = member_info.get('data', {}).get('role', '')
            return role == 'admin' or role == 'owner'
        except Exception as e:
            print(f"An error occurred while checking admin status: {e}")
            return False

    async def url_to_base64(url):
        async with httpx.AsyncClient(timeout=9000) as client:
            response = await client.get(url)
            if response.status_code == 200:
                image_bytes = response.content
                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                return encoded_string
            else:
                raise Exception(f"Failed to retrieve image: {response.status_code}")

    if if_nailong:
        @bot.on(GroupMessageEvent)
        async def get_pic(event):
            if event.group_id in nailong_groups:
                if not event.get("image"):
                    return
                img_url = event.get("image")[0]["url"]
                b64_in = await url_to_base64(img_url)
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as executor:
                    check = await loop.run_in_executor(executor, nailong_main, b64_in)
                if check == 1:
                    if chehui1:
                        # is_group_admin1 = await is_group_admin(event.group_id, bot.qq)
                        try:
                            msg = event.json()
                            event_dict = json.loads(msg)
                            Source_id = event_dict['message_id']
                            await bot.recall(Source_id)
                            if config.ai_llm.config["llm"]["aiReplyCore"]:
                                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                                name = data["data"]["nickname"]
                                system_instruction = await use_folder_chara('喷子.txt')
                                reply = await aiReplyCore([{
                                                               "text": f"系统提示:{name}刚刚发送了一张奶龙的图片,这是一张很唐(愚蠢引人不适)的图，对其进行攻击"}],
                                                          1145141919810, config, system_instruction=system_instruction,
                                                          bot=bot, tools=None)
                                await bot.send(event, reply, True)
                            else:
                                await bot.send(event, random.choice(attack1), True)
                            if mute1:
                                await bot.mute(event.group_id, event.sender.user_id, 60)
                        except:
                            await bot.send(event, random.choice(attack1), True)
                    else:
                        if config.ai_llm.config["llm"]["aiReplyCore"]:
                            system_instruction = await use_folder_chara('喷子.txt')
                            data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                            name = data["data"]["nickname"]
                            reply = await aiReplyCore([{
                                                           "text": f"系统提示:{name}刚刚发送了一张奶龙的图片,这是一张很唐(愚蠢引人不适)的图，对其进行攻击"}],
                                                      1145141919810, config, system_instruction=system_instruction,
                                                      bot=bot, tools=None)
                            await bot.send(event, reply, True)
                        else:
                            await bot.send(event, random.choice(attack1), True)

    if if_doro:
        @bot.on(GroupMessageEvent)
        async def get_pic1(event):
            if event.group_id in doro_groups:
                if not event.get("image"):
                    return
                img_url = event.get("image")[0]["url"]
                b64_in = await url_to_base64(img_url)
                loop = asyncio.get_running_loop()
                # 线程池
                with ThreadPoolExecutor() as executor:
                    check = await loop.run_in_executor(executor, doro_main, b64_in)
                if check == 1:
                    if chehui2:
                        # is_group_admin1 = await is_group_admin(event.group_id, bot.qq)
                        try:
                            msg = event.json()
                            event_dict = json.loads(msg)
                            Source_id = event_dict['message_id']
                            await bot.recall(Source_id)
                            if config.ai_llm.config["llm"]["aiReplyCore"]:
                                system_instruction = await use_folder_chara('喷子.txt')
                                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                                name = data["data"]["nickname"]
                                reply = await aiReplyCore([{
                                                               "text": f"系统提示:{name}刚刚发送了一张doro的图片,这是一张很唐(愚蠢引人不适)的图，对其进行攻击"}],
                                                          1145141919810, config, system_instruction=system_instruction,
                                                          bot=bot, tools=None)
                                await bot.send(event, reply, True)
                            else:
                                await bot.send(event, random.choice(attack2), True)
                            if mute2:
                                await bot.mute(event.group_id, event.sender.user_id, 60)
                        except:
                            await bot.send(event, random.choice(attack2), True)
                    else:
                        if config.ai_llm.config["llm"]["aiReplyCore"]:
                            data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                            name = data["data"]["nickname"]
                            system_instruction = await use_folder_chara('喷子.txt')
                            reply = await aiReplyCore([{
                                                           "text": f"系统提示:{name}刚刚发送了一张doro的图片,这是一张很唐(愚蠢引人不适)的图，对其进行攻击"}],
                                                      1145141919810, config, system_instruction=system_instruction,
                                                      bot=bot, tools=None)
                            await bot.send(event, reply, True)
                        else:
                            await bot.send(event, random.choice(attack2), True)

    @bot.on(GroupMessageEvent)
    async def _(event):
        if if_nanniang or event.user_id == 1270858640:
            if event.group_id in nanniang_groups or event.user_id == 1270858640:
                if not event.get("image"):
                    return
                img_url = event.get("image")[0]["url"]
                b64_in = await url_to_base64(img_url)
                loop = asyncio.get_running_loop()
                # 线程池
                with ThreadPoolExecutor() as executor:
                    check = await loop.run_in_executor(executor, nn_main, b64_in)
                if check == 1:
                    if chehui3:
                        # is_group_admin1 = await is_group_admin(event.group_id, bot.qq)
                        try:
                            msg = event.json()
                            event_dict = json.loads(msg)
                            Source_id = event_dict['message_id']
                            await bot.recall(Source_id)
                            if config.ai_llm.config["llm"]["aiReplyCore"]:
                                data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                                name = data["data"]["nickname"]
                                system_instruction = await use_folder_chara('喷子.txt')
                                reply = await aiReplyCore([{"text": f"系统提示:{name}发了一张男娘图，对其进行攻击"}],
                                                          1145141919810, config, system_instruction=system_instruction,
                                                          bot=bot, tools=None)
                                await bot.send(event, reply, True)
                            else:
                                await bot.send(event, random.choice(attack3), True)
                            if mute3:
                                await bot.mute(event.group_id, event.sender.user_id, 60)
                        except:
                            await bot.send(event, random.choice(attack3), True)
                    else:
                        if config.ai_llm.config["llm"]["aiReplyCore"]:
                            data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
                            name = data["data"]["nickname"]
                            system_instruction = await use_folder_chara('喷子.txt')
                            reply = await aiReplyCore([{"text": f"系统提示:{name}发了一张男娘图，对其进行攻击"}],
                                                      1145141919810, config, system_instruction=system_instruction,
                                                      bot=bot, tools=None)
                            await bot.send(event, reply, True)
                        else:
                            await bot.send(event, random.choice(attack3), True)
