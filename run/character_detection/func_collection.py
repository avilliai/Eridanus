from framework_common.database_util.User import get_user
async def operate_group_censor(bot, event, config, target_id, operation):
    if operation == "开启奶龙审核":
        await call_operate_nailong_censor(bot, event, config, target_id, True)
    elif operation == "关闭奶龙审核":
        await call_operate_nailong_censor(bot, event, config, target_id, False)
    elif operation == "开启doro审核":
        await call_operate_doro_censor(bot, event, config, target_id, True)
    elif operation == "关闭doro审核":
        await call_operate_doro_censor(bot, event, config, target_id, False)
    elif operation == "开启男娘审核":
        await call_operate_nanniang_censor(bot, event, config, target_id, True)
    elif operation == "关闭男娘审核":
        await call_operate_nanniang_censor(bot, event, config, target_id, False)


async def call_operate_nailong_censor(bot, event, config, target_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["user_handle_logic_operate_level"]:
        if status:
            if target_id not in config.character_detection.nailong["whitelist"]:
                config.character_detection.nailong["whitelist"].append(target_id)
                config.save_yaml("nailong",plugin_name="character_detection")
            await bot.send(event, f"已将{target_id}加入奶龙审核目标")
        else:
            try:
                config.character_detection.nailong["whitelist"].remove(target_id)
                config.save_yaml("nailong",plugin_name="character_detection")
                await bot.send(event, f"已将{target_id}移出奶龙审核目标")
            except ValueError:
                await bot.send(event, f"{target_id} 不在奶龙审核目标中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def call_operate_doro_censor(bot, event, config, target_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["user_handle_logic_operate_level"]:
        if status:
            if target_id not in config.character_detection.doro["whitelist"]:
                config.character_detection.doro["whitelist"].append(target_id)
                config.save_yaml("doro",plugin_name="character_detection")
            await bot.send(event, f"已将{target_id}加入doro审核目标")
        else:
            try:
                config.character_detection.doro["whitelist"].remove(target_id)
                config.save_yaml("doro",plugin_name="character_detection")
                await bot.send(event, f"已将{target_id}移出doro审核目标")
            except ValueError:
                await bot.send(event, f"{target_id} 不在doro审核目标中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def call_operate_nanniang_censor(bot, event, config, target_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["user_handle_logic_operate_level"]:
        if status:
            if target_id not in config.character_detection.nanniang["whitelist"]:
                config.character_detection.nanniang["whitelist"].append(target_id)
                config.save_yaml("nanniang",plugin_name="character_detection")
            await bot.send(event, f"已将{target_id}加入男娘审核目标")
        else:
            try:
                config.character_detection.nanniang["whitelist"].remove(target_id)
                config.save_yaml("nanniang",plugin_name="character_detection")
                await bot.send(event, f"已将{target_id}移出男娘审核目标")
            except ValueError:
                await bot.send(event, f"{target_id} 不在男娘审核目标中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")