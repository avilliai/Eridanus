import asyncio
import base64
import os
import random
import time

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent, FriendRequestEvent, GroupRequestEvent, \
    LifecycleMetaEvent
from developTools.message.message_components import Record, Text, Image, File, Node
from framework_common.database_util.User import get_user

from developTools.utils.logger import get_logger

logger = get_logger()


async def delete_old_files_async(folder_path):
    """
    异步删除文件夹中过期的文件
    :param folder_path:
    :return:
    """
    current_time = time.time()
    time_threshold = 3600
    deleted_file_sizes = 0

    async def process_file(file_path) -> None:
        nonlocal deleted_file_sizes
        try:
            if file_path.endswith(".py") or file_path.endswith(".ttf"):
                #print(f"跳过文件: {file_path}")
                return None

            file_mtime = os.path.getmtime(file_path)

            if current_time - file_mtime > time_threshold:
                file_size = os.path.getsize(file_path)
                deleted_file_sizes += file_size
                await asyncio.to_thread(os.remove, file_path)
                #print(f"已删除文件: {file_path} (大小: {file_size:.2f} MB)")
        except Exception as e:
            logger.error(f"处理文件失败: {file_path} - {e}")
        deleted_file_sizes = deleted_file_sizes // (1024 ** 2)
        return None

    # 获取所有文件路径
    tasks = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 检查是否是文件（跳过文件夹）
        if os.path.isfile(file_path):
            tasks.append(process_file(file_path))

    # 等待所有文件处理任务完成
    await asyncio.gather(*tasks)

    # 统计删除的文件总大小
    return deleted_file_sizes

async def call_operate_blandwhite(bot, event, config, target_id, type):
    if type == "添加群黑名单":
        await call_operate_group_blacklist(bot, event, config, target_id, True)
    elif type == "删除群黑名单":
        await call_operate_group_blacklist(bot, event, config, target_id, False)
    elif type == "添加群白名单":
        await call_operate_group_whitelist(bot, event, config, target_id, True)
    elif type == "取消群白名单":
        await call_operate_group_whitelist(bot, event, config, target_id, False)
    elif type == "添加用户黑名单":
        await call_operate_user_blacklist(bot, event, config, target_id, True)
    elif type == "取消用户黑名单":
        await call_operate_user_blacklist(bot, event, config, target_id, False)
    elif type == "添加用户白名单":
        await call_operate_user_whitelist(bot, event, config, target_id, True)
    elif type == "取消用户白名单":
        await call_operate_user_whitelist(bot, event, config, target_id, False)


async def call_operate_user_blacklist(bot, event, config, target_user_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["user_handle_logic_operate_level"]:
        if status:
            if target_user_id not in config.common_config.censor_user["blacklist"]:
                config.common_config.censor_user["blacklist"].append(target_user_id)
                config.save_yaml("censor_user", plugin_name="common_config")
            await bot.send(event, f"已将{target_user_id}加入黑名单")
        else:
            try:
                config.common_config.censor_user["blacklist"].remove(target_user_id)
                config.save_yaml("censor_user", plugin_name="common_config")
                await bot.send(event, f"{target_user_id} 已被移出黑名单")
            except ValueError:
                await bot.send(event, f"{target_user_id} 不在黑名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def call_operate_user_whitelist(bot, event, config, target_user_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["user_handle_logic_operate_level"]:
        if status:
            if target_user_id not in config.common_config.censor_user["whitelist"]:
                config.common_config.censor_user["whitelist"].append(target_user_id)
                config.save_yaml("censor_user", plugin_name="common_config")
            await bot.send(event, f"已将{target_user_id}加入白名单")
        else:
            try:
                config.common_config.censor_user["whitelist"].remove(target_user_id)
                config.save_yaml("censor_user", plugin_name="common_config")
                await bot.send(event, f"{target_user_id} 已被移出白名单")
            except ValueError:
                await bot.send(event, f"{target_user_id} 不在白名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def call_operate_group_blacklist(bot, event, config, target_group_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["group_handle_logic_operate_level"]:
        if status:
            if target_group_id not in config.common_config.censor_group["blacklist"]:
                config.common_config.censor_group["blacklist"].append(target_group_id)
                config.save_yaml("censor_group", plugin_name="common_config")
            await bot.send(event, f"已将群{target_group_id}加入黑名单")
        else:
            try:
                config.common_config.censor_group["blacklist"].remove(target_group_id)
                config.save_yaml("censor_group", plugin_name="common_config")
                await bot.send(event, f"已将群{target_group_id}移出黑名单")
            except ValueError:
                await bot.send(event, f"群{target_group_id} 不在黑名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def call_operate_group_whitelist(bot, event, config, target_group_id, status):
    user_info = await get_user(event.user_id, event.sender.nickname)
    if user_info.permission >= config.common_config.basic_config["group_handle_logic_operate_level"]:
        if status:
            if target_group_id not in config.common_config.censor_group["whitelist"]:
                config.common_config.censor_group["whitelist"].append(target_group_id)
                config.save_yaml("censor_group", plugin_name="common_config")
            await bot.send(event, f"已将群{target_group_id}加入白名单")
        else:
            try:
                config.common_config.censor_group["whitelist"].remove(target_group_id)
                config.save_yaml(str("censor_group"), plugin_name="common_config")
                await bot.send(event, f"已将群{target_group_id}移出白名单")
            except ValueError:
                await bot.send(event, f"群{target_group_id} 不在白名单中")
    else:
        await bot.send(event, f"你没有足够权限执行此操作")


async def garbage_collection(bot, event, config):
    bot.logger.info_func("开始清理缓存")
    folders = ["data/pictures/cache",
               "data/pictures/galgame",
               "data/video/cache",
               "data/voice/cache",
               "run/streaming_media/service/Link_parsing/data",
               "data/pictures/benzi"
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


async def report_to_master(bot, event, config):
    mes_type = "bad_content"
    if hasattr(event, "group_id"):
        group_id = event.group_id
    else:
        group_id = None
    if mes_type == "bad_content":
        r = f"违规内容上报\n发送者id为{event.user_id} 群号为{group_id}"
    elif mes_type == "ideas":
        r = f"反馈意见上报\n发送者id为{event.user_id}"
    node_li = [Node(content=[Text(r)])]
    for i in event.processed_message:
        if "text" in i:
            node_li.append(Node(content=[Text(i["text"])]))
        elif "image" in i:
            node_li.append(Node(content=[Image(file=i["image"])]))
        else:
            node_li.append(Node(content=[Text(str(i))]))
    await bot.send_friend_message(config.common_config.basic_config["master"]['id'], node_li)


async def send(bot, event, config, message, delay=0):
    await asyncio.sleep(delay)
    message_list = []
    print(message)
    for i in message:
        #print(i)
        if len(i) > 1:
            for j in i:
                if "text" in j:
                    message_list.append(Text(i[j]))
                elif "image" in j:
                    message_list.append(Image(file=i[j]))
                elif "audio" in j:
                    message_list.append(Record(file=i[j]))
                elif "video" in j:
                    message_list.append(File(file=i[j]))
        else:
            if "text" in i:
                message_list.append(Text(i["text"]))
            elif "image" in i:
                message_list.append(Image(file=i["image"]))
            elif "audio" in i:
                message_list.append(Record(file=i["audio"]))
            elif "video" in i:
                message_list.append(File(file=i["video"]))
    await bot.send(event, message_list)


async def send_contract(bot, event, config):
    return {"管理员id": config.common_config.basic_config["master"]['id']}


def main(bot, config):
    global send_next_message
    send_next_message = False

    @bot.on(LifecycleMetaEvent)
    async def _(event):
        group_list = await bot.get_group_list()
        group_list = group_list["data"]
        friend_list = await bot.get_friend_list()
        friend_list = friend_list["data"]

        encoded_strings = ['c2FsdF/or7vlj5bnvqTliJfooajmlbDph486IF9zYWx0',
                           'c2FsdF/or7vlj5blpb3lj4vliJfooajmlbDph486IF9zYWx0',
                           'c2FsdF/lkK/liqjmiJDlip8K5b2T5YmN576k5pWw6YePOiBfc2FsdA==',
                           'c2FsdF/lpb3lj4vmlbDph486IF9zYWx0',
                           'c2FsdF/pobnnm67lnLDlnYDkuI7mlofmoaMKaHR0cHM6Ly9lcmlkYW51cy1kb2MubmV0bGlmeS5hcHAvCuacrOmhueebrua6kOeggeWPiuS4gOmUruWMheWujOWFqOWFjei0ue+8jOWmguaCqOmAmui/h+S7mOi0uea4oOmBk+iOt+W+l++8jOaBreWWnOS9oOiiq+mql+S6huOAgl9zYWx0',
                           'c2FsdF9kYXRhL3N5c3RlbS93aW4geHAubXAzX3NhbHQ=']

        def decode_string(s):
            decoded_bytes = base64.b64decode(s)
            decoded_string = decoded_bytes.decode('utf-8')
            return decoded_string[5:-5]

        try:
            bot.logger.info(f"{decode_string(encoded_strings[0])}: {len(group_list)}")
            bot.logger.info(f"{decode_string(encoded_strings[1])} {len(friend_list)}")
            await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                          f"{decode_string(encoded_strings[2])}{len(group_list)}\n{decode_string(encoded_strings[3])} {len(friend_list)}")
        except:
            pass
        if random.randint(1, 100) < 10:
            await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                          Record(file=f"{decode_string(encoded_strings[5])}"))
        await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                      f"{decode_string(encoded_strings[4])}")
        while True:
            await garbage_collection(bot, event, config)
            await asyncio.sleep(5400)  # 每1.5h清理一次缓存
    @bot.on(GroupMessageEvent)
    async def groups_send(event: GroupMessageEvent):
        global send_next_message
        if event.user_id==config.common_config.basic_config["master"]['id'] and event.pure_text=="notice":
            send_next_message = True
            await bot.send(event,"下一条消息将被转发至所有群")
        if send_next_message and event.user_id==config.common_config.basic_config["master"]['id']:
            send_next_message = False
            groups = await bot.get_group_list()
            for group in groups["data"]:
                try:
                    bot.logger.info(f"转发消息至群{group['group_id']}")
                    await bot.send_group_message(group["group_id"],event.message_chain)
                except Exception as e:
                    bot.logger.error(f"发送群消息失败：{group['group_id']} 原因: {e}")
    @bot.on(GroupMessageEvent)
    async def _(event):
        if event.pure_text == "/gc":
            user_info = await get_user(event.user_id, event.sender.nickname)
            if user_info.permission >= 3:
                r = await garbage_collection(bot, event, config)
                await bot.send(event, r)

    @bot.on(FriendRequestEvent)
    async def FriendRequestHandler(event: FriendRequestEvent):
        if event.user_id in config.common_config.censor_user["blacklist"]:
            bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 用户被加入黑名单，拒绝添加")
            await bot.handle_friend_request(event.flag, False, "拒绝添加好友")
            await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                          f"收到好友请求，{event.user_id}({event.comment}) 用户被加入黑名单，拒绝添加")
        else:
            user_info = await get_user(event.user_id)
            if user_info.permission >= config.common_config.basic_config["申请bot好友所需权限"]:
                bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 同意")
                await bot.handle_friend_request(event.flag, True, "")
                await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                              f"收到好友请求，{event.user_id}({event.comment}) 同意")
            else:
                bot.logger.info_func(f"收到好友请求，{event.user_id}({event.comment}) 拒绝")
                await bot.handle_friend_request(event.flag, False, "你没有足够权限添加好友")
                await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                              f"收到好友请求，{event.user_id}({event.comment}) 拒绝（用户权限不足）")

    @bot.on(GroupRequestEvent)
    async def GroupRequestHandler(event: GroupRequestEvent):
        if event.sub_type == "invite":
            if event.group_id in config.common_config.censor_group["blacklist"]:
                bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 群被加入黑名单，拒绝邀请")
                await bot.send_friend_message(event.user_id, f"该群已被加入黑名单，无法加入")
                await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                              f"收到来自{event.user_id})的群邀请，{event.group_id}({event.comment}) 群被加入黑名单，拒绝邀请")
            else:
                user_info = await get_user(event.user_id)
                if user_info.permission >= config.common_config.basic_config["邀请bot加群所需权限"]:
                    bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 同意")
                    await bot.set_group_add_request(event.flag, True, "allow")
                    await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                                  f"收到来自{event.user_id}的群邀请，{event.group_id}({event.comment}) 同意")
                else:
                    bot.logger.info_func(f"收到群邀请，{event.group_id}({event.comment}) 拒绝")
                    await bot.send_friend_message(event.user_id, f"你没有足够权限邀请bot加入该群")
                    await bot.send_friend_message(config.common_config.basic_config["master"]['id'],
                                                  f"收到来自{event.user_id}的群邀请，{event.group_id}({event.comment}) 拒绝（用户权限不足）")
        elif event.sub_type == "add":
            if event.group_id in config.common_config.censor_group["blacklist"]:
                pass
            else:
                bot.logger.info_func(f"收到加群申请，{event.group_id} {event.comment}同意")
                await bot.send_group_message(event.group_id,
                                             f"有新的加群请求，请尽快处理\n申请人：{event.user_id}\n{event.comment}")

    @bot.on(GroupMessageEvent)
    async def black_and_white_handler(event):
        await _handler(event)

    @bot.on(PrivateMessageEvent)
    async def black_and_white_handler(event):
        await _handler(event)

    async def _handler(event):
        if event.pure_text.startswith("/bl add "):
            try:
                target_user_id = int(event.pure_text.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
            await call_operate_user_blacklist(bot, event, config, target_user_id, True)
        elif event.pure_text.startswith("/bl remove "):
            try:
                target_user_id = int(event.pure_text.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
            await call_operate_user_blacklist(bot, event, config, target_user_id, False)
        elif event.pure_text.startswith("/blgroup add "):
            try:
                target_group_id = int(event.pure_text.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的群号")
                return
            await call_operate_group_blacklist(bot, event, config, target_group_id, True)
        elif event.pure_text.startswith("/blgroup remove "):
            try:
                target_group_id = int(event.pure_text.split(" ")[2])
            except:
                await bot.send(event, f"请输入正确的群号")
                return
            await call_operate_group_blacklist(bot, event, config, target_group_id, False)
        elif event.pure_text.startswith("/wl add "):
            try:
                target_user_id = int(event.pure_text.split(" ")[2])
                await call_operate_user_whitelist(bot, event, config, target_user_id, True)
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
        elif event.pure_text.startswith("/wl remove "):
            try:
                target_user_id = int(event.pure_text.split(" ")[2])
                await call_operate_user_whitelist(bot, event, config, target_user_id, False)
            except:
                await bot.send(event, f"请输入正确的用户id")
                return
        elif event.pure_text.startswith("/wlgroup add "):
            try:
                target_group_id = int(event.pure_text.split(" ")[2])
                await call_operate_group_whitelist(bot, event, config, target_group_id, True)
            except:
                await bot.send(event, f"请输入正确的群号")
        elif event.pure_text.startswith("/wlgroup remove "):
            try:
                target_group_id = int(event.pure_text.split(" ")[2])
                await call_operate_group_whitelist(bot, event, config, target_group_id, False)
            except:
                await bot.send(event, f"请输入正确的群号")
