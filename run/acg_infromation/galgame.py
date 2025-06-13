import datetime

import asyncio
from concurrent.futures import ThreadPoolExecutor

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Node, Text, Image
from run.acg_infromation.service.galgame import Get_Access_Token,Get_Access_Token_json,flag_check,params_check,get_game_image, \
    context_assemble, get_introduction
from run.streaming_media.service.Link_parsing.Link_parsing import gal_PILimg

def main(bot,config):
    @bot.on(GroupMessageEvent)
    async def galgame_group_reply(event: GroupMessageEvent):
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, asyncio.run,
                                       galgame_group_check(event))

    async def galgame_group_check(event: GroupMessageEvent):
        #暂定标记状态flag：
        # flag：1，精确游戏查询
        # flag：2，游戏列表查询
        # flag：3，gid 查询单个游戏的详情
        # flag：4，orgId 查询机构详情
        # flag：5，cid 查询角色详情
        # flag：6，orgId 查询机构下的游戏
        # flag：7，查询日期区间内发行的游戏
        # flag：8，随机游戏

        flag =0
        flag_check_test=0
        keyword=str(event.pure_text)
        filepath = 'data/pictures/galgame'
        cmList = []
        forMeslist = []

        if "gal" in str(event.pure_text) or "Gal" in str(event.pure_text):
            #print('text')
            try:
                access_token = await Get_Access_Token()
            except Exception as e:
                bot.logger.error(f"access_token failed: {e}")
                return
            if "查询" in str(event.pure_text):
                keyword = str(event.pure_text)
                index = keyword.find("查询")
                if index != -1:
                    keyword = keyword[index + len("查询") :]
                    if ':' in keyword or ' ' in keyword or '：' in keyword:
                        keyword = keyword[+1:]
                        pass
                flag = 2
                if "精确" in str(event.pure_text):
                    flag = 1
                if "机构" in str(event.pure_text):
                    flag = 4
                    if "游戏" in str(event.pure_text):
                        flag = 6
                        flag_check_test = 3
                elif "id" in str(event.pure_text):
                    flag = 3
                if "角色" in str(event.pure_text):
                    flag = 5
                bot.logger.info(f'access_token：{access_token}，flag:{flag}，gal查询目标：{keyword}')

        if "新作" in str(event.pure_text) :
            now = datetime.datetime.now().date()
            flag=7
            month = datetime.datetime.now().date().month
            year = datetime.datetime.now().date().year
            day = datetime.datetime.now().date().day
            if "本日" in str(event.pure_text) or "今日" in str(event.pure_text) or "今天" in str(event.pure_text):
                flag_check_test=3
                date = datetime.date(year, month, day)
                bot.logger.info(f'本日新作查询')
            elif "昨日" in str(event.pure_text):
                flag_check_test=3
                date = datetime.date(year, month, day - 1)
                bot.logger.info(f'昨日新作查询')
            elif "本月" in str(event.pure_text):
                date = datetime.date(year, month - 1, day)
                flag_check_test = 3
                bot.logger.info(f'本月新作查询')
            else:
                return

        if ("galgame推荐" == str(event.pure_text) or "Galgame推荐" == str(event.pure_text) or "gal推荐" == str(event.pure_text)or "Gal推荐" == str(event.pure_text)
                or ("随机" in str(event.pure_text) and ("gal" in str(event.pure_text) or "Gal" in str(event.pure_text)))):
            flag = 8
            flag_check_test = 3
            bot.logger.info(f'有玩gal的下头男，galgame推荐开启，张数：1')

        if flag ==2:
            print('进行gal列表查询')
            url = flag_check(flag)
            params = params_check(flag, keyword)
            #access_token = Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state=json_check['success']
            #print(state)
            if state:
                total = json_check["data"]["total"]
                #print(total)
                #print(json_check)
                if total > 1:
                    gal_namelist = ''
                    total=int(total)
                    if total >10:
                        total = 10
                    for i in range(total):
                        data = json_check['data']['result'][i]
                        #print(data)
                        name_check = data["name"]
                        print(name_check)
                        if name_check:
                            if "chineseName" in json_check['data']['result'][i]:
                                name_check = data["chineseName"]
                        gal_namelist += f"{name_check} \n"
                    #print(f'存在多个匹配对象，请精确您的查询目标:\n{gal_namelist}')
                    context=f'存在多个匹配对象，请发送 ‘gal精确查询’ 来精确您的查询目标:\n{gal_namelist}'
                    flag_check_test = 1
                elif total == 1:
                    flag = 1
                    data = json_check['data']['result'][0]
                    #print(data)
                    name_check = data["name"]
                    if name_check:
                        if "chineseName" in json_check['data']['result'][0]:
                            name_check = data["chineseName"]
                    #data = json_check['data']['result'][i]
                    keyword=name_check
                    #print(keyword)
            if flag ==1:
                print('进行gal精确查询')
                print(keyword)
                url = flag_check(flag)
                params = params_check(flag, keyword)
                json_check = await Get_Access_Token_json(access_token, url, params)
                #print(json_check)
                state = json_check['success']
                if state:
                    context=await context_assemble(json_check)
                    mainImg_state = json_check["data"]["game"]["mainImg"]
                    img_path = await get_game_image(mainImg_state, filepath)
                    #print(context)
                    pass
            else:
                pass

        elif flag == 1:
            print('进行gal精确查询')
            url = flag_check(flag)
            params = params_check(flag, keyword)
            json_check = await Get_Access_Token_json(access_token, url, params)
            # print(json_check)
            state = json_check['success']
            if state:
                context = await context_assemble(json_check)
                mainImg_state = json_check["data"]["game"]["mainImg"]
                img_path = await get_game_image(mainImg_state, filepath)
                # print(context)
                pass


        elif flag ==3:
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state:
                context = await context_assemble(json_check)
                #print(context)
                mainImg_state = json_check["data"]["game"]["mainImg"]
                img_path = await get_game_image(mainImg_state, filepath)

        elif flag ==4:
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state:
                context = await context_assemble(json_check)
                #print(context)
                if 'mainImg' in json_check["data"]["org"]:
                    mainImg_state = json_check["data"]["org"]["mainImg"]
                    img_path = await get_game_image(mainImg_state, filepath)
                else:
                    state = False

        elif flag ==5:
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state:
                context = await context_assemble(json_check)
                #print(context)
                mainImg_state = json_check["data"]["character"]["mainImg"]
                img_path = await get_game_image(mainImg_state, filepath)

        elif flag ==6:
            url = flag_check(flag)
            params = params_check(flag, keyword)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state:
                data_count = len(json_check["data"])
                if int(data_count) ==0:
                    state = False
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = await context_assemble(data)
                    #print(context)
                    mainImg_state = data["mainImg"]
                    img_path = await get_game_image(mainImg_state, filepath)
                    cmList.append(Node(content=[Image(file=img_path)]))
                    cmList.append(Node(content=[Text(f'{context}')]))
                #print(context)

        elif flag ==7:
            url = flag_check(flag)
            keyword=True
            releaseStartDate = date
            releaseEndDate = now
            params = params_check(flag, keyword,releaseStartDate,releaseEndDate)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            if state:
                data_count = len(json_check["data"])
                if int(data_count) ==0:
                    state = False
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = await context_assemble(data)
                    #print(data)
                    mainImg_state = data["mainImg"]
                    img_path = await get_game_image(mainImg_state, filepath)
                    cmList.append(Node(content=[Image(file=img_path)]))
                    cmList.append(Node(content=[Text(f'{context}')]))
                    if int(data_count) < 4:
                        gid = data["gid"]
                        introduction=await get_introduction(gid)
                        cmList.append(Node(content=[Text(f'{introduction}')]))
                #print(context)

        elif flag ==8:
            url = flag_check(flag)
            params =params_check(flag, keyword)
            access_token = await Get_Access_Token()
            json_check = await Get_Access_Token_json(access_token, url, params)
            #print(json_check)
            state = json_check['success']
            # print(state)
            cmList.append(Node(content=[Text(f'今天的gal推荐，请君过目：')]))
            if state:
                data_count = len(json_check["data"])
                for i in range(data_count):
                    data = json_check['data'][i]
                    context = await context_assemble(data)
                    #print(data)
                    gid=data["gid"]
                    introduction = await get_introduction(gid)
                    mainImg_state = 'https://store.ymgal.games/'+data["mainImg"]
                    if config.acg_infromation.config["绘图框架"]['gal_recommend'] is False:
                        img_path = await get_game_image(mainImg_state, filepath)
                        cmList.append(Node(content=[Image(file=img_path)]))
                        cmList.append(Node(content=[Text(f'{context}')]))
                        cmList.append(Node(content=[Text(f'{introduction}')]))

                    elif config.acg_infromation.config["绘图框架"]['gal_recommend'] is True:
                        text=f"{context}\n{introduction}"
                        bangumi_json = await gal_PILimg(text, [mainImg_state], 'data/pictures/cache/',type_soft=f'Galgame 推荐')
                        if bangumi_json['status']:
                            bot.logger.info('gal推荐图片制作成功，开始推送~~~')
                            await bot.send(event, Image(file=bangumi_json['pic_path']))
                        flag =0


        if flag != 0 :
            #print(context)
            try:
                if state == True:
                    if flag_check_test == 0:
                        bot.logger.info(f'进入文件发送ing')
                        cmList.append(Node(content=[Image(file=img_path)]))
                        cmList.append(Node(content=[Text(f'{context}')]))
                        cmList.append(Node(content=[Text(f'当前菜单：\n1，gal查询\n2，gid_gal单个游戏详情查询\n3，orgId_gal机构详情查询\n4，cid_gal游戏角色详情查询\n5，orgId_gal机构下的游戏查询\n6，本月新作，本日新作（单此一项请艾特bot食用\n7，galgame推荐')]))
                        cmList.append(Node(content=[Text(f'该功能由YMGalgame API实现，支持一下谢谢喵\n本功能由“漫朔”开发\n部分功能还在完善，欢迎催更')]))
                        await bot.send(event, cmList)
                        pass
                    elif flag_check_test == 1:
                        #print(context)
                        await bot.send(event, f'{context}')
                    elif flag_check_test == 3:
                        cmList.append(Node(content=[Text(f'当前菜单：\n1，gal查询\n2，gid_gal单个游戏详情查询\n3，orgId_gal机构详情查询\n4，cid_gal游戏角色详情查询\n5，orgId_gal机构下的游戏查询\n6，本月新作，本日新作（单此一项请艾特bot食用\n7，galgame推荐')]))
                        cmList.append(Node(content=[Text(f'该功能由YMGalgame API实现，支持一下谢谢喵\n本功能由“漫朔”开发\n部分功能还在完善，欢迎催更')]))
                        await bot.send(event, cmList)
                        pass
                else:
                    await bot.send(event, f'好像暂时找不到你说的gal或公司欸~')
            except Exception:
                bot.logger.error("发送失败，未知错误")
                await bot.send(event, f'好像暂时找不到你说的gal或公司欸~')
        pass