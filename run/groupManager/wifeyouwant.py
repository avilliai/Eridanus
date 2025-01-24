import random
import os
import datetime
import aiosqlite
import asyncio
import httpx
import requests
import re
import json
from developTools.event.events import GroupMessageEvent, FriendRequestEvent, PrivateMessageEvent, startUpMetaEvent, \
    ProfileLikeEvent, PokeNotifyEvent
from developTools.message.message_components import Record, Node, Text, Image,At
from plugins.core.aiReplyCore import aiReplyCore
from plugins.core.userDB import update_user, add_user, get_user
from plugins.game_plugin.galgame import get_game_image
from plugins.game_plugin.wife_you_want import manage_group_status,manage_group_add,initialize_db,manage_group_check,PIL_lu_maker,\
    run_async_task,daily_task
from datetime import datetime
from asyncio import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

def main(bot,config):
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
    bot.logger.info(f"今日老婆功能成功加载！")

    @bot.on(GroupMessageEvent)
    async def today_wife(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            if not event.raw_message.startswith("今"):
                return
            if ('今日' in str(event.raw_message) or '今天' in str(event.raw_message) or '今日' in str(
                    event.raw_message)) and '老婆' in str(event.raw_message):
                bot.logger.info("今日老婆开启！")
                today_api = config.api["today_wife"]["api"]
                if '张' in str(event.raw_message) or '个' in str(event.raw_message) or '位' in str(
                        event.raw_message):
                    cmList = []
                    context = str(event.raw_message)
                    name_id_number = re.search(r'\d+', context)
                    if name_id_number:
                        number = int(name_id_number.group())
                        if number > 5:
                            await bot.send(event, '数量过多，渣男！！！！')
                            return
                    for i in range(number):
                        headers = {'Referer': 'https://weibo.com/'}
                        response = requests.get(today_api, headers=headers)
                        with open(f'{filepath}/today_wife_{i}.jpg', 'wb') as file:
                            file.write(response.content)
                        bot.logger.info(f"api获取到第{i+1}个老婆！")
                        cmList.append(Node(content=[Image(file=f'{filepath}/today_wife_{i}.jpg')]))
                    await bot.send(event, cmList)
                    pass
                else:
                    headers = {'Referer': 'https://weibo.com/'}
                    response = requests.get(today_api, headers=headers)
                    #bot.logger.info("今日老婆开启！")
                    with open(f'{filepath}/today_wife.jpg', 'wb') as file:
                        file.write(response.content)
                    img_path = f'{filepath}/today_wife.jpg'
                    await bot.send(event, Image(file=img_path))

    @bot.on(GroupMessageEvent)  # 今日老公
    async def today_husband(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            global filepath
            if str(event.raw_message).startswith("今"):
                if ('今日' in str(event.raw_message) or '今天' in str(event.raw_message) or '今日' in str(
                        event.raw_message)) and '老公' in str(event.raw_message):
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
                        #img_path = await get_game_image(proxy_url, filepath_check)
                        await bot.send(event, [Image(file=proxy_url)])
                    except Exception as e:
                        bot.logger.error(f"Error in today_husband: {e}")
                        await bot.send(event, 'api失效，望君息怒')


    @bot.on(GroupMessageEvent)  # 不知道从哪里找的api对接
    async def api_collect(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            flag = 0
            if '今日一言' in str(event.raw_message) or '答案之书' in str(event.raw_message) or '每日一言' in str(
                    event.raw_message):
                url = 'https://api.dwo.cc/api/yi?api=yan'
                flag = 1
                bot.logger.info("今日一言")
            elif 'emo时刻' in str(event.raw_message) or 'emo了' in str(event.raw_message) or '网抑云' in str(
                    event.raw_message):
                url = 'https://api.dwo.cc/api/yi?api=emo'
                flag = 1
                bot.logger.info("emo时刻")
            elif 'wyy评论' in str(event.raw_message) or '网易云评论' in str(event.raw_message):
                url = 'https://api.dwo.cc/api/yi?api=wyy'
                flag = 1
                bot.logger.info("网易云评论")
            elif '舔狗日记' in str(event.raw_message):
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

        membercheck_id = int(event.sender.user_id)
        if str(event.raw_message).startswith('🦌') or str(event.raw_message) in {'戒🦌'}:
            if membercheck_id in membercheck:
                await bot.send(event,'技能冷却ing')
                bot.logger.info('检测到有人过于勤奋的🦌，跳过')
                return
            else:
                membercheck[membercheck_id] = 1
        else:return
        lu_recall = ['不！给！你！🦌！！！','我靠你怎么这么坏！','再🦌都🦌出火星子了！！','让我来帮你吧~','好恶心啊~~','有变态！！','你这种人渣我才不会喜欢你呢！',
                        '令人害怕的坏叔叔','才不给你计数呢！（哼']
        if str(event.raw_message).startswith('🦌'):
            target_id = int(event.sender.user_id)
            times_add=0
            match = re.search(r"qq=(\d+)", event.raw_message)
            if match:
                target_id = match.group(1)
            else:
                for context in str(event.raw_message):
                    if context != '🦌':
                        membercheck.pop(membercheck_id)
                        return
            flag = random.randint(0, 50)
            if flag <= 8:
                await bot.send(event, lu_recall[random.randint(0, len(lu_recall) - 1)])
                membercheck.pop(membercheck_id)
                return
            bot.logger.info(f'yes! 🦌!!!!, 目标：{target_id}')

            if await manage_group_status('lu_limit', f'lu_others', target_id) == 1 and int(target_id) !=int(event.sender.user_id):#贞操锁
                await bot.send(event, [At(qq=target_id), f' 是个好孩子，才不会给你呢~'])
                membercheck.pop(membercheck_id)
                return

            for context in str(event.raw_message):
                if context =='🦌':
                    times_add +=1

            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            await manage_group_status(current_day, current_year_month, target_id,1)

            times=await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id)
            await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id,times+times_add)

            if await PIL_lu_maker(current_date,target_id):
                bot.logger.info('制作成功，开始发送~~')
                if int(times + times_add) in {0,1} :
                    times_record = int(await manage_group_status('lu_record', f'lu_others', target_id)) + 1
                    await manage_group_status('lu_record', f'lu_others', target_id, times_record)
                    await bot.send(event,[At(qq=target_id), f' 今天🦌了！', Image(file='data/pictures/wife_you_want_img/lulululu.png')])
                else:
                    await bot.send(event, [At(qq=target_id), f' 今天🦌了{times+times_add}次！',
                                           Image(file='data/pictures/wife_you_want_img/lulululu.png')])

        elif '戒🦌' == str(event.raw_message):
            bot.logger.info('No! 戒🦌!!!!')
            target_id = int(event.sender.user_id)
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            await manage_group_status(current_day, current_year_month, target_id,2)
            times = await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id)
            await manage_group_status('lu', f'{current_year}_{current_month}_{current_day}', target_id, times + 1)

            if await PIL_lu_maker(current_date,target_id):
                bot.logger.info('制作成功，开始发送~~')
                await bot.send(event,[At(qq=target_id), f' 今天戒🦌了！', Image(file='data/pictures/wife_you_want_img/lulululu.png')])

        elif '补🦌' == str(event.raw_message):
            bot.logger.info('yes! 补🦌!!!!')
            target_id = int(event.sender.user_id)
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            current_year_month = f'{current_year}_{current_month}'
            current_day = current_date.day
            membercheck.pop(membercheck_id)
            try:
                times_record = int(await manage_group_status('lu_record', f'lu_others', target_id))
                times_record_check=times_record//3
                if times_record_check == 0:
                    await bot.send(event, [At(qq=target_id), f' 您的补🦌次数好像不够呢喵~~（已连续{times_record}天）'])
                else:
                    for i in range(current_day):
                        day=current_day-i
                        if int(await manage_group_status(day, current_year_month, target_id)) not in {1,2}:
                            await manage_group_status(day, current_year_month, target_id, 1)
                            await manage_group_status('lu_record', f'lu_others', target_id,times_record-3)
                            await PIL_lu_maker(current_date, target_id)
                            await bot.send(event, [At(qq=target_id), f' 您已成功补🦌！', Image(file='data/pictures/wife_you_want_img/lulululu.png')])
                            break
            except Exception as e:
                await bot.send(event, [At(qq=target_id), f' 补🦌失败了喵~'])

        elif '开启贞操锁' == str(event.raw_message):
            target_id = int(event.sender.user_id)
            await manage_group_status('lu_limit', f'lu_others', target_id,1)
            membercheck.pop(membercheck_id)
            await bot.send(event,'您已开启贞操锁~')
        elif '关闭贞操锁' == str(event.raw_message):
            target_id = int(event.sender.user_id)
            await manage_group_status('lu_limit', f'lu_others', target_id,0)
            membercheck.pop(membercheck_id)
            await bot.send(event,'您已关闭贞操锁~')

        else:
            if membercheck_id in membercheck:
                membercheck.pop(membercheck_id)

        if membercheck_id in membercheck:
            await sleep(10)
            if membercheck_id in membercheck:
                membercheck.pop(membercheck_id)

    @bot.on(GroupMessageEvent)  # 今日腿子
    async def today_husband(event: GroupMessageEvent):
        async with httpx.AsyncClient() as client:
            if str(event.raw_message).startswith("今"):
                if '今日' in str(event.raw_message) or '今天' in str(event.raw_message) or '今日' in str(event.raw_message):
                    global filepath
                    url=None
                    if '腿' in str(event.raw_message):
                        bot.logger.info("今日腿子开启！")
                        url='https://api.dwo.cc/api/meizi'
                    elif '黑' in str(event.raw_message):
                        bot.logger.info("今日黑丝开启！")
                        url='https://api.dwo.cc/api/hs_img'
                    elif '白' in str(event.raw_message):
                        bot.logger.info("今日白丝开启！")
                        url='https://api.dwo.cc/api/bs_img'
                    elif '头像' in str(event.raw_message):
                        bot.logger.info("今日头像开启！")
                        url='https://api.dwo.cc/api/dmtou'
                    if url is None:return
                    try:
                        response = requests.get(url)
                        img_path = f'{filepath}/today_api_check.jpg'
                        with open(img_path, 'wb') as file:
                            file.write(response.content)
                        await bot.send(event,[Image(file=img_path)])
                    except Exception:
                        await bot.send(event, 'api失效了喵，请过一段时间再试试吧')

    @bot.on(GroupMessageEvent)  # 透群友合集
    async def wife_you_want(event: GroupMessageEvent):
        async with (aiosqlite.connect("data/dataBase/wifeyouwant.db") as db):
            global filepath
            wifePrefix=config.api["today_wife"]["wifePrefix"]
            if (f'{wifePrefix}' in str(event.raw_message)):  # 前置触发词
                target_id_aim = None
                flag_persona = 0
                flag_aim = 0
                target_name=None
                from_id = int(event.sender.user_id)
                target_group = int(event.group_id)
                if ('透群主' in str(event.raw_message)):
                    flag_persona = 1
                    check = 'owner'
                elif ('透管理' in str(event.raw_message)):
                    flag_persona = 2
                    check = 'admin'
                elif ('透群友' in str(event.raw_message)):
                    flag_persona = 3
                    pass
                elif ('娶群友' in str(event.raw_message)):
                    flag_persona = 4

                    if await manage_group_status(from_id,target_group,'wife_you_get') != 0:
                        target_id_aim = await manage_group_status(from_id,target_group,'wife_you_get')
                        flag_aim = 1
                    else:
                        flag_aim = 0
                    pass
                elif ('离婚' in str(event.raw_message)):
                    if await manage_group_status(from_id,target_group,'wife_you_get') != 0:
                        await manage_group_status(from_id, target_group, 'wife_you_get',0)
                        await bot.send(event, '离婚啦，您现在是单身贵族咯~')
                else:
                    flag_persona = 0

                if flag_persona == 3 or flag_persona == 4 or "透" in str(event.raw_message) or "娶" in str(event.raw_message):
                    context = str(event.raw_message)
                    if not ("管理" in str(event.raw_message) or "群主" in str(event.raw_message)):
                        name_id_number=None
                        name_id_number_1=None
                        name_id_number_2 = None
                        name_id_number = re.search(r'\d+', context)
                        if name_id_number is not None:
                            name_id_number_2=0
                        if "群友" not in str(event.raw_message):
                            if "透" in str(event.raw_message) :
                                index = context.find("透")
                                if index != -1:
                                    context_check = context[index + len("透"):]
                            elif "娶" in str(event.raw_message):
                                index = context.find("娶")
                                if index != -1:
                                    context_check = context[index + len("娶"):]
                            #print(context_check)
                            friendlist_get = await bot.get_group_member_list(event.group_id)

                            for friend in friendlist_get["data"]:
                                if context_check in friend['nickname'] or context_check in friend['card']:
                                    #print(friend)
                                    name_id_number_1=friend['user_id']
                                    name_id_number_2=0
                                    if "透" in str(event.raw_message):
                                        flag_persona = 3
                                    elif "娶" in str(event.raw_message):
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
                                else:number=name_id_number_1
                                target_id_aim = number
                                #print(target_id_aim)
                                rnum1 = random.randint(1, 20)
                                if rnum1 > 3:
                                    # await bot.send(event, '不许瑟瑟！！！！', True)
                                    target_group = int(event.group_id)
                                    #print(target_group,target_id_aim)
                                    group_member_check = await bot.get_group_member_info(target_group, target_id_aim)
                                    #print(group_member_check)
                                    if group_member_check['status'] == 'ok':
                                        flag_aim = 1
                            # print(rnum1)
                            # print(flag_aim)

                        rnum0 = random.randint(1, 20)
                        if rnum0 == 1:
                            await bot.send(event, '不许瑟瑟！！！！')
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

                        for friend in data["data"]:
                            #print(friend)
                            data_test = None
                            data_check = friend['role']
                            # print(data_check)
                            if flag_persona == 1 or flag_persona == 2:
                                if data_check == check:
                                    data_test = friend['user_id']
                            elif flag_persona == 3 or flag_persona == 4:
                                data_test = friend['user_id']
                            if data_test != None:
                                friendlist.append(data_test)
                            if flag_persona == 1:
                                if data_check == 'owner':
                                    data_check_number = 1
                                if data_check_number == 1:
                                    break
                        #print(friendlist)
                        number_target = len(friendlist)
                        target_number = random.randint(1, number_target)
                        target_id = friendlist[target_number - 1]
                    if flag_aim == 0 and flag_persona == 1:
                        await manage_group_status(from_id, target_group, 'group_owner')
                        #await manage_group_status(f"{target_group}_owner", target_id)
                    #print(target_id)
                    bot.logger.info(f'群：{target_group}，透群友目标：{target_id}')
                    group_member_check = await bot.get_group_member_info(target_group, target_id)
                    # print(group_member_check)
                    # target_id = extract_between_symbols(str(group_member_check), 'id=', ' member')
                    if await manage_group_status(from_id,target_group,'wife_you_get') != 0 and flag_persona == 4:
                        target_name = await manage_group_status(from_id,target_group,'wife_you_get')
                    else:
                        target_name = group_member_check['data']['nickname']
                        # target_name = extract_between_symbols(str(group_member_check), 'member_name=', ' permission')
                    if flag_persona == 4:
                        if await manage_group_status(from_id,target_group,'wife_you_get') != 0:
                            flag_aim = 0
                        else:
                            await manage_group_status(from_id, target_group, 'wife_you_get',target_id)


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
                        if await manage_group_status(target_id,target_group,'group_owner') != 0:
                            times = int(await manage_group_status(target_id,target_group,'group_owner'))
                            times += 1
                            await manage_group_status(target_id,target_group,'group_owner',times)
                        else:
                            times=1
                            await manage_group_status(target_id,target_group,'group_owner',times)
                        await bot.send(event,
                                                     [f'@{from_name} 恭喜你涩到群主！！！！',
                                                      Image(file=target_img_path),
                                                      f'群主【{target_name}】今天这是第{times}次被透了呢'])
                    elif flag_persona == 2:
                        await bot.send(event,
                                                     [f'@{from_name} 恭喜你涩到管理！！！！',
                                                      Image(file=target_img_path),
                                                      f'【{target_name}】 ({target_id})哒！'])
                    elif flag_persona == 3:
                        if flag_aim == 1:
                            await bot.send(event,
                                                         [f'@{from_name} 恭喜你涩到了群友！！！！',
                                                          Image(file=target_img_path),
                                                          f'【{target_name}】 ({target_id})哒！'])
                        else:
                            await bot.send(event,
                                                         [f'@{from_name} 今天你的色色对象是',
                                                          Image(file=target_img_path),
                                                          f'【{target_name}】 ({target_id})哒！'])
                    elif flag_persona == 4:
                        if flag_aim == 1:
                            await bot.send(event,[f'@{from_name} 恭喜你娶到了群友！！！！',
                                                Image(file=target_img_path),
                                                 f'【{target_name}】 ({target_id})哒！'])
                        else:
                            await bot.send(event,[f'@{from_name} 今天你的结婚对象是',
                                                Image(file=target_img_path),
                                                f'【{target_name}】 ({target_id})哒！'])

                if flag_persona != 0 and target_name is not None:
                    await manage_group_add(from_id, target_id, target_group)

                if '记录' in str(event.raw_message) and (
                        '色色' in str(event.raw_message) or '瑟瑟' in str(event.raw_message) or '涩涩' in str(
                    event.raw_message)):
                    bot.logger.info(f'色色记录启动！')
                    cmList = []
                    if '本周' in str(event.raw_message) or '每周' in str(event.raw_message) or '星期' in str(
                            event.raw_message):
                        type_context = '以下是本周色色记录：'
                        type='week'
                    elif '本月' in str(event.raw_message) or '月份' in str(event.raw_message) or '月' in str(
                            event.raw_message):
                        type = 'month'
                        type_context = '以下是本月色色记录：'
                    elif '年' in str(event.raw_message) :
                        type = 'Year'
                        type_context = '以下是年度色色记录：'
                    else:
                        type_context = '以下是本日色色记录：'
                        type = 'day'
                    list_from, list_target = await manage_group_check(target_group, type)
                    #print(list_from, list_target)
                    if list_from==None or list_target==None:
                        await bot.send(event, f'本群好像还没有一个人开过趴捏~')
                        return
                    friendlist_get = await bot.get_group_member_list(event.group_id)
                    context_from='以下是透别人的次数~\n'
                    context_target = '以下是被别人透的次数~\n'
                    for i in range(len(list_from)):
                        for member in friendlist_get['data']:
                            if list_from[0][0] == str(member['user_id']):
                                from_king_name=member['nickname']
                            if list_from[i][0] == str(member['user_id']):
                                context_from+=f'{member["nickname"]} ({member["user_id"]}): {list_from[i][1]} 次\n'
                    for i in range(len(list_target)):
                        for member in friendlist_get['data']:
                            if list_target[0][0] == str(member['user_id']):
                                target_king_name=member['nickname']
                            if list_target[i][0] == str(member['user_id']):
                                context_target+=f'{member["nickname"]} ({member["user_id"]}): {list_target[i][1]} 次\n'

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
