import asyncio
import datetime
import os
import sys
import traceback
from asyncio import sleep

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Text, Image
from run.acg_infromation.service.bangumisearch import banguimiList, bangumisearch, screenshot_to_pdf_and_png, \
    run_async_task, daily_task
from run.streaming_media.service.Link_parsing.Link_parsing import bangumi_PILimg

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def call_bangumi_search(bot, event, config, keywords, cat):
    try:
        dic = {"番剧": 'all', "动画": 2, "书籍": 1, "游戏": 4, "音乐": 3, "三次元": 6}
        url = f"https://bgm.tv/subject_search/{keywords}?cat={dic[cat]}"
        resu = await bangumisearch(url)
        subjectlist = resu[1]
        crtlist = resu[2]
        order = 1
        if str(event.pure_text).startswith("0") and order <= len(crtlist):
            crt = crtlist[order - 1].find("a")["href"]
            url = "https://bgm.tv" + crt
            bot.logger.info("正在获取" + crt + "详情")
            path = f"data/pictures/cache/search-{keywords}-0{order}.png"
            title = crtlist[order - 1].find("a").string
        elif 1 <= order <= len(subjectlist):
            subject = subjectlist[order - 1].find("a")["href"]
            url = "https://bgm.tv" + subject
            bot.logger.info("正在获取" + subject + "详情")
            path = f"data/pictures/cache/search-{keywords}-{order}.png"
            title = subjectlist[order - 1].find("a").string
        else:
            await bot.send(event, "查询失败！不规范的操作")
            searchtask.pop(event.sender.user_id)
            return
        try:
            bot.logger.info("正在获取" + title + "详情")
            await screenshot_to_pdf_and_png(url, path, 1080, 1750)
            await bot.send(event, [Text(f'查询结果：{title}'), Image(file=path)])
        except Exception as e:
            bot.logger.error(e)
            await bot.send(event, "查询失败，重新试试？")

    except Exception as e:
        bot.logger.error(e)
        await bot.send(event, "查询失败，重新试试？")


async def call_remen(bot, event, config):
    pass


def main(bot, config):
    searchtask = {}
    switch = 0
    recall_id = None
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_async_task, trigger=CronTrigger(hour=0, minute=1))
    scheduler.start()

    @bot.on(GroupMessageEvent)
    async def bangumi_search(event: GroupMessageEvent):
        context = event.pure_text
        if ("本季" in context or "季度" in context or "top" in context or "排行" in context or "本月" in context) and (
                "新番" in context or "番剧" in context or "动画" in context or "bangumi" in context):
            now = datetime.datetime.now()
            # 根据月份判断当前季度的第一个月
            if now.month in [1, 2, 3]:
                month = 1  # 第一季度的第一个月是1月
            elif now.month in [4, 5, 6]:
                month = 4  # 第二季度的第一个月是4月
            elif now.month in [7, 8, 9]:
                month = 7  # 第三季度的第一个月是7月
            else:
                month = 10  # 第四季度的第一个月是10月
            year = datetime.datetime.now().strftime("%Y")
        else:
            return
        try:
            if "top" in context:
                top = int(context.split("top")[1])  # 获取top参数
            elif "排行" in context:
                top = int(context.split("排行")[1])
            else:
                top = 20
        except:
            top = 24

        try:
            finalT, finalC, isbottom = await banguimiList(year, month, top)
            # print(finalT, finalC, isbottom)
            if finalT == [] or finalC == [] or isbottom == 0:
                month_check = int(month) - 1
                finalT, finalC, isbottom = await banguimiList(year, month_check, top)
            # print(finalT, finalC, isbottom)
            title = f'{year}年{month}月 | Bangumi 番组计划\n'
            if year == "":
                title = "| Bangumi 番组计划\n"
            if month == "":
                title = title.replace("月", "")
            bottom = "到底啦~"
            combined_list = []
            rank = 1
            # print(len(finalT))
            times = len(finalT) // 10
            if len(finalT) % 10 != 0:
                times += 1
            text = ''
            cmList = []
            total_text_check = ''
            for i in range(times):
                combined_str = ""
                if i == 0:
                    combined_str += "title,"
                for j in range(10):  # 10个一组发送消息
                    combined_str += f"Image(url=finalC[{rank - 1}],cache=True),finalT[{rank - 1}]"
                    rank += 1
                    if i * 10 + j + 1 == len(finalT):
                        break
                    if j != 9:
                        combined_str += ","
                if isbottom:
                    combined_str += ",bottom"
                count_check = 0
                for title, cover in zip(finalT, finalC[:len(finalT)]):
                    # display(Image(url=cover, cache=True))  # 显示图片
                    if title in total_text_check: continue
                    total_text_check += title
                    count_check += 1
                    words = title.split("\n")  # 按换行符分割文本，逐行处理
                    title_check = ''
                    line_flag = 0
                    for line in words:  # 遍历每一行（处理换行符的部分）
                        if line_flag == 0 or line_flag == 3:
                            if line_flag == 0: line_flag = 1
                            continue
                        title_check += f'{line}'
                        if '评分' not in line:
                            title_check += f'----'
                        else:
                            line_flag = 3
                    text += f'{count_check}、{title_check}\n'
                    cmList.append(cover)
            text = text.replace(' ', '')
            bot.logger.info("获取番剧排行成功")
            bangumi_json = await bangumi_PILimg(text, cmList, 'data/pictures/cache/',
                                                type_soft=f'bangumi {month}月新番', name=f'bangumi {month}月新番')
            if bangumi_json['status']:
                bot.logger.info('番剧排行图片制作成功，开始推送~~~')
                await bot.send(event, Image(file=bangumi_json['pic_path']))
            # await bot.send(event, cmList)
        except Exception as e:
            bot.logger.error(e)
            traceback.print_exc()
            await bot.send(event, "获取番剧信息失败，请稍后再试")

    @bot.on(GroupMessageEvent)
    async def bangumi_search_week(event: GroupMessageEvent):
        context = event.pure_text
        if ("今日" in context) and (
                "新番" in context or "番剧" in context or "动画" in context or "bangumi" in context or "放送" in context):
            weekday = datetime.datetime.today().weekday()
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            # print(f'bangumi 周{weekdays[weekday]}放送')
            bangumi_json = await bangumi_PILimg(filepath='data/pictures/cache/',
                                                type_soft=f'bangumi 周{weekdays[weekday]}放送',
                                                name=f'bangumi 周{weekdays[weekday]}放送', type='calendar')
            # print(json.dumps(bangumi_json, indent=4))
            if bangumi_json['status']:
                bot.logger.info('今日番剧图片制作成功，开始推送~~~')
                await bot.send(event,
                               [f'bangumi 周{weekdays[weekday]}番剧放送！！', Image(file=bangumi_json['pic_path'])])

    @bot.on(GroupMessageEvent)
    async def bangumi_search(event: GroupMessageEvent):
        botname = config.common_config.basic_config["bot"]
        context = event.pure_text
        if not event.pure_text.startswith(config.acg_infromation.config["acg_information"]["bangumi_query_prefix"]):
            return
        if "bangumi查询" in context:
            # url="https://api.bgm.tv/search/subject/"+str(event.message_chain).split(" ")[1]
            search_type = None
            keywords = context.replace(" ", "").split("查询")[1]
        elif "查询动画" in context or "查询番剧" in context or "番剧查询" in context:
            search_type = 2
            if context.startswith("查询"):
                if '动画' in context:
                    keywords = context.replace(" ", "").split("动画")[1]
                elif '番剧' in context:
                    keywords = context.replace(" ", "").split("番剧")[1]
            else:
                keywords = context.replace(" ", "").split("查询")[1]
        elif "查询书籍" in context or "书籍查询" in context:
            search_type = 1
            if context.startswith("查询"):
                keywords = context.replace(" ", "").split("书籍")[1]
            else:
                keywords = context.replace(" ", "").split("查询")[1]
        elif "查询游戏" in context or "游戏查询" in context:
            search_type = 4
            if context.startswith("查询"):
                keywords = context.replace(" ", "").split("游戏")[1]
            else:
                keywords = context.replace(" ", "").split("查询")[1]
        elif "查询音乐" in context or "音乐查询" in context:
            search_type = 3
            if context.startswith("查询"):
                keywords = context.replace(" ", "").split("音乐")[1]
            else:
                keywords = context.replace(" ", "").split("查询")[1]
        elif "查询三次元" in context or "三次元查询" in context:
            search_type = 6
            if context.startswith("查询"):
                keywords = context.replace(" ", "").split("三次元")[1]
            else:
                keywords = context.replace(" ", "").split("查询")[1]
        else:
            return
        bot.logger.info("正在查询：" + keywords)

        nonlocal searchtask, recall_id, switch  # 变量提前，否则可能未定义
        try:
            bangumi_json = await bangumi_PILimg(filepath='data/pictures/cache/',
                                                type_soft=f'bangumi 查询', type='search', target=keywords,
                                                search_type=search_type)
            if bangumi_json['status']:
                bot.logger.info('bangumi搜索成功，开始推送~~~')
                if bangumi_json['next_choice'] is True:
                    searchtask[event.sender.user_id] = bangumi_json['choice_contents']
                    switch = 1
                    recall_id = await bot.send(event, [f"请发送编号进入详情页，或发送退出退出查询",
                                                       Image(file=bangumi_json['pic_path'])])

                elif bangumi_json['next_choice'] is False:
                    await bot.send(event, [f"这是{botname}为您查询到的结果～～", Image(file=bangumi_json['pic_path'])])
                    if event.sender.user_id in searchtask:
                        searchtask.pop(event.sender.user_id)
            else:
                await bot.send(event, f"{botname}没有找到该番剧呢～")
        except Exception as e:
            bot.logger.error(e)
            if event.sender.user_id in searchtask:
                searchtask.pop(event.sender.user_id)
            await bot.send(event, "查询失败，请稍后再试")

    @bot.on(GroupMessageEvent)
    async def bangumi_search_detail(event: GroupMessageEvent):
        nonlocal searchtask, recall_id
        botname = config.common_config.basic_config["bot"]
        if event.sender.user_id in searchtask:
            try:
                if str(event.pure_text) == "退出":
                    searchtask.pop(event.sender.user_id)
                    await bot.recall(recall_id['data']['message_id'])
                    await bot.send(event, "已退出查询")
                    return
                bangumi_json_choice = searchtask[event.sender.user_id]

                order = int(str(event.pure_text))
                searchtask.pop(event.sender.user_id)
                await bot.recall(recall_id['data']['message_id'])
                recall_id = await bot.send(event, "正在获取，请稍后~~~")

                if 1 <= order <= len(bangumi_json_choice):
                    subject_id = bangumi_json_choice[order]
                else:
                    await bot.send(event, "查询失败喵～")
                    searchtask.pop(event.sender.user_id)
                    return

                try:
                    bangumi_json = await bangumi_PILimg(filepath='data/pictures/cache/', type_soft=f'bangumi 查询',
                                                        type='search_accurate', target=subject_id)
                    if bangumi_json['status']:
                        bot.logger.info('bangumi搜索成功，开始推送~~~')
                        await bot.send(event,
                                       [f"这是{botname}为您查询到的结果～～", Image(file=bangumi_json['pic_path'])])
                except Exception as e:
                    bot.logger.error(e)
                    await bot.send(event, "查询失败喵，请稍后再试喵～")
                try:
                    searchtask.pop(event.sender.user_id)
                except Exception as e:
                    bot.logger.error(e)
                    pass
            except Exception as e:
                bot.logger.error(e)
                if event.sender.user_id in searchtask:
                    searchtask.pop(event.sender.user_id)
                await bot.send(event, "查询失败喵，请输入正确的数字喵")
            await bot.recall(recall_id['data']['message_id'])

    @bot.on(GroupMessageEvent)
    async def bangumi_search_timeout(event: GroupMessageEvent):
        nonlocal searchtask
        nonlocal switch
        if event.sender.user_id in searchtask:
            if switch:
                switch = 0  # 保证只发送一次超时提示
                await sleep(60 * 3)
                if event.sender.user_id in searchtask:  # 检验查询是否结束
                    searchtask.pop(event.sender.user_id)
                    await bot.send(event, "查询超时喵～")

    @bot.on(GroupMessageEvent)
    async def Bilibili_today_hot(event: GroupMessageEvent):
        file_path = 'data/pictures/wife_you_want_img/'
        output_path = f'{file_path}bili_today_hot_back_out.png'
        if '今日热门' == event.pure_text:
            if not os.path.isfile(output_path):
                await daily_task()
            bot.logger.info('今日热门开启！！！')
            await bot.send(event, Image(file=output_path))
