import traceback

from developTools.message.message_components import Node, Text
from framework_common.framework_util.websocket_fix import ExtendBot


async def quit_group(bot: ExtendBot,event,config,th:int=30,mode: str="above"):
    """
    退出群聊
    :param bot: WebSocketBot
    :param event: GroupMessageEvent
    :param config: 配置文件
    :param th: 筛选阈值
    :param mode: 退出模式，"above"表示只退出上面的成员，"below"表示只退出下面的成员
    :return:
    """
    bot.logger.info(f"退出群聊：模式:{mode} 阈值:{th}")
    if not event.user_id == config.common_config.basic_config["master"]["id"]:
        await bot.send(event, "你没有权限执行此操作！恶意操作将被上报！")
        return {"status": "failed", "reason": "你没有权限执行此操作！"}
    groups = await bot.get_group_list()

    count=[]
    if mode=="above":
        for group in groups["data"]:
            if group["member_count"] > th and group["group_id"]!=0 and group["group_id"] not in config.common_config.censor_group["whitelist"]:
                try:
                    bot.logger.info(f'退出群聊：{group}')
                    await bot.quit(group["group_id"])
                    count.append(group)
                except:
                    traceback.print_exc()
    elif mode=="below":
        for group in groups["data"]:
            if group["member_count"] < th and group["group_id"]!=0 and group["group_id"] not in config.common_config.censor_group["whitelist"]:
                try:
                    bot.logger.info(f'退出群聊：{group}')
                    await bot.quit(group["group_id"])
                    count.append(group)
                except:
                    traceback.print_exc()
    await bot.send(event, f"已退出{len(count)}个群聊！")
    count_str = '\n\n'.join(str(item) for item in count)
    await bot.send(event, Node(content=[Text(f"退出的群如下：{count_str}")]))