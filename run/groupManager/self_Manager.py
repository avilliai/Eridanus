import asyncio

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent, FriendRequestEvent, GroupRequestEvent, \
    GroupIncreaseNoticeEvent, LifecycleMetaEvent
from plugins.core.aiReplyCore_without_funcCall import aiReplyCore_shadow
from plugins.core.userDB import get_user
from plugins.utils.GCTool import delete_old_files_async


async def call_operate_blandwhite(bot,event,config,target_id,type):
    if type=="添加群黑名单":
        await call_operate_group_blacklist(bot,event,config,target_id,True)
    elif type=="删除群黑名单":
        await call_operate_group_blacklist(bot,event,config,target_id,False)
    elif type=="添加群白名单":
        await call_operate_group_whitelist(bot,event,config,target_id,True)
    elif type=="取消群白名单":
        await call_operate_group_whitelist(bot,event,config,target_id,False)
    elif type=="添加用户黑名单":
        await call_operate_user_blacklist(bot,event,config,target_id,True)
    elif type=="取消用户黑名单":
        await call_operate_user_blacklist(bot,event,config,target_id,False)
    elif type=="添加用户白名单":
        await call_operate_user_whitelist(bot,event,config,target_id,True)
    elif type=="取消用户白名单":
        await call_operate_user_whitelist(bot,event,config,target_id,False)

async def call_operate_user_blacklist(bot,event,config,target_user_id,status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.settings["bot_config"]["user_handle_logic_operate_level"]:
        if status:
            if target_user_id not in config.censor_user["blacklist"]:
                config.censor_user["blacklist"].append(target_user_id)
                config.save_yaml(str("censor_user"))
            await bot.send(event, f"已将{target_user_id}加入黑名单")
        else:
            try:
                config.censor_user["blacklist"].remove(target_user_id)
                config.save_yaml(str("censor_user"))
            except ValueError:
                await bot.send(event,f"{target_user_id} 不在黑名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")
async def call_operate_user_whitelist(bot,event,config,target_user_id,status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.settings["bot_config"]["user_handle_logic_operate_level"]:
        if status:
            if target_user_id not in config.censor_user["whitelist"]:
                config.censor_user["whitelist"].append(target_user_id)
                config.save_yaml(str("censor_user"))
            await bot.send(event, f"已将{target_user_id}加入白名单")
        else:
            try:
                config.censor_user["whitelist"].remove(target_user_id)
                config.save_yaml(str("censor_user"))
            except ValueError:
                await bot.send(event,f"{target_user_id} 不在白名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")
async def call_operate_group_blacklist(bot,event,config,target_group_id,status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.settings["bot_config"]["group_handle_logic_operate_level"]:
        if status:
            if target_group_id not in config.censor_group["blacklist"]:
                config.censor_group["blacklist"].append(target_group_id)
                config.save_yaml(str("censor_group"))
            await bot.send(event, f"已将群{target_group_id}加入黑名单")
        else:
            try:
                config.censor_group["blacklist"].remove(target_group_id)
                config.save_yaml(str("censor_group"))
            except ValueError:
                await bot.send(event, f"群{target_group_id} 不在黑名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")
async def call_operate_group_whitelist(bot,event,config,target_group_id,status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info[6] >= config.settings["bot_config"]["group_handle_logic_operate_level"]:
        if status:
            if target_group_id not in config.censor_group["whitelist"]:
                config.censor_group["whitelist"].append(target_group_id)
                config.save_yaml(str("censor_group"))
            await bot.send(event, f"已将群{target_group_id}加入白名单")
        else:
            try:
                config.censor_group["whitelist"].remove(target_group_id)
                config.save_yaml(str("censor_group"))
            except ValueError:
                await bot.send(event, f"群{target_group_id} 不在白名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")
async def garbage_collection(bot,event,config):
    bot.logger.info_func("开始清理缓存")
    folders=["data/pictures/cache",
              "data/pictures/galgame",
              "data/video/cache",
              "data/voice/cache",
              "plugins/resource_search_plugin/Link_parsing/data"
              ]
    async def safe_delete(folder):
        try:
            return await delete_old_files_async(folder)
        except Exception as e:
            bot.logger.error(f"处理文件夹 {folder} 时发生错误: {e}")
            return 0
    folder_sizes = await asyncio.gather(*[safe_delete(folder) for folder in folders], return_exceptions=True)

    total_size = sum(size for size in folder_sizes if isinstance(size, (int, float)))
    bot.logger.info_func(f"本次清理了 {total_size:.2f} MB 的缓存")
    return f"本次清理了 {total_size:.2f} MB 的缓存"
async def report_to_master(bot,event,config,mes_type):
    if mes_type=="bad_content":
        r = await aiReplyCore_shadow([{"text": f"告诉管理员，id为{event.user_id}，昵称为{event.sender.nickname}的用户发送了不合适的内容：{event.raw_message}。上报消息中必须保留发送者id即{event.user_id}请管理员决定是否屏蔽该用户。请注意在处理该任务时，保持你的角色设定"}], config.basic_config["master"]['id'], config,
                                     func_result=True)
        await bot.send_friend_message(config.basic_config["master"]['id'],r)
    elif mes_type=="ideas":
        r = await aiReplyCore_shadow([{
                                          "text": f"告诉管理员，id为{event.user_id}，昵称为{event.sender.nickname}的用户反馈了 {event.raw_message}。上报消息中必须保留发送者id即{event.user_id}。请注意在处理该任务时，保持你的角色设定"}],
                                     config.basic_config["master"]['id'], config,
                                     func_result=True)
        await bot.send_friend_message(config.basic_config["master"]['id'], r)
def main(bot,config):
    @bot.on(LifecycleMetaEvent)
    async def _(event):
        while True:
            await garbage_collection(bot,event,config)
            await asyncio.sleep(5400)  # 每1.5h清理一次缓存
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.raw_message=="/gc":
            user_info = await get_user(event.user_id, event.sender.nickname)
            if user_info[6] >= 3:
                r=await garbage_collection(bot,event,config)
                await bot.send(event,r)
    @bot.on(FriendRequestEvent)
    async def FriendRequestHandler(event: FriendRequestEvent):
        if event.user_id in config.censor_user["blacklist"]:
            bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 用户被加入黑名单，拒绝添加")
            await bot.handle_friend_request(event.flag,False,"拒绝添加好友")
            await bot.send_friend_message(config.basic_config["master"]['id'], f"收到好友请求，{event.user_id}({event.comment}) 用户被加入黑名单，拒绝添加")
        else:
            user_info = await get_user(event.user_id)
            if user_info[6] >= config.settings["bot_config"]["申请bot好友所需权限"]:
                bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 同意")
                await bot.handle_friend_request(event.flag,True,"")
                await bot.send_friend_message(config.basic_config["master"]['id'], f"收到好友请求，{event.user_id}({event.comment}) 同意")
            else:
                bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 拒绝")
                await bot.handle_friend_request(event.flag,False,"你没有足够权限添加好友")
                await bot.send_friend_message(config.basic_config["master"]['id'], f"收到好友请求，{event.user_id}({event.comment}) 拒绝（用户权限不足）")

    @bot.on(GroupRequestEvent)
    async def GroupRequestHandler(event: GroupRequestEvent):
        if event.sub_type == "invite":
            if event.group_id in config.censor_group["blacklist"]:
                bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 群被加入黑名单，拒绝邀请")
                await bot.send(event, f"该群已被加入黑名单，无法加入")
                await bot.send_friend_message(config.basic_config["master"]['id'], f"收到来自{event.user_id})的群邀请，{event.group_id}({event.comment}) 群被加入黑名单，拒绝邀请")
            else:
                user_info = await get_user(event.user_id)
                if user_info[6] >= config.settings["bot_config"]["邀请bot加群所需权限"]:
                    bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 同意")
                    await bot.set_group_add_request(event.flag,True,"allow")
                    await bot.send_friend_message(config.basic_config["master"]['id'], f"收到来自{event.user_id}的群邀请，{event.group_id}({event.comment}) 同意")
                else:
                    bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 拒绝")
                    await bot.send(event, f"你没有足够权限邀请bot加入该群")
                    await bot.send_friend_message(config.basic_config["master"]['id'], f"收到来自{event.user_id}的群邀请，{event.group_id}({event.comment}) 拒绝（用户权限不足）")
        elif event.sub_type == "add":
            if event.group_id in config.censor_group["blacklist"]:
                pass
            else:
                bot.logger.info_func(f"收到加群申请，{event.group_id} {event.comment}同意")
                await bot.send_group_message(event.group_id,f"有新的加群请求，请尽快处理\n申请人：{event.user_id}\n{event.comment}")
    @bot.on(GroupIncreaseNoticeEvent)
    async def GroupIncreaseNoticeHandler(event: GroupIncreaseNoticeEvent):
        if config.api["llm"]["aiReplyCore"]:
            data = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            name=data["data"]["nickname"]
            r = await aiReplyCore_shadow([{"text": f"{name}加入了群聊，为他发送入群欢迎语"}], event.group_id, config, func_result=True)
            await bot.send(event, str(r))
        else:
            await bot.send(event, f"欢迎新群员{event.user_id}加入群聊")
    @bot.on(GroupMessageEvent)
    async def black_and_white_handler(event):
        await _handler(event)
    @bot.on(PrivateMessageEvent)
    async def black_and_white_handler(event):
        await _handler(event)
    async def _handler(event):
        if event.raw_message.startswith("/bl add "):
            try:
                target_user_id = int(event.raw_message.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
            await call_operate_user_blacklist(bot,event,config,target_user_id,True)
        elif event.raw_message.startswith("/bl remove "):
            try:
                target_user_id = int(event.raw_message.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
            await call_operate_user_blacklist(bot,event,config,target_user_id,False)
        elif event.raw_message.startswith("/blgroup add "):
            try:
                target_group_id = int(event.raw_message.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的群号")
                return
            await call_operate_group_blacklist(bot,event,config,target_group_id,True)
        elif event.raw_message.startswith("/blgroup remove "):
            try:
                target_group_id = int(event.raw_message.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的群号")
                return
            await call_operate_group_blacklist(bot,event,config,target_group_id,False)
        elif event.raw_message.startswith("/wl add "):
            try:
                target_user_id = int(event.raw_message.split(" ")[2])
                await call_operate_user_whitelist(bot,event,config,target_user_id,True)
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
        elif event.raw_message.startswith("/wl remove "):
            try:
                target_user_id = int(event.raw_message.split(" ")[2])
                await call_operate_user_whitelist(bot,event,config,target_user_id,False)
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
        elif event.raw_message.startswith("/wlgroup add "):
            try:
                target_group_id = int(event.raw_message.split(" ")[2])
                await call_operate_group_whitelist(bot,event,config,target_group_id,True)
            except:
                await bot.send(event, f"请输入正确的群号")
        elif event.raw_message.startswith("/wlgroup remove "):
            try:
                target_group_id = int(event.raw_message.split(" ")[2])
                await call_operate_group_whitelist(bot,event,config,target_group_id,False)
            except:
                await bot.send(event, f"请输入正确的群号")
