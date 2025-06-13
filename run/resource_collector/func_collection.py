from developTools.event.events import GroupMessageEvent
from developTools.message.message_components import Text, Node, File, Image
from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.utils.zip import compress_files, sanitize_filename
from framework_common.utils.zip_2_pwd_version import compress_files_with_pwd
from run.resource_collector.service.iwara.iwara1 import search_videos, download_specific_video, fetch_video_info


async def iwara_search(bot:ExtendBot,event:GroupMessageEvent,config,aim:str,operation:str):
    user_info = await get_user(event.user_id)
    if operation=="search":
        user_info = await get_user(event.user_id)
        if not user_info.permission >= config.resource_collector.config["iwara"]["iwara_search_level"]:
            await bot.send(event, "无权限")
            return
        await bot.send(event, Text(f"正在iwara搜索{aim}"))
        try:
            list = await search_videos(aim, config,config.resource_collector.config["iwara"]["iwara_gray_layer"])
            if len(list) == 0:
                await bot.send(event, Text(f"未搜索到{aim}相关iwara视频"))
                return
            node_list = [
                Node(content=[Text(i.get('title')), Text("\nvideo_id:"), Text(i.get('video_id')), Image(file=i.get('path'))])
                for i in list
            ]
            bot.logger.info(node_list)
            await bot.send(event, node_list)
        except Exception as e:
            await bot.send(event, Text(f"iwara搜索{aim}失败：{e}"))
    elif operation=="download":
        if not user_info.permission >= config.resource_collector.config["iwara"]["iwara_download_level"]:
            await bot.send(event, "无权限")
            return
        videoid = aim
        await bot.send(event, Text(f"正在下载iwara视频{videoid}"))
        try:
            list = await download_specific_video(videoid, config)
            if config.resource_collector.config["iwara"]["zip_file"]:
                zip_name=f"{list.get('title')}.zip"
                bot.logger.info(f"正在压缩文件至data/video/cache/{zip_name}")
                if config.resource_collector.config["iwara"]["zip_password"]:
                    compress_files_with_pwd(list.get('path'), "data/video/cache", zip_name=zip_name, password=config.resource_collector.config["iwara"]["zip_password"])
                    await bot.send(event, Text(f"文件压缩中，密码：{config.resource_collector.config['iwara']['zip_password']}"))
                else:
                    compress_files(list.get('path'),
                   "data/video/cache",
                   zip_name=zip_name)
                file_ziped = f"data/video/cache/{sanitize_filename(list.get('title'))}.zip"
                await bot.send(event,File(file=file_ziped))
                msg = [Node(content=[Text(list.get('title')), Text("\nvideo_id:"), Text(list.get('video_id'))])]
            else:
                await bot.send(event, File(file=list.get('path')))
                msg = [Node(content=[Text(list.get('title')), Text("\nvideo_id:"), Text(list.get('video_id'))])]
            await bot.send(event, msg)
        except Exception as e:
            await bot.send(event, Text(f"iwara视频{videoid}下载失败：{e}"))
async def iwara_tendency(bot:ExtendBot,event:GroupMessageEvent,config,aim_type:str):
    user_info = await get_user(event.user_id)
    if not user_info.permission >= config.resource_collector.config["iwara"]["iwara_search_level"]:
        await bot.send(event, "无权限")
        return
    if aim_type=="hotest":
        await bot.send(event, Text(f"正在获取iwara热门视频"))
        try:
            list = await fetch_video_info('popularity', config)
            if len(list) == 0:
                await bot.send(event, Text(f"未获取到iwara热门视频"))
                return
            node_list = [
                Node(content=[Text(i.get('title')), Text("\nvideo_id:"), Text(i.get('video_id')),
                              Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        except Exception as e:
            await bot.send(event, Text(f"iwara热门获取失败：{e}"))
    if aim_type=="trending":
        await bot.send(event, Text(f"正在获取iwara趋势视频"))
        try:
            list = await fetch_video_info('trending', config)
            if len(list) == 0:
                await bot.send(event, Text(f"未获取到iwara趋势视频"))
                return
            node_list = [
                Node(content=[Text(i.get('title')), Text("\nvideo_id:"), Text(i.get('video_id')),
                              Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        except Exception as e:
            await bot.send(event, Text(f"iwara趋势获取失败：{e}"))
    if aim_type=="latest":
        await bot.send(event, Text(f"正在获取iwara最新视频"))
        try:
            list = await fetch_video_info('date', config)
            if len(list) == 0:
                await bot.send(event, Text(f"未获取到iwara最新视频"))
                return
            node_list = [
                Node(content=[Text(i.get('title')), Text("\nvideo_id:"), Text(i.get('video_id')),
                              Image(file=i.get('path'))])
                for i in list
            ]
            await bot.send(event, node_list)
        except Exception as e:
            await bot.send(event, Text(f"iwara最新获取失败：{e}"))
