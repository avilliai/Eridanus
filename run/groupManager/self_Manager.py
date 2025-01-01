from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from plugins.core.userDB import get_user


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
def main(bot,config):
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