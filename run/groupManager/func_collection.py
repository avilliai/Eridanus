import traceback

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
    if not event.user_id == config.common_config.basic_config["master"]["id"]:
        await bot.send(event, "你没有权限执行此操作！恶意操作将被上报！")
    groups = await bot.get_group_list()
    for group in groups["data"]:
        print(group["group_id"], group["member_count"])
    if mode=="above":
        for group in groups["data"]:
            if group["member_count"] > th and group["group_id"]!=0:
                try:
                    await bot.quit(group["group_id"])
                except:
                    traceback.print_exc()
    elif mode=="below":
        for group in groups["data"]:
            if group["member_count"] < th and group["group_id"]!=0:
                try:
                    await bot.quit(group["group_id"])
                except:
                    traceback.print_exc()