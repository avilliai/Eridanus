import asyncio
import random
import shutil
from concurrent.futures.thread import ThreadPoolExecutor

from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image, Node, Text, File, Card
from developTools.utils.logger import get_logger
from framework_common.database_util.User import get_user
from framework_common.framework_util.yamlLoader import YAMLManager
from run.resource_collector.service.asmr.asmr100 import random_asmr_100, latest_asmr_100, choose_from_latest_asmr_100, \
    choose_from_hotest_asmr_100
from run.resource_collector.service.jmComic.jmComic import JM_search, JM_search_week, JM_search_comic_id, downloadComic, \
    downloadALLAndToPdf
from run.resource_collector.service.zLibrary.zLib import search_book, download_book
from run.resource_collector.service.zLibrary.zLibrary import Zlibrary
from framework_common.utils.random_str import random_str
from framework_common.utils.utils import download_file, merge_audio_files, download_img

logger=get_logger()
module_config=YAMLManager.get_instance()
proxy = module_config.common_config.basic_config["proxy"]["http_proxy"]
if proxy != "":
    proxies = {
        "http": proxy,
        "https": proxy
    }
else:
    proxies = None
if module_config.resource_collector.config["z_library"]["email"] != "" and module_config.resource_collector.config["z_library"][
    "password"] != "":
    global Z
    try:
        Z = Zlibrary(email=module_config.resource_collector.config["z_library"]["email"],
                     password=module_config.resource_collector.config["z_library"]["password"], proxies=proxies)
        logger.info("✅ z_library 登陆成功")
    except Exception as e:
        logger.error(f"❌ z_library login error:{e}")

global operating
operating = {}  #jm文件共享的维护列表

async def search_book_info(bot,event,config,info):
    global Z
    user_info = await get_user(event.user_id)
    if user_info.permission >= config.resource_collector.config["z_library"]["search_operate_level"]:

        await bot.send(event, "正在搜索中，请稍候...")
        result = search_book(Z, info, config.resource_collector.config["z_library"]["search_num"])
        forward_list = []
        for r in result:
            forward_list.append(Node(content=[Text(r[0]), Image(file=r[1])]))
        print(forward_list)
        await bot.send(event, forward_list)
        # await bot.send(event,Image(file=p)])
        # print(r)
    else:
        await bot.send(event, "你没有权限使用该功能")
async def call_download_book(bot,event,config,book_id: str,hash:str):
    global Z
    user_info = await get_user(event.user_id)
    if user_info.permission >= config.resource_collector.config["z_library"]["download_operate_level"]:
        await bot.send(event, "正在下载中，请稍候...")
        loop = asyncio.get_running_loop()
        try:
            with ThreadPoolExecutor() as executor:
                path = await loop.run_in_executor(executor,download_book,Z,book_id.strip(),hash.strip())
            await bot.send(event, File(file=path))
            await bot.send(event, "下载成功，请查看文件",True)
        except Exception as e:
            bot.logger.error(f"download_book error:{e}")
            await bot.send(event, "下载失败，请稍后再试",True)
    else:
        await bot.send(event, "你没有权限使用该功能")

async def call_asmr(bot,event,config,try_again=False,mode="random"):
    user_info = await get_user(event.user_id)
    if user_info.permission >= config.resource_collector.config["asmr"]["asmr_level"]:
        bot.logger.info("asmr start")
        try:
            if mode=="random":
                r=await random_asmr_100(proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            elif mode=="latest":
                r=await choose_from_latest_asmr_100(proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            elif mode=="hotest":
                r = await choose_from_hotest_asmr_100(proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            i = random.choice(r['media_urls'])

            await bot.send(event, Card(audio=i[0], title=i[1], image=r['mainCoverUrl']))
            try:
                img=await download_img(r['mainCoverUrl'],f"data/pictures/cache/{random_str()}.png",config.resource_collector.config["asmr"]["gray_layer"],proxy=config.common_config.basic_config["proxy"]["http_proxy"])
            except Exception as e:
                bot.logger.error(f"download_img error:{e}")
                img=r['mainCoverUrl']
            forward_list = []
            if config.resource_collector.config["asmr"]["with_url"]:
                forward_list.append(Node(content=[Text(f"随机asmr\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"), Image(file=img)]))
            else:
                await bot.send(event,[Text(f"随机asmr\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"), Image(file=img)])
            file_paths=[]
            main_path = f"data/voice/cache/{r['title']}.{r['media_urls'][0][1].split('.')[-1]}"

            metype = r['media_urls'][0][1].split('.')[-1]

            for i in r['media_urls']:
                if i[1].split('.')[-1] != metype or len(file_paths) >= config.resource_collector.config["asmr"]["max_merge_file_num"]:
                    bot.logger.error(f"audio type change:{i[1]}")
                    break
                if config.resource_collector.config["asmr"]["with_file"]:
                    path=f"data/voice/cache/{i[1]}"
                    file=await download_file(i[0],path,config.common_config.basic_config["proxy"]["http_proxy"])
                    file_paths.append(file)
                text=f"音频名称: {i[1]}\n音频url: {i[0]}"
                forward_list.append(Node(content=[Text(text)]))
            if config.resource_collector.config["asmr"]["with_url"]:
                await bot.send(event, forward_list)
            if config.resource_collector.config["asmr"]["with_file"]:
                loop = asyncio.get_running_loop()
                try:
                    await bot.send(event, "正在合并音频文件，请等待完成...")
                    bot.logger.info(f"asmr file merge and upload start: path:{main_path},merge_files:{file_paths}")
                    with ThreadPoolExecutor() as executor:
                        path = await loop.run_in_executor(executor, merge_audio_files, file_paths, main_path)
                    await bot.send(event, File(file=path))
                except Exception as e:
                    bot.logger.error(f"asmr file merge and upload error:{e}")

        except Exception as e:
            bot.logger.error(f"asmr error:{e}")
            if try_again==False:
                bot.logger.warning("asmr try again!")
                await call_asmr(bot,event,config,try_again=True)
            if try_again==True:
                await bot.send(event, "失败了！要不再试一次？")
    else:
        await bot.send(event, "你没有权限使用该功能")

async def check_latest_asmr(bot,event,config):
    bot.logger.info_func("开始监测 asmr.one 更新")
    try:
        r=await latest_asmr_100(proxy=config.common_config.basic_config["proxy"]["http_proxy"])
        if r["id"]!=config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["latest_asmr_id"]:
            bot.logger.info_func(f"最新asmr id:{r['id']} {r['title']} 开始推送")
            group_list = config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["groups"]
            for group_id in group_list:
                try:
                    i = random.choice(r['media_urls'])
                    await bot.send_group_message(group_id, Card(audio=i[0], title=i[1], image=r['mainCoverUrl']))
                    try:
                        img = await download_img(r['mainCoverUrl'], f"data/pictures/cache/{random_str()}.png", config.resource_collector.config["asmr"]["gray_layer"],
                                                 proxy=config.common_config.basic_config["proxy"]["http_proxy"])
                    except Exception as e:
                        bot.logger.error(f"download_img error:{e}")
                        img = r['mainCoverUrl']
                    forward_list = []
                    if config.resource_collector.config["asmr"]["with_url"]:
                        forward_list.append(Node(
                            content=[Text(f"asmr更新啦\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"),
                                     Image(file=img)]))
                    else:
                        await bot.send_group_message(group_id,
                                       [Text(f"asmr更新啦\n标题: {r['title']}\nnsfw: {r['nsfw']}\n源: {r['source_url']}"),
                                        Image(file=img)])
                    file_paths = []
                    main_path = f"data/voice/cache/{r['title']}.{r['media_urls'][0][1].split('.')[-1]}"
                    for i in r['media_urls']:
                        if config.resource_collector.config["asmr"]["with_file"]:
                            path = f"data/voice/cache/{i[1]}"
                            file = await download_file(i[0], path, config.common_config.basic_config["proxy"]["http_proxy"])
                            file_paths.append(file)
                        text = f"音频名称: {i[1]}\n音频url: {i[0]}"
                        forward_list.append(Node(content=[Text(text)]))
                    if config.resource_collector.config["asmr"]["with_url"]:
                        await bot.send_group_message(group_id, forward_list)
                    if config.resource_collector.config["asmr"]["with_file"]:
                        loop = asyncio.get_running_loop()
                        try:
                            bot.logger.info(
                                f"asmr file merge and upload start: path:{main_path},merge_files:{file_paths}")
                            with ThreadPoolExecutor() as executor:
                                path = await loop.run_in_executor(executor, merge_audio_files, file_paths, main_path)
                            await bot.send_group_message(group_id, File(file=path))
                            await bot.send_group_message(group_id, "完整音频文件已上传", True)
                        except Exception as e:
                            bot.logger.error(f"asmr file merge and upload error:{e}")
                except Exception as e:
                    bot.logger.error(f"latest_asmr_push error:{e}")
            bot.logger.info_func(f"最新asmr id:{r['id']} {r['title']} 推送完成")
            config.scheduled_tasks.sheduled_tasks_push_groups_ordinary["nightASMR"]["latest_asmr_id"]=r["id"]
            config.save_yaml("sheduled_tasks_push_groups_ordinary",plugin_name="scheduled_tasks")
        else:
            bot.logger.info_func("asmr.one 无更新")
    except Exception as e:
        bot.logger.error(f"check_latest_asmr error:{e}")
async def call_jm(bot,event,config,mode="preview",comic_id=607279,serach_topic=None):
    async def _call_jm():
        global operating
        if mode=="preview":

            if hasattr(event, "group_id"):
                temp_id = event.group_id
            else:
                temp_id = event.user_id
            if comic_id in operating:
                if event.group_id not in operating[comic_id]:
                    operating[comic_id].append(event.group_id)
                    await bot.send(event, "相关文件占用中，请等待...", True)
                else:
                    await bot.send(event, "已有相关文件占用，请稍等", True)
                return
            event.group_id = temp_id
            operating[comic_id] = [event.group_id]
            bot.logger.info(f"JM验车 {comic_id}")
            await bot.send(event, "下载中...稍等喵", True)
            try:
                loop = asyncio.get_running_loop()
                # 使用线程池执行器
                with ThreadPoolExecutor() as executor:
                    # 使用 asyncio.to_thread 调用函数并获取返回结果
                    png_files = await loop.run_in_executor(executor, downloadComic, comic_id, 1,
                                                           config.resource_collector.config["JMComic"]["previewPages"],config.resource_collector.config["JMComic"]["anti_nsfw"],config.resource_collector.config["JMComic"]["gif_compress"])
            except Exception as e:
                bot.logger.error(e)
                await bot.send(event, "下载失败", True)
                operating.pop(comic_id)
                return
            cmList = []
            bot.logger.info(png_files)
            cmList.append(Node(content=[Text(
                f"车牌号：{comic_id} \nbot仅提供本子部分页面预览。\n图片已经过处理，但不保证百分百不被吞。预览是黑色是正常的，点进去查看")]))
            shutil.rmtree(f"data/pictures/benzi/temp{comic_id}")

            for path in png_files:
                cmList.append(Node(content=[Image(file=path)]))
            for group_id in operating[comic_id]:
                event.group_id = group_id
                await bot.send(event, cmList)
            operating.pop(comic_id)
        elif mode=="download":
            if hasattr(event, "group_id"):
                temp_id = event.group_id
            else:
                temp_id = event.user_id
            if comic_id in operating:
                if temp_id not in operating[comic_id]:
                    operating[comic_id].append(temp_id)
                    await bot.send(event, "相关文件占用中，请等待...", True)
                else:
                    await bot.send(event, "本群已有相关文件占用，请稍等", True)
                return
            operating[comic_id] = [temp_id]
            try:
                await bot.send(event, "已启用线程,请等待下载完成", True)
                loop = asyncio.get_running_loop()
                with ThreadPoolExecutor() as executor:
                    r = await loop.run_in_executor(executor, downloadALLAndToPdf, comic_id,
                                                   config.resource_collector.config["JMComic"]["savePath"])
                bot.logger.info(f"下载完成，车牌号：{comic_id} \n保存路径：{config.resource_collector.config['JMComic']['savePath']} {comic_id} ")
            except Exception as e:
                bot.logger.error(e)
                await bot.send(event, "下载失败", True)
            finally:
                try:
                    shutil.rmtree(f"{config.resource_collector.config['JMComic']['savePath']}/{comic_id}")
                    for group_id in operating[comic_id]:
                        event.group_id = group_id  # 修改数据实现切换群聊，懒狗实现
                        await bot.send(event, File(file=f"{config.resource_collector.config['JMComic']['savePath']}/{comic_id}.pdf"))
                        await bot.send(event, "下载完成了( >ρ< ”)。请等待上传完成。", True)

                    bot.logger.info("移除预览缓存")
                    operating.pop(comic_id)
                    if config.resource_collector.config['JMComic']["autoClearPDF"]:
                        await wait_and_delete_file(bot,file_path=f"{config.resource_collector.config['JMComic']['savePath']}/{comic_id}.pdf")
                except Exception as e:
                    bot.logger.error(e)
                finally:
                    if comic_id in operating:
                        operating.pop(comic_id)
        elif mode=="search":
            bot.logger.info(f"JM搜索: {serach_topic}")
            try:
                context = JM_search(serach_topic)
                if context == "":
                    await bot.send(event, "好像没有找到你说的本子呢~~~")
                    return {"status": "failed", "message": "没有找到相关本子"}
                r = Node(content=[Text(context)])
                await bot.send(event, r)
            except Exception as e:
                bot.logger.error(e)
                await bot.send(event, "搜索失败", True)
    user_info = await get_user(event.user_id)
    if mode == "preview":
        if user_info.permission < config.resource_collector.config["jmcomic"]["jm_comic_search_level"]:
            await bot.send(event, "你没有权限使用该功能")
            return {"status": "failed", "message": "你没有权限使用该功能"}
    elif mode == "download":
        if user_info.permission < config.resource_collector.config["jmcomic"]["jm_comic_download_level"]:
            await bot.send(event, "你没有权限使用该功能")
            return {"status": "failed", "message": "你没有权限使用该功能"}
    elif mode == "search":
        if user_info.permission < config.resource_collector.config["jmcomic"]["jm_comic_search_level"]:
            await bot.send(event, "你没有权限使用该功能")
            return {"status": "failed", "message": "你没有权限使用该功能"}
    else:
        await bot.send(event, "指令错误，请使用preview/download/search")
    asyncio.create_task(_call_jm())
    return {"status": "running", "message": "任务已在后台启动，请耐心等待结果"}
def main(bot,config):

    logger = bot.logger


    @bot.on(GroupMessageEvent)
    async def book_resource_search(event):

        if str(event.pure_text).startswith("搜书"):
            book_name = str(event.pure_text).split("搜书")[1]
            await search_book_info(bot,event,config,book_name)

    @bot.on(GroupMessageEvent)
    async def book_resource_download(event):
        if str(event.pure_text).startswith("下载书"):
            try:
                book_id = str(event.pure_text).split("下载书")[1].split(" ")[0]
                hash = str(event.pure_text).split("下载书")[1].split(" ")[1]
                await call_download_book(bot,event,config,book_id,hash)
            except Exception as e:
                bot.logger.error(f"book_resource_download error:{e}")
                await bot.send(event, "指令格式错误，请使用“下载书{book_id} {hash}”")
        elif event.pure_text=="随机奥术" or event.pure_text=="随机asmr" or event.pure_text=="随机奥数":

            await call_asmr(bot,event,config)
        elif event.pure_text=="最新asmr" or event.pure_text=="最新奥术" or event.pure_text=="最新奥数":
            await call_asmr(bot,event,config,mode="latest")
        elif event.pure_text=="最热asmr" or event.pure_text=="最热奥术" or event.pure_text=="热门asmr":
            await call_asmr(bot,event,config,mode="hotest")

    @bot.on(LifecycleMetaEvent)
    async def _(event):
        loop = asyncio.get_running_loop()
        while True:
            try:
                with ThreadPoolExecutor() as executor:
                    await loop.run_in_executor(executor, asyncio.run, check_latest_asmr(bot,event ,config))
                # await check_bili_dynamic(bot,config)
            except Exception as e:
                bot.logger.error(e)
            await asyncio.sleep(700)  # 每 11 分钟检查一次
    """
    以下为jm的功能实现
    """

    @bot.on(GroupMessageEvent)
    async def querycomic(event: GroupMessageEvent):
        if event.pure_text.startswith("jm搜") or event.pure_text.startswith("JM搜"):
            user_info = await get_user(event.user_id)
            if user_info.permission < config.resource_collector.config["jmcomic"]["jm_comic_search_level"]:
                await bot.send(event, "你没有权限使用该功能")
                return
            keyword = event.pure_text
            index = keyword.find("搜")
            if index != -1:
                keyword = keyword[index + len("查询"):]
                if ':' in keyword or ' ' in keyword or '：' in keyword:
                    keyword = keyword[+1:]
                context = JM_search(keyword)
            else:
                await bot.send(event, "指令格式错误，请使用“jm搜{关键字}”")
                return
            aim = context

            logger.info(f"JM搜索: {aim}")
            try:
                if context == "":
                    await bot.send(event, "好像没有找到你说的本子呢~~~")
                    return
                r = Node(content=[Text(context)])
                await bot.send(event, r)
            except Exception as e:
                logger.error(e)
                await bot.send(event, "寄了喵", True)

    @bot.on(GroupMessageEvent)
    async def randomcomic(event: GroupMessageEvent):
        if '本周jm' == event.pure_text or '本周JM' == event.pure_text or '今日jm' == event.pure_text or '今日JM' == event.pure_text:
            context = JM_search_week()
            cmList = []

            cmList.append(Node(content=[Text('本周的JM排行如下，请君过目\n')]))
            cmList.append(Node(content=[Text(context)]))
            await bot.send(event,cmList)

    @bot.on(GroupMessageEvent)
    async def download(event: GroupMessageEvent):
        if event.pure_text.startswith("验车") or event.pure_text == "随机本子":
            try:
                if event.pure_text.startswith("验车"):
                    comic_id = int(event.pure_text.replace("验车", ""))
                else:
                    context = ['正在随机ing，请稍等喵~~', '正在翻找好看的本子喵~', '嘿嘿，JM，启动！！！！', '正在翻找JM.jpg',
                               '有色色！我来了', 'hero来了喵~~', '了解~', '全力色色ing~']
                    await bot.send(event, random.choice(context))
                    context = JM_search_comic_id()
                    comic_id = context[random.randint(1, len(context)) - 1]
            except Exception as e:
                logger.error(e)
                await bot.send(event, "无效输入 int，指令格式如下\n验车【车牌号】\n如：验车604142", True)
                return
            await call_jm(bot,event,config,mode="preview",comic_id=comic_id)

    @bot.on(GroupMessageEvent)
    async def downloadAndToPdf(event: GroupMessageEvent):
        if event.pure_text.startswith("JM下载"):

            user_info = await get_user(event.user_id)
            if user_info.permission < config.resource_collector.config["jmcomic"]["jm_comic_download_level"]:
                await bot.send(event, "你没有权限使用该功能")
                return
            try:
                comic_id = int(event.pure_text.replace("JM下载", ""))
                logger.info(f"JM下载启动 aim: {comic_id}")
            except:
                await bot.send(event, "非法参数，指令示例 JM下载601279")
                return
            await call_jm(bot,event,config,mode="download",comic_id=comic_id)



async def wait_and_delete_file(bot,file_path, interval=60):
    await asyncio.sleep(1800) #30min后自动删除
    for _ in range(10):
        try:
            shutil.os.remove(file_path)
            bot.logger.info(f"文件 {file_path} 已成功删除")
            return
        except PermissionError:
            bot.logger.warning(f"文件 {file_path} 被占用，等待重试...")
            await asyncio.sleep(interval)
        except FileNotFoundError:
            bot.logger.warning(f"文件 {file_path} 已不存在")
            return
        except Exception as e:
            bot.logger.error(f"删除文件时出现错误: {e}")
            return

