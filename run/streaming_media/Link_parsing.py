import asyncio
import shutil
from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image,File,Video
from plugins.streaming_media_service.Link_parsing.core.login_core import ini_login_Link_Prising
from plugins.streaming_media_service.Link_parsing.Link_parsing import link_prising,download_video_link_prising
from plugins.streaming_media_service.Link_parsing.music_link_parsing import netease_music_link_parse

global teamlist
teamlist = {}
async def call_bili_download_video(bot,event: GroupMessageEvent,config):
    global teamlist
    if event.group_id in teamlist:
        json = teamlist[event.group_id]
        teamlist.pop(event.group_id)
    else:
        return {"status": "当前群聊没有已缓存的解析结果。"}
    if json['soft_type'] not in {'bilibili', 'dy', 'wb', 'xhs', 'x'}:
        await bot.send(event, '该类型视频暂未提供下载支持，敬请期待')
        return
    proxy = config.api["proxy"]["http_proxy"]
    try:
        video_json = await download_video_link_prising(json, filepath='data/pictures/cache/', proxy=proxy)
        if 'video' in video_json['type']:
            if video_json['type'] == 'video_bigger':
                await bot.send(event, f'视频有些大，请耐心等待喵~~')
            await bot.send(event, Video(file=video_json['video_path']))
        elif video_json['type'] == 'file':
            await bot.send(event, f'好大的视频，小的将发送至群文件喵~')
            await bot.send(event, File(file=video_json['video_path']))
        elif video_json['type'] == 'too_big':
            await bot.send(event, f'太大了，罢工！')
    except Exception as e:
        await bot.send(event, f'下载失败\n{e}')

def main(bot,config):
    botname=config.basic_config["bot"]["name"]

    bili_login_check,douyin_login_check,xhs_login_check=ini_login_Link_Prising(type=0)
    if bili_login_check and douyin_login_check and xhs_login_check:
        bot.logger.info('链接解析功能已上线！')
    else:
        if not bili_login_check:
            bot.logger.warning('B站session未能成功获取')
        else:
            bot.logger.warning('B站session成功获取')
        if not douyin_login_check:
            bot.logger.warning('未能获取到设置抖音的ck')
        else:
            bot.logger.info('抖音的ck成功获取！')
        if not xhs_login_check:
            bot.logger.warning('未能获取到设置小红书的ck')
        else:
            bot.logger.info('小红书的ck成功获取！')


    node_path = shutil.which("node")  # 自动查找 Node.js 可执行文件路径
    if not node_path:
        bot.logger.warning("Node.js 未安装或未正确添加到系统 PATH 中!")
    try:
        import execjs
        if "Node.js" in execjs.get().name:
            bot.logger.info('系统已正确读取到node.js')
    except:
        pass
    @bot.on(GroupMessageEvent)
    async def Link_Prising_search(event: GroupMessageEvent):
        global teamlist
        proxy = config.api["proxy"]["http_proxy"]
        #print(proxy)
        url=event.raw_message
        if event.group_id in teamlist:
            json=teamlist[event.group_id]
            if event.get("text")[0]=="下载视频":
                if json['soft_type'] not in {'bilibili','dy','wb','xhs','x'}:
                    await bot.send(event, '该类型视频暂未提供下载支持，敬请期待')
                    teamlist.pop(event.group_id)
                    return
                #await bot.send(event, '开始下载，请稍等喵~~~')
                await call_bili_download_video(bot,event,config)
            return


        link_prising_json = await link_prising(url, filepath='data/pictures/cache/',proxy=proxy)
        send_context=f'{botname}识别结果：'
        #print(link_prising_json)
        if link_prising_json['status']:
            bot.logger.info('链接解析成功，开始推送~~')
            if link_prising_json['video_url']:
                send_context=f'该视频可下载，发送“下载视频”以推送'
                teamlist[event.group_id]=link_prising_json
                if "QQ小程序" in url and config.settings["bili_dynamic"]["is_QQ_chek"] is not True:
                    await bot.send(event, [f'{send_context}'])
                    return
            await bot.send(event, [f'{send_context}\n', Image(file=link_prising_json['pic_path'])])
        else:
            if link_prising_json['reason']:
                #print(link_prising_json)
                bot.logger.error(str('bili_link_error ') + link_prising_json['reason'])

    @bot.on(GroupMessageEvent)
    async def Music_Link_Prising_search(event: GroupMessageEvent):
        if config.settings["网易云卡片"]["enable"]:
            url = event.raw_message
            if "music.163.com" not in url:
                return
            link_parsing_json = await netease_music_link_parse(url, filepath='data/pictures/cache/')
            if link_parsing_json['status']:
                bot.logger.info('网易云音乐链接解析成功，开始推送~~~')
                await bot.send(event, Image(file=link_parsing_json['pic_path']))
            else:
                if link_parsing_json['reason']:
                    bot.logger.error(f'netease_music_link_error: {link_parsing_json["reason"]}')


