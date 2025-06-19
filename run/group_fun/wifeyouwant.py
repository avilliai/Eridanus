import asyncio
import datetime
import os
import random
import re
import threading
from asyncio import sleep
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import aiosqlite
import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Node, Text, Image, At
from run.group_fun.service.wife_you_want import manage_group_status, manage_group_add, initialize_db, \
    manage_group_check, PIL_lu_maker, \
    run_async_task, today_check_api, query_group_users, add_or_update_user_collect


def queue_check_wait(bot, config):
    global url_activate, queue_check
    url_activate = False

    @bot.on(LifecycleMetaEvent)
    async def _(event):
        global url_activate
        if not url_activate:
            url_activate = True

            loop = asyncio.get_running_loop()
            while True:
                # bot.logger.info("开始写入")
                try:
                    with ThreadPoolExecutor() as executor:
                        await loop.run_in_executor(executor, asyncio.run, queue_check_wait_make(bot, config))
                    # await check_bili_dynamic(bot,config)
                except Exception as e:
                    bot.logger.error(f'wife_you_want数据库出错，可以考虑关掉热门群友以解决此报错：{e}')
                await asyncio.sleep(600)  # 哈哈
        else:
            pass
            bot.logger.error(f'上一次写入时长过长，请酌情考虑')


async def queue_check_wait_make(bot, config):
    # print("LifecycleMetaEvent")
    global queue_check
    queue_check_make = []
    while queue_check:
        # print('queue_check', queue_check)
        from_id, target_group, target_team, value = queue_check.popleft()
        if target_team == 'group_owner_record':
            queue_check_make.append(
                (from_id, target_group, f'{datetime.now().year}_{datetime.now().month}_{datetime.now().day}', value))
        queue_check_make.append((from_id, target_group, target_team, value))

    if queue_check_make:
        await add_or_update_user_collect(queue_check_make)
        # await manage_group_status(from_id, target_group, target_team, value)
        # print(f"Updated {from_id}, {target_group},  {target_team} to {value}")


def main(bot, config):
    global last_messages
    last_messages = {}
    global filepath
    filepath = 'data/pictures/wife_you_want_img'
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    asyncio.run(initialize_db())
    global membercheck
    membercheck = {}
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_async_task, trigger=CronTrigger(hour=0, minute=0))
    scheduler.start()
    today_wife_api, header = config.group_fun.config["today_wife"]["api"], config.group_fun.config["today_wife"][
        "header"]
    global queue_check
    queue_check = deque()

    threading.Thread(target=queue_check_wait(bot, config), daemon=True).start()

    @bot.on(GroupMessageEvent)
    async def today_wife(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            global num_check, today_api
            if not event.pure_text.startswith("今"):
                return
            if ('今日' in str(event.pure_text) or '今天' in str(event.pure_text) or '今日' in str(
                    event.pure_text)) and '老婆' in str(event.pure_text):
                bot.logger.info("今日老婆开启！")
                if '张' in str(event.pure_text) or '个' in str(event.pure_text) or '位' in str(
                        event.pure_text):
                    cmList = []
                    context = str(event.pure_text)
                    name_id_number = re.search(r'\d+', context)
                    if name_id_number:
                        number = int(name_id_number.group())
                        if number > 5:
                            await bot.send(event, '数量过多，渣男！！！！')
                            return
                    for i in range(number):
                        response = today_check_api(today_wife_api, header)
                        with open(f'{filepath}/today_wife_{i}.jpg', 'wb') as file:
                            file.write(response.content)
                        bot.logger.info(f"api获取到第{i + 1}个老婆！")
                        cmList.append(Node(content=[Image(file=f'{filepath}/today_wife_{i}.jpg')]))
                    await bot.send(event, cmList)
                    pass
                else:
                    response = today_check_api(today_wife_api, header)
                    # bot.logger.info("今日老婆开启！")
                    with open(f'{filepath}/today_wife.jpg', 'wb') as file:
                        file.write(response.content)
                    img_path = f'{filepath}/today_wife.jpg'
                    await bot.send(event, Image(file=img_path))

    @bot.on(GroupMessageEvent)  # 今日老公
    async def today_husband(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            global filepath
            if str(event.pure_text).startswith("今"):
                if ('今日' in str(event.pure_text) or '今天' in str(event.pure_text) or '今日' in str(
                        event.pure_text)) and '老公' in str(event.pure_text):
                    bot.logger.info("今日老公开启！")
                    params = {
                        "format": "json",
                        "num": '1',
                        'tag': '男子'
                    }
                    url = 'https://api.hikarinagi.com/random/v2/?'
                    # url="https://api.hikarinagi.com/random/v2/?tag=原神&num=1&r-18=false"
                    try:
                        response = await client.get(url, params=params)
                        data = response.json()
                        url = data[0]['url']
                        proxy_url = url.replace("https://i.pximg.net/", "https://i.yuki.sh/")
                        bot.logger.info(f"搜索成功，作品pid：{data[0]['pid']}，反代url：{proxy_url}")
                        # img_path = await get_game_image(proxy_url, filepath_check)
                        await bot.send(event, [Image(file=proxy_url)])
                    except Exception as e:
                        bot.logger.error(f"Error in today_husband: {e}")
                        await bot.send(event, 'api失效，望君息怒')

    @bot.on(GroupMessageEvent)  # 今日萝莉
    async def today_luoli(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            global filepath
            if str(event.pure_text).startswith("今"):
                if ('今日' in str(event.pure_text) or '今天' in str(event.pure_text) or '今日' in str(
                        event.pure_text)) and '萝莉' in str(event.pure_text):
                    bot.logger.info("今日萝莉开启！")
                    params = {
                        "format": "json",
                        "num": '1',
                        'tag': 'ロリ'
                    }
                    url = 'https://api.hikarinagi.com/random/v2/?'
                    try:
                        response = await client.get(url, params=params)
                        data = response.json()
                        url = data[0]['url']
                        proxy_url = url.replace("https://i.pximg.net/", "https://i.yuki.sh/")
                        bot.logger.info(f"搜索成功，作品pid：{data[0]['pid']}，反代url：{proxy_url}")
                        # img_path = await get_game_image(proxy_url, filepath_check)
                        await bot.send(event, [Image(file=proxy_url)])
                    except Exception as e:
                        bot.logger.error(f"Error in today_husband: {e}")
                        await bot.send(event, 'api失效，望君息怒')

    @bot.on(GroupMessageEvent)  # 不知道从哪里找的api对接
    async def api_collect(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            flag = 0
            if '今日一言' == str(event.pure_text) or '答案之书' == str(event.pure_text) or '每日一言' == str(
                    event.pure_text):
                url = 'https://api.dwo.cc/api/yi?api=yan'
                flag = 1
                bot.logger.info("今日一言")
            elif 'emo时刻' == str(event.pure_text) or 'emo了' == str(event.pure_text) or '网抑云' == str(
                    event.pure_text):
                url = 'https://api.dwo.cc/api/yi?api=emo'
                flag = 1
                bot.logger.info("emo时刻")
            elif 'wyy评论' == str(event.pure_text) or '网易云评论' == str(event.pure_text):
                url = 'https://api.dwo.cc/api/yi?api=wyy'
                flag = 1
                bot.logger.info("网易云评论")
            elif '舔狗日记' == str(event.pure_text):
                url = 'https://api.dwo.cc/api/dog'
                flag = 1
                bot.logger.info("舔狗日记")
            try:
                if flag == 1:
                    response = await client.get(url)
                    context = str(response.text)
                elif flag == 2:
                    response = await client.get(url)
                    # print(response.text)
                    data = response.json()
                    context = data['数据']['content']
            except Exception:
                await bot.send(event, 'api出错了喵')
                flag = 0
                return

            if flag != 0:
                await bot.send(event, context)

    @bot.on(GroupMessageEvent)  # 开卢
    async def today_LU(event: GroupMessageEvent):
        global membercheck
        context = event.pure_text
        if context == '':
            context = event.raw_message
        membercheck_id = int(event.sender.user_id)
        if context.startswith('🦌') or context in {'戒🦌', '补🦌', '开启贞操锁', '关闭贞操锁'}:
            if membercheck_id in membercheck:
                if context in {'补🦌'}:
                    membercheck.pop(membercheck_id)
                else:
                    await bot.send(event, '技能冷却ing')
                    bot.logger.info('检测到有人过于勤奋的🦌，跳过')
                    if membercheck_id in membercheck:
                        membercheck.pop(membercheck_id)
                    return
            else:
                membercheck[membercheck_id] = 1
        else:
            return

        lu_recall = ['不！给！你！🦌！！！', '我靠你怎么这么坏！', '再🦌都🦌出火星子了！！', '让我来帮你吧~', '好恶心啊~~',
                     '有变态！！', '你这种人渣我才不会喜欢你呢！',
                     '令人害怕的坏叔叔', '才不给你计数呢！（哼', '杂鱼杂鱼', '杂鱼哥哥还是处男呢',
                     '哥哥怎么还在这呀，好可怜']
        if context.startswith('🦌'):
            target_id = int(event.sender.user_id)
            times_add = 0
            match = re.search(r"qq=(\d+)", context)
            if match:
                target_id = match.group(1)
            else:
                for context_check in context:
                    if context_check != '🦌':
                        membercheck.pop(membercheck_id)
                        return
            flag = random.randint(0, 100)
            if flag <= 8:
                await bot.send(event, lu_recall[random.randint(0, len(lu_recall) - 1)])
                membercheck.pop(membercheck_id)
                return
            bot.logger.info(f'yes! 🦌!!!!, 目标：{target_id}')

            if await manage_group_status('lu_limit', f'lu_others', target_id) == 1 and int(target_id) != int(
                    event.sender.user_id):  # 贞操锁
                await bot.send(event, [At(qq=target_id), f' 是个好孩子，才不会给你呢~'])
                membercheck.pop(membercheck_id)
                return
            # print('检测是否有贞操锁')
            for context_check in context:
                if context_check == '🦌':
                    times_add += 1

            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            await manage_group_status(current_day, current_year_month, target_id, 1)
            # print('设置🦌状态')
            times = await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id)
            await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id,
                                      times + times_add)
            # print('设置🦌次数')
            bot.logger.info(f'进入图片制作')
            img_url = await PIL_lu_maker(current_date, target_id)

            if img_url:
                bot.logger.info('制作成功，开始发送~~')
                if int(times + times_add) in {0, 1}:
                    times_record = int(await manage_group_status('lu_record', f'lu_others', target_id)) + 1
                    await manage_group_status('lu_record', f'lu_others', target_id, times_record)
                    recall_id = await bot.send(event, [At(qq=target_id), f' 今天🦌了！', Image(file=img_url)])
                else:
                    recall_id = await bot.send(event, [At(qq=target_id), f' 今天🦌了{times + times_add}次！',
                                                       Image(file=img_url)])
                if config.group_fun.config["today_wife"]["签🦌撤回"] is True:
                    await sleep(20)
                    await bot.recall(recall_id['data']['message_id'])

        elif '戒🦌' == context:
            bot.logger.info('No! 戒🦌!!!!')
            target_id = int(event.sender.user_id)
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            await manage_group_status(current_day, current_year_month, target_id, 2)
            times = await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id)
            await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id, times + 1)
            img_url = await PIL_lu_maker(current_date, target_id)
            if img_url:
                bot.logger.info('制作成功，开始发送~~')
                await bot.send(event, [At(qq=target_id), f' 今天戒🦌了！', Image(file=img_url)])

        elif '补🦌' == context:
            bot.logger.info('yes! 补🦌!!!!')
            target_id = int(event.sender.user_id)
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            if membercheck_id in membercheck:
                membercheck.pop(membercheck_id)
            try:
                times_record = int(await manage_group_status('lu_record', f'lu_others', target_id))
                times_record_check = times_record // 3
                if times_record_check == 0:
                    await bot.send(event, [At(qq=target_id), f' 您的补🦌次数好像不够呢喵~~（已连续{times_record}天）'])
                else:
                    for i in range(current_day):
                        day = current_day - i
                        if int(await manage_group_status(day, current_year_month, target_id)) not in {1, 2}:
                            await manage_group_status(day, current_year_month, target_id, 1)
                            await manage_group_status('lu_record', f'lu_others', target_id, times_record - 3)
                            img_url = await PIL_lu_maker(current_date, target_id)

                            await bot.send(event, [At(qq=target_id), f' 您已成功补🦌！', Image(file=img_url)])
                            break
            except Exception as e:
                await bot.send(event, [At(qq=target_id), f' 补🦌失败了喵~'])

        elif '开启贞操锁' == context:
            target_id = int(event.sender.user_id)
            await manage_group_status('lu_limit', f'lu_others', target_id, 1)
            membercheck.pop(membercheck_id)
            await bot.send(event, '您已开启贞操锁~')
        elif '关闭贞操锁' == context:
            target_id = int(event.sender.user_id)
            await manage_group_status('lu_limit', f'lu_others', target_id, 0)
            membercheck.pop(membercheck_id)
            await bot.send(event, '您已关闭贞操锁~')

        else:
            if membercheck_id in membercheck:
                membercheck.pop(membercheck_id)

        if membercheck_id in membercheck:
            await sleep(5)
            if membercheck_id in membercheck:
                membercheck.pop(membercheck_id)

    @bot.on(GroupMessageEvent)  # 透群友合集
    async def today_group_owner(event: GroupMessageEvent):
        flag_aim = 0
        flag_persona = 0
        target_id = None
        if event.message_chain.has(At):
            try:
                if '今日群友' in event.processed_message[0]['text']:
                    target_id = event.message_chain.get(At)[0].qq
                    flag_persona = 3
            except Exception as e:
                pass
        elif '今日群主' == str(event.pure_text):
            flag_persona = 1
            check = 'owner'
        elif '今日管理' == str(event.pure_text):
            flag_persona = 2
            check = 'admin'
        elif '今日群友' == str(event.pure_text):
            flag_persona = 3
            # check = 'owner'


        else:
            flag_persona = 0
        if flag_persona != 0:
            bot.logger.info("今日群主or群友任务开启")
            friendlist = []
            target_group = int(event.group_id)
            if target_id is None:
                friendlist_get = await bot.get_group_member_list(event.group_id)
                data_count = len(friendlist_get["data"])
                if flag_persona == 2 or flag_persona == 3 or flag_persona == 4 or flag_persona == 5:
                    if data_count > 500:
                        await bot.send(event, '抱歉，群聊人数过多，bot服务压力过大，仅开放今日群主功能，谢谢')
                        return
                for friend in friendlist_get["data"]:
                    data_test = None
                    data_check = friend['role']
                    if flag_persona == 1 or flag_persona == 2 or flag_persona == 5:
                        if data_check == check: data_test = friend['user_id']
                    elif flag_persona == 3 or flag_persona == 4:
                        data_test = friend['user_id']
                    if data_test is not None: friendlist.append(data_test)
                    if flag_persona == 1 or flag_persona == 5:
                        if data_check == 'owner': break
                target_id = friendlist[random.randint(1, len(friendlist)) - 1]

            target_name = (await bot.get_group_member_info(target_group, target_id))['data']['nickname']
            # print(target_name,target_id)
            if flag_persona != 0:
                today_wife_api, header = config.group_fun.config["today_wife"]["api"], \
                config.group_fun.config["today_wife"]["header"]
                response = today_check_api(today_wife_api, header)
                img_path = f'data/pictures/wife_you_want_img/today_wife.jpg'
                with open(img_path, 'wb') as file:
                    file.write(response.content)
                if config.group_fun.config["today_wife"]["is_at"]:
                    await bot.send_group_message(target_group, [f'这里是今天的 ', At(qq=target_id), f' 哟~~~\n',
                                                                Image(file=img_path)])
                else:
                    await bot.send(event, [f'这里是今天的 {target_name} 哟~~~\n', Image(file=img_path)])

    @bot.on(GroupMessageEvent)  # 透群友合集
    async def wife_you_want(event: GroupMessageEvent):
        async with (aiosqlite.connect("data/dataBase/wifeyouwant.db") as db):
            friendlist_check_count = 0
            friendlist = []
            if 'group_check' == event.pure_text:
                target_group = int(event.group_id)
                friendlist_check = await query_group_users('group_owner_record', target_group)
                for friendlist_check_member in friendlist_check:
                    friendlist_check_count += 1
                    if friendlist_check_count > 50: break
                    friendlist.append(friendlist_check_member[0])
                queue_check.append((1270858640, 674822468, 'group_owner_record', 20))
                # print('queue_check', queue_check)
                for friend in friendlist:
                    # print(friend)
                    pass
                # print(len(friendlist))
                # await bot.send(event, friendlist)

    @bot.on(GroupMessageEvent)  # 透群友合集
    async def wife_you_want(event: GroupMessageEvent):
        async with (aiosqlite.connect("data/dataBase/wifeyouwant.db") as db):
            global filepath
            wifePrefix = config.group_fun.config["today_wife"]["wifePrefix"]

            if config.group_fun.config["today_wife"]["透热门群友"] is True:
                target_group = int(event.group_id)
                from_id = int(event.sender.user_id)
                if await manage_group_status(from_id, target_group, 'group_owner_record') != 0:
                    target_data = None
                    for item in queue_check:
                        if str(item[0]) == str(from_id):
                            target_data = item
                            break
                    if target_data is not None and str(target_data[1]) == str(target_group):
                        times = target_data[3]
                        # print(f'times:{times}')
                        # print(f'times:{times}, target_data:{target_data[1]},target_group:{target_group}')
                        queue_check.remove(target_data)
                    else:
                        try:
                            times = int(await manage_group_status(from_id, target_group, 'group_owner_record'))
                        except:
                            pass  # 大朔老师啥时候有空了加个缓存
                    times += 1
                    queue_check.append((from_id, target_group, 'group_owner_record', times))
                    # await manage_group_status(from_id, target_group, 'group_owner_record', times)
                else:

                    times = 1
                    queue_check.append((from_id, target_group, 'group_owner_record', times))
                    # await manage_group_status(from_id, target_group, 'group_owner_record', times)

            context = event.pure_text
            if context == '':
                context = event.raw_message
            if f'{wifePrefix}' in context:  # 前置触发词
                target_id_aim = None
                flag_persona = 0
                flag_aim = 0
                target_name = None
                from_id = int(event.sender.user_id)
                target_group = int(event.group_id)

                if '透群主' in context:
                    flag_persona = 1
                    check = 'owner'
                elif '透管理' in context:
                    flag_persona = 2
                    check = 'admin'
                elif '透群友' in context:
                    flag_persona = 3
                    pass
                elif '娶群友' in context:
                    flag_persona = 4
                    if await manage_group_status(from_id, target_group, 'wife_you_get') != 0:
                        target_id_aim = await manage_group_status(from_id, target_group, 'wife_you_get')
                        flag_aim = 1
                    else:
                        flag_aim = 0
                    pass
                elif '离婚' in context:
                    if await manage_group_status(from_id, target_group, 'wife_you_get') != 0:
                        await manage_group_status(from_id, target_group, 'wife_you_get', 0)
                        await bot.send(event, '离婚啦，您现在是单身贵族咯~')
                elif '/今日群主' == context:
                    flag_persona = 5
                    check = 'owner'
                else:
                    flag_persona = 0

                if flag_persona == 3 or flag_persona == 4 or "透" in context or "娶" in context:
                    if not ("管理" in context or "群主" in context):
                        name_id_number = None
                        name_id_number_1 = None
                        name_id_number_2 = None
                        name_id_number = re.search(r'\d+', context)
                        if name_id_number is not None:
                            name_id_number_2 = 0
                        if "群友" not in context:
                            if "透" in context:
                                index = context.find("透")
                                if index != -1:
                                    context_check = context[index + len("透"):]
                            elif "娶" in context:
                                index = context.find("娶")
                                if index != -1:
                                    context_check = context[index + len("娶"):]
                            # print(context_check)
                            friendlist_get = await bot.get_group_member_list(event.group_id)

                            for friend in friendlist_get["data"]:
                                if context_check in friend['nickname'] or context_check in friend['card']:
                                    # print(friend)
                                    name_id_number_1 = friend['user_id']
                                    name_id_number_2 = 0
                                    if "透" in context:
                                        flag_persona = 3
                                    elif "娶" in context:
                                        flag_persona = 4
                                    break

                        if name_id_number_2 is not None:
                            if flag_aim == 1:
                                await bot.send(event, '渣男！吃着碗里的想着锅里的！', True)
                                flag_persona = 0
                                flag_aim = 0
                            else:
                                if name_id_number_1 is None:
                                    number = int(name_id_number.group())
                                else:
                                    number = name_id_number_1
                                target_id_aim = number
                                # print(target_id_aim)
                                rnum1 = random.randint(1, 20)
                                if rnum1 > 3:
                                    # await bot.send(event, '不许瑟瑟！！！！', True)
                                    target_group = int(event.group_id)
                                    # print(target_group,target_id_aim)
                                    group_member_check = await bot.get_group_member_info(target_group, target_id_aim)
                                    # print(group_member_check)
                                    if group_member_check['status'] == 'ok':
                                        flag_aim = 1
                            # print(rnum1)
                            # print(flag_aim)

                        if random.randint(1, 20) == 1:
                            lu_recall = ['不许瑟瑟！！！！', '你是坏蛋！！', '色色是不允许的！', '不给！', '笨蛋哥哥',
                                         '为什么不是我？', '看着我啊，我才不帮你呢！'
                                , '逃跑喵']
                            await bot.send(event, lu_recall[random.randint(0, len(lu_recall) - 1)])
                            # await bot.send(event, '不许瑟瑟！！！！')
                            flag_persona = 0

                if flag_persona != 0:
                    bot.logger.info("透群友任务开启")
                    friendlist = []
                    target_name = None
                    target_id = None
                    target_img = None
                    # target_nikenamne=None
                    from_name = str(event.sender.nickname)
                    from_id = int(event.sender.user_id)
                    # flag_aim = 0
                    target_group = int(event.group_id)

                    if flag_aim == 1:
                        target_id = target_id_aim
                    else:
                        friendlist_get = await bot.get_group_member_list(event.group_id)
                        data = friendlist_get
                        # data = json.loads(data)
                        # print(data)
                        data_count = len(friendlist_get["data"])
                        if flag_persona == 2 or flag_persona == 3 or flag_persona == 4:
                            if data_count > 500:
                                await bot.send(event, '抱歉，群聊人数过多，bot服务压力过大，仅开放/透群主功能，谢谢')
                                return
                        data_check_number = 0
                        try:
                            friendlist_check_count = 0
                            if config.group_fun.config["today_wife"]["透热门群友"] is True and flag_persona not in [2,
                                                                                                                    1]:
                                friendlist_check = await query_group_users('group_owner_record', target_group)
                                for friendlist_check_member in friendlist_check:
                                    friendlist_check_count += 1
                                    if friendlist_check_count > 50: break
                                    friendlist.append(friendlist_check_member[0])

                        except Exception:
                            bot.logger.error('透热门群友列表加载出错，执行全局随机')

                        if not friendlist:
                            for friend in data["data"]:
                                # print(friend)
                                data_test = None
                                data_check = friend['role']
                                # print(data_check)
                                if flag_persona == 1 or flag_persona == 2 or flag_persona == 5:
                                    if data_check == check:
                                        data_test = friend['user_id']
                                elif flag_persona == 3 or flag_persona == 4:
                                    data_test = friend['user_id']
                                if data_test is not None:
                                    friendlist.append(data_test)
                                if flag_persona == 1 or flag_persona == 5:
                                    if data_check == 'owner': break
                        # print(friendlist)

                        number_target = len(friendlist)
                        target_number = random.randint(1, number_target)
                        target_id = friendlist[target_number - 1]
                    if flag_aim == 0 and flag_persona == 1:
                        await manage_group_status(from_id, target_group, 'group_owner')
                        # await manage_group_status(f"{target_group}_owner", target_id)
                    # print(target_id)
                    bot.logger.info(f'群：{target_group}，透群友目标：{target_id}')
                    group_member_check = await bot.get_group_member_info(target_group, target_id)
                    # print(group_member_check)
                    # target_id = extract_between_symbols(str(group_member_check), 'id=', ' member')
                    if await manage_group_status(from_id, target_group, 'wife_you_get') != 0 and flag_persona == 4:
                        target_name = await manage_group_status(from_id, target_group, 'wife_you_get')
                    else:
                        target_name = group_member_check['data']['nickname']
                        # target_name = extract_between_symbols(str(group_member_check), 'member_name=', ' permission')
                    if flag_persona == 4:
                        if await manage_group_status(from_id, target_group, 'wife_you_get') != 0:
                            flag_aim = 0
                        else:
                            await manage_group_status(from_id, target_group, 'wife_you_get', target_id)

                    # 下面是获取对应人员头像的代码
                    target_img_url = f"https://q1.qlogo.cn/g?b=qq&nk={target_id}&s=640"  # QQ头像 URL 格式
                    try:
                        target_img_path = target_img_url
                    except Exception:
                        await bot.send(event, '(˃ ⌑ ˂ഃ )诶呀——腾子请求限制，请再试一次吧')
                        return
                    from_name = str(from_name)
                    target_name = str(target_name)

                    if flag_persona == 1:
                        if await manage_group_status(target_id, target_group, 'group_owner') != 0:
                            times = int(await manage_group_status(target_id, target_group, 'group_owner'))
                            times += 1
                            await manage_group_status(target_id, target_group, 'group_owner', times)
                        else:
                            times = 1
                            await manage_group_status(target_id, target_group, 'group_owner', times)
                        recall_id = await bot.send(event,
                                                   [f'@{from_name} 恭喜你涩到群主！！！！',
                                                    Image(file=target_img_path),
                                                    f'群主【{target_name}】今天这是第{times}次被透了呢'])
                    elif flag_persona == 2:
                        recall_id = await bot.send(event,
                                                   [f'@{from_name} 恭喜你涩到管理！！！！',
                                                    Image(file=target_img_path),
                                                    f'【{target_name}】 ({target_id})哒！'])
                    elif flag_persona == 3:
                        if flag_aim == 1:
                            recall_id = await bot.send(event,
                                                       [f'@{from_name} 恭喜你涩到了群友！！！！',
                                                        Image(file=target_img_path),
                                                        f'【{target_name}】 ({target_id})哒！'])
                        else:
                            recall_id = await bot.send(event,
                                                       [f'@{from_name} 今天你的色色对象是',
                                                        Image(file=target_img_path),
                                                        f'【{target_name}】 ({target_id})哒！'])
                    elif flag_persona == 4:
                        if flag_aim == 1:
                            recall_id = await bot.send(event, [f'@{from_name} 恭喜你娶到了群友！！！！',
                                                               Image(file=target_img_path),
                                                               f'【{target_name}】 ({target_id})哒！'])
                        else:
                            recall_id = await bot.send(event, [f'@{from_name} 今天你的结婚对象是',
                                                               Image(file=target_img_path),
                                                               f'【{target_name}】 ({target_id})哒！'])

                    elif flag_persona == 5:
                        today_wife_api, header = config.group_fun.config["today_wife"]["api"], \
                        config.group_fun.config["today_wife"]["header"]
                        response = today_check_api(today_wife_api, header)
                        img_path = f'data/pictures/wife_you_want_img/today_wife.jpg'
                        with open(img_path, 'wb') as file:
                            file.write(response.content)
                        await bot.send(event, [f'这里是今天的{target_name}哟~~~\n', Image(file=img_path)])

                    if config.group_fun.config["today_wife"]["透群友撤回"] is True:
                        try:
                            await sleep(20)
                            await bot.recall(recall_id['data']['message_id'])
                        except Exception:
                            pass

                if flag_persona != 0 and target_name is not None:
                    await manage_group_add(from_id, target_id, target_group)

                if '记录' in str(event.pure_text) and (
                        '色色' in str(event.pure_text) or '瑟瑟' in str(event.pure_text) or '涩涩' in str(
                    event.pure_text)):
                    bot.logger.info(f'色色记录启动！')
                    cmList = []
                    if '本周' in str(event.pure_text) or '每周' in str(event.pure_text) or '星期' in str(
                            event.pure_text):
                        type_context = '以下是本周色色记录：'
                        type = 'week'
                    elif '本月' in str(event.pure_text) or '月份' in str(event.pure_text) or '月' in str(
                            event.pure_text):
                        type = 'month'
                        type_context = '以下是本月色色记录：'
                    elif '年' in str(event.pure_text):
                        type = 'Year'
                        type_context = '以下是年度色色记录：'
                    else:
                        type_context = '以下是本日色色记录：'
                        type = 'day'
                    list_from, list_target = await manage_group_check(target_group, type)
                    # print(list_from, list_target)
                    if list_from is None or list_target is None:
                        await bot.send(event, f'本群好像还没有一个人开过趴捏~')
                        return
                    friendlist_get = await bot.get_group_member_list(event.group_id)
                    context_from = '以下是透别人的次数~\n'
                    context_target = '以下是被别人透的次数~\n'
                    for i in range(len(list_from)):
                        for member in friendlist_get['data']:
                            if list_from[0][0] == str(member['user_id']):
                                from_king_name = member['nickname']
                            if list_from[i][0] == str(member['user_id']):
                                context_from += f'{member["nickname"]} ({member["user_id"]}): {list_from[i][1]} 次\n'
                    for i in range(len(list_target)):
                        for member in friendlist_get['data']:
                            if list_target[0][0] == str(member['user_id']):
                                target_king_name = member['nickname']
                            if list_target[i][0] == str(member['user_id']):
                                context_target += f'{member["nickname"]} ({member["user_id"]}): {list_target[i][1]} 次\n'

                    cmList.append(Node(content=[Text(f'{type_context}')]))

                    cmList.append(Node(content=[Text('透群友最多的人诞生了！！'),
                                                Image(file=f"https://q1.qlogo.cn/g?b=qq&nk={list_from[0][0]}&s=640"),
                                                Text(f'是【{from_king_name}】 ({list_from[0][0]})哦~')]))
                    cmList.append(Node(content=[Text(f'{context_from}')]))

                    cmList.append(Node(content=[Text('被群友透最多的人诞生了！！'),
                                                Image(file=f"https://q1.qlogo.cn/g?b=qq&nk={list_target[0][0]}&s=640"),
                                                Text(f'是【{target_king_name}】 ({list_target[0][0]})哦~')]))
                    cmList.append(Node(content=[Text(f'{context_target}')]))

                    await bot.send(event, cmList)

    @bot.on(GroupMessageEvent)  # 复读程序
    async def fudu(event: GroupMessageEvent):
        global last_messages
        if config.group_fun.config["today_wife"]["复读开关"] is not True:
            return
        Read_check = ['[', '@', '来点', '随机', '#', '今日', 'gal', '查询', '搜索', '/', '瓶子', '什么', 'minfo', 'id',
                      '管理', 'mai', '更新', '今', '日记', '看', '赞我', '随机', '本周', 'b50', '分数列表', '完成表',
                      '🦌']
        group1 = f'{event.group_id}_1'
        group2 = f'{event.group_id}_2'
        group3 = f'{event.group_id}_3'
        message = str(event.pure_text)
        if message == '':
            return
        flag = None
        if group1 not in last_messages:
            last_messages[group1] = None
        if group2 not in last_messages:
            last_messages[group2] = None
        if group3 not in last_messages:
            last_messages[group3] = None

        fudu1 = last_messages[group1]
        fudu2 = last_messages[group2]
        fudu3 = last_messages[group3]
        for i in range(len(Read_check)):
            if str(Read_check[i]) in str(event.pure_text):
                return
        fudu1 = message
        last_messages[group1] = message
        if fudu1 != fudu3:
            if fudu1 == fudu2:
                rnum0 = random.randint(1, 100)
                if rnum0 < 30:
                    bot.logger.info(f"复读触发群：{event.group_id}，复读内容：{message}")
                    await bot.send(event, str(message))
                    last_messages[group3] = message
        last_messages[group2] = message
        # print(last_messages)
