import asyncio
import shutil
from developTools.event.events import GroupMessageEvent, LifecycleMetaEvent
from developTools.message.message_components import Image
from plugins.resource_search_plugin.Link_parsing.core.login_core import ini_login_Link_Prising
from plugins.resource_search_plugin.Link_parsing.Link_parsing import link_prising

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
        url=event.raw_message
        if "QQ小程序" in url and config.settings["bili_dynamic"]["is_QQ_chek"] is not True:
            return

        try:
            dy_file_path,url_check=await link_prising(url,filepath='data/pictures/cache/')
            if dy_file_path is not None:
                bot.logger.info('链接解析成功，开始推送~~')
                await bot.send(event, [f'{botname}识别结果：\n',Image(file=dy_file_path)])
        except Exception as e:
            bot.logger.warning('链接解析失败')
            pass

