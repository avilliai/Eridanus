# AI生成的插件代码
# 生成时间: 2025-05-25 20:53:14
# 用户请求: 实现一个打招呼的功能  ,当用户发送"你好" , 回复"你好哦~"

import asyncio
from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Text, Image
from framework_common.framework_util.hot_reload import event_handler
from framework_common.database_util.User import get_user
from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from developTools.message.message_components import Text, Image
import traceback

# 假设 ExtendBot, YAMLManager, GroupMessageEvent 是由框架提供的
# from bot_framework import ExtendBot, YAMLManager, GroupMessageEvent 
# (No actual import here as per instructions, assuming they are globally available or injected)

plugin_name = "GreetingPlugin"

async def handle_greeting(bot, event, config):
    """
    处理问候消息。如果用户发送 "你好"，则回复 "你好哦~"。
    """
    try:
        # 获取消息内容
        message = str(event.pure_text).strip()

        if message == "你好":
            # 发送文本消息
            await bot.send(event, "你好哦~")
    except Exception as e:
        print(f"Error in handle_greeting: {e}")
        traceback.print_exc()

def main(bot: 'ExtendBot', config: 'YAMLManager'):
    """
    插件的主入口函数，用于注册事件监听器。
    """
    try:
        # 使用标准的 @bot.on() 装饰器注册群消息事件监听
        # 框架会将 GroupMessageEvent 类型的事件传递给 decorated handler
        @bot.on('GroupMessageEvent') # Per instruction "请不要使用@bot.on('GroupMessageEvent')而是使用标准的@bot.on(GroupMessageEvent)" - this seems like a typo in my thought process.
                                   # The example says "@bot.on(GroupMessageEvent)" which means passing the class, not a string.
                                   # I will correct this.
                                   # If GroupMessageEvent is not defined, this will cause an error.
                                   # Given the context, it should be `GroupMessageEvent` the class, not the string 'GroupMessageEvent'.
                                   # Let's assume GroupMessageEvent is available.
        async def group_message_handler(event: 'GroupMessageEvent'): # Type hint for event
            """
            异步处理接收到的群消息。
            """
            try:
                # 调用核心处理函数
                await handle_greeting(bot, event, config)
                # 对于处理结果，可以根据需要进行进一步操作，但 handle_greeting 目前不返回特定结果
            except Exception as e:
                print(f"Error in group_message_handler: {e}")
                traceback.print_exc()
        
        # print(f"✅ {plugin_name}插件加载成功。") # Optional: for confirmation, but not requested in output format

    except Exception as e:
        print(f"❌ {plugin_name}插件加载失败: {e}")
        traceback.print_exc()

# Correcting the @bot.on decorator based on the example's specific instruction:
# "请不要使用@bot.on('GroupMessageEvent')而是使用标准的@bot.on(GroupMessageEvent)"
# This means I need `GroupMessageEvent` to be an actual class reference.
# The problem prompt's example structure is:
# @bot.on(GroupMessageEvent)
# async def Messagehandler(event):
# This implies GroupMessageEvent is a known type.

# Re-generating with the corrected decorator usage.
# I will assume `GroupMessageEvent` is an imported or globally available type.
# If it's not, the code would need `from some_framework_module import GroupMessageEvent`.
# Since I'm only returning the code, I'll write it as if `GroupMessageEvent` is resolvable.

# Final refined code:

import traceback

# It's assumed that ExtendBot, YAMLManager, and GroupMessageEvent are provided by the bot framework.
# For example:
# from qqbot.core.robot import ExtendBot
# from qqbot.core.config import YAMLManager
# from qqbot.model.events import GroupMessageEvent 
# (These imports are commented out as per instruction to only return executable Python functions,
#  and assuming these types are available in the execution scope.)

plugin_name = "GreetingPlugin"

async def handle_greeting_logic(bot, event, config):
    """
    Core logic for handling greetings.
    Responds "你好哦~" if the message is "你好".
    """
    try:
        message = str(event.pure_text).strip()
        if message == "你好":
            await bot.send(event, "你好哦~")
    except AttributeError as e:
        # Handle cases where event might not have pure_text, or bot might not have send
        # This is a basic safeguard, more specific error handling might be needed depending on the framework
        print(f"Error processing event: Missing attribute - {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"An unexpected error occurred in handle_greeting_logic: {e}")
        traceback.print_exc()

def main(bot: 'ExtendBot', config: 'YAMLManager'):
    """
    Main function for the plugin. Registers event handlers.
    """
    try:
        # Using the standard @bot.on() decorator with the event class
        # Assumes GroupMessageEvent is an available type (e.g., imported from the framework)
        @bot.on(GroupMessageEvent) # Corrected: Using the class GroupMessageEvent directly
        async def group_message_event_handler(event: 'GroupMessageEvent'):
            """
            Handles incoming group messages.
            """
            try:
                # Call the specific logic function, passing bot, event, and config
                await handle_greeting_logic(bot, event, config)
            except Exception as e:
                # Error handling within the event handler itself
                print(f"Error in group_message_event_handler: {e}")
                traceback.print_exc()
        
        # You could add a log here to confirm loading if desired, e.g.:
        # print(f"✅ {plugin_name} loaded successfully and listening for greetings.")

    except Exception as e:
        # This handles errors during the setup phase (e.g., if @bot.on fails)
        print(f"❌ Failed to load {plugin_name}: {e}")
        traceback.print_exc()

# Note: The type hints 'ExtendBot', 'YAMLManager', 'GroupMessageEvent' are strings
# to avoid NameError if these types are not explicitly imported at the top level.
# In a real framework environment, you would typically have:
# from your_framework.bot import ExtendBot
# from your_framework.config import YAMLManager
# from your_framework.events import GroupMessageEvent
# And then you could use them directly in type hints without quotes.
