import asyncio
import json
import os
import re
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from developTools.event.events import GroupMessageEvent, PrivateMessageEvent

from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from developTools.message.message_components import Text, Image
from framework_common.framework_util.hot_reload import event_handler, hot_reload_manager
from framework_common.database_util.User import get_user

# 复用现有的AI核心处理器
from run.ai_llm.service.aiReplyCore import aiReplyCore


class AICodeGenerator:
    """AI代码生成器 - 复用现有AI系统"""
    
    def __init__(self, config):
        self.config = config
        
        # 生成的代码保存目录
        self.generated_dir = Path("run/ai_generated")
        self.generated_dir.mkdir(exist_ok=True)
        
        # 代码模板
        self.plugin_template = '''# AI生成的插件代码
# 生成时间: {timestamp}

import asyncio
from developTools.event.events import GroupMessageEvent, PrivateMessageEvent
from developTools.message.message_components import Text, Image
from framework_common.framework_util.hot_reload import event_handler
from framework_common.database_util.User import get_user
from framework_common.database_util.User import get_user
from framework_common.framework_util.websocket_fix import ExtendBot
from framework_common.framework_util.yamlLoader import YAMLManager
from developTools.message.message_components import Text, Image
{generated_code}
'''
        
    async def generate_code(self, prompt: str, user_id: str) -> Optional[str]:
        """使用现有AI系统生成代码"""
        try:
            system_prompt = """你是一个专业的QQ机器人插件开发者。请根据用户需求生成Python代码。

要求：
1. 使用提供的框架结构和API
2. 代码必须是可执行的Python函数,请只返回可执行的Python代码，不要包含markdown标记和任何其他可能导致程序无法执行的内容。
3. 使用@event_handler装饰器注册事件监听
4. 函数参数包含: bot, event, config
6. 遵循异步编程规范 (async/await)
7. 包含适当的错误处理
8. 你可以生成不同的函数,但是函数这些函数最总需要在main函数中被调用
9. 返回的代码中需要包含main函数以及你生成的实现对应需求的函数

你需要回复的简单示例：
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
import aiohttp
import json
async def func(bot, event, config):
    # 获取消息内容
    message = str(event.pure_text).strip()
    # 处理逻辑...
    # 发送文本消息
    await bot.send(event, "消息内容")
    # 发送图片消息
    await bot.send(event, Image(file=path))
    # 图文一起发送
    await bot.send(event,[Text("文字内容"),Image(file=path)])

def main(bot: ExtendBot, config: YAMLManager):
    try:
        # 使用标准的 @bot.on() 装饰器 请不要使用@bot.on('GroupMessageEvent')而是使用标准的@bot.on(GroupMessageEvent)
        @bot.on(GroupMessageEvent)
        async def Messagehandler(event):
            try:
                result = await func(bot, event, config)
                # 对于处理结果，可以根据需要进行进一步操作
            except Exception as e:
                print(f"Error in AI code handler: {e}")
                traceback.print_exc()
    except Exception as e:
        print(f"❌ {plugin_name}插件加载失败: {e}")
        traceback.print_exc()
"""

            # 使用现有的AI核心处理器
            full_prompt = f"{system_prompt}\n\n用户需求：{prompt}"
            
            # 调用AI核心处理器
            response = await aiReplyCore(
                processed_message=[{"text": full_prompt}],
                user_id=user_id,
                config=self.config,
                system_instruction=system_prompt
            )
            
            if response and isinstance(response, dict):
                content = response.get("content", "")
                if isinstance(content, list):
                    content = " ".join([str(item) for item in content])
                return str(content).strip()
            elif response and isinstance(response, str):
                return response.strip()
            else:
                return None
                
        except Exception as e:
            print(f"Error generating code: {e}")
            traceback.print_exc()
            return None
            
    def validate_code(self, code: str) -> tuple[bool, str]:
        """验证生成的代码"""
        try:
            # 基本语法检查
            compile(code, '<string>', 'exec')
            
            # 检查必需的导入和装饰器
            if 'def main' not in code:
                return False, "代码缺少main函数定义"
            
            if '@bot.on(GroupMessageEvent)' not in code:
                return False, "代码缺少@bot.on(GroupMessageEvent)装饰器"
                
            if 'async def' not in code:
                return False, "代码缺少异步函数定义"
                
            # 检查危险操作
            dangerous_patterns = [
                r'import\s+os.*system',
                r'subprocess',
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__',
                r'open\s*\(.*(w|a).*\)',  # 写入文件操作
                r'rm\s+-rf',
                r'del\s+',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    return False, f"代码包含潜在危险操作: {pattern}"
                    
            return True, "代码验证通过"
            
        except SyntaxError as e:
            return False, f"语法错误: {e}"
        except Exception as e:
            return False, f"验证失败: {e}"
            
    async def save_and_reload_code(self, code: str, filename: str, user_request: str) -> tuple[bool, str]:
        """保存生成的代码并触发热重载"""
        try:
            # 生成完整的插件代码
            full_code = self.plugin_template.format(
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_request=user_request,
                generated_code=code
            )
            
            # 保存到文件
            plugin_file = self.generated_dir / f"{filename}.py"
            with open(plugin_file, 'w', encoding='utf-8') as f:
                f.write(full_code)
                
            # 等待文件写入完成
            await asyncio.sleep(1)
            
            # 触发热重载
            success = await hot_reload_manager.reload_plugin(str(plugin_file))
            
            if success:
                return True, f"代码已保存到 {plugin_file} 并成功重载"
            else:
                return False, f"代码已保存到 {plugin_file} 但重载失败"
                
        except Exception as e:
            return False, f"保存代码失败: {e}"


# 全局AI代码生成器实例
ai_generator: Optional[AICodeGenerator] = None


def init_ai_generator(config):
    """初始化AI代码生成器"""
    global ai_generator
    ai_generator = AICodeGenerator(config)


async def handle_ai_code_generation(bot, event, config):
    """处理AI代码生成请求"""
    try:
        # 初始化生成器
        if ai_generator is None:
            init_ai_generator(config)
            
        # 使用 event.pure_text 获取消息内容
        message = str(event.pure_text).strip()
        if not message:
            await bot.send(event, "消息内容为空")
            return False
            
        # 检查是否是代码生成请求
        if not message.startswith(("/ai生成", "/生成代码", "/gen")):
            return False
            
        # 获取用户信息和权限检查
        user_info = await get_user(event.user_id, event.sender.nickname)
        required_level = config.ai_code_generator.config.get("required_permission_level", 0)
        
        if user_info.permission < required_level:
            await bot.send(event, "权限不足，无法使用AI代码生成功能")
            return True
            
        # 解析请求
        parts = message.split(maxsplit=2)
        if len(parts) < 2:
            await bot.send(event, "使用方法: /ai生成 [文件名] [功能描述]\n例如: /ai生成 hello_plugin 实现一个打招呼的功能")
            return True
            
        if len(parts) == 2:
            filename = f"auto_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            prompt = parts[1]
        else:
            filename = parts[1]
            prompt = parts[2]
            
        # 文件名验证
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', filename):
            await bot.send(event, "文件名格式错误，只能包含字母、数字和下划线，且不能以数字开头")
            return True
            
        # 发送处理中消息
        await bot.send(event, "正在生成代码，请稍候...")
        
        # 调用AI生成代码
        generated_code = await ai_generator.generate_code(prompt, str(event.user_id))
        
        if not generated_code:
            await bot.send(event, "代码生成失败，请检查AI配置或稍后重试")
            return True
            
        # 清理markdown格式
        # 移除所有的```python或```标记
        generated_code = re.sub(r'```(?:python)?\s*\n?', '', generated_code, flags=re.MULTILINE)
        generated_code = re.sub(r'```\s*', '', generated_code, flags=re.MULTILINE)
        # 移除单独的"python"字样
        generated_code = re.sub(r'^python\s*$', '', generated_code, flags=re.MULTILINE)
        # 移除可能存在的多余空行
        generated_code = generated_code.strip()
            
        # 验证代码
        is_valid, validation_msg = ai_generator.validate_code(generated_code)
        if not is_valid:
            await bot.send(event, f"生成的代码验证失败: {validation_msg}")
            return True
            
        # 保存并重载代码
        success, save_msg = await ai_generator.save_and_reload_code(
            generated_code, filename, prompt
        )
        
        if success:
            await bot.send(event, f"✅ {save_msg}\n\n生成的代码预览:\n{generated_code[:500]}{'...' if len(generated_code) > 500 else ''}\n")
        else:
            await bot.send(event, f"❌ {save_msg}")
            
        return True
        
    except Exception as e:
        print(f"Error in AI code generation: {e}")
        traceback.print_exc()
        
        try:
            await bot.send(event, f"处理请求时发生错误: {str(e)}")
        except:
            pass
            
        return False


async def handle_reload_command(bot, event, config):
    """处理手动重载命令"""
    try:
        # 使用 event.pure_text 获取消息内容
        message = str(event.pure_text).strip()
        if not message:
            return False
            
        if not message.startswith(("/reload", "/重载")):
            return False
            
        # 权限检查
        user_info = await get_user(event.user_id, event.sender.nickname)
        if user_info.permission < 3:  # 需要管理员权限
            await bot.send(event, "权限不足，无法使用重载功能")
            return True
            
        parts = message.split(maxsplit=1)
        if len(parts) < 2:
            # 显示已加载的模块
            modules = hot_reload_manager.get_loaded_modules()
            module_list = "\n".join([f"- {mod}" for mod in modules[-10:]])  # 显示最近10个
            
            await bot.send(event, f"使用方法: /reload [插件名]\n\n最近加载的模块:\n{module_list}")
            return True
            
        plugin_name = parts[1]
        
        # 执行重载
        success = await hot_reload_manager.reload_plugin(plugin_name)
        
        if success:
            await bot.send(event, f"✅ 插件 {plugin_name} 重载成功")
        else:
            await bot.send(event, f"❌ 插件 {plugin_name} 重载失败")
            
        return True
        
    except Exception as e:
        print(f"Error in reload command: {e}")
        return False


async def handle_help_command(bot, event, config):
    """处理帮助命令"""
    try:
        # 使用 event.pure_text 获取消息内容
        message = str(event.pure_text).strip()
        if not message:
            return False
            
        if message not in ("/help", "/帮助", "/ai帮助"):
            return False
            
        help_text = """🤖 AI代码生成机器人帮助

📝 代码生成:
/ai生成 [文件名] [功能描述]
/生成代码 [文件名] [功能描述]
/gen [文件名] [功能描述]

例子:
/ai生成 hello_plugin 实现一个打招呼的功能
/ai生成 weather 查询天气信息

🔄 插件管理:
/reload [插件名] - 重载指定插件
/重载 [插件名] - 重载指定插件

⚠️ 注意事项:
- 需要管理员权限才能使用
- 生成的代码会自动验证安全性
- 支持热重载，无需重启机器人
- 文件名只能包含字母、数字和下划线
- AI模型配置复用现有ai_llm设置"""
        
        await bot.send(event, help_text)
        
        return True
        
    except Exception as e:
        print(f"Error in help command: {e}")
        return False


def main(bot: ExtendBot, config: YAMLManager):
    """插件主入口函数"""
    try:
        # 初始化AI代码生成器
        init_ai_generator(config)
        bot.logger.info("🔥 AI代码生成初始化/热重载成功")

        
        # 使用标准的 @bot.on() 装饰器
        @bot.on(GroupMessageEvent)
        async def ai_code_handler(event):
            """统一处理AI代码生成相关的消息"""
            #print(f"AI代码:: 收到消息: {event.pure_text} 来自 {event.user_id}")
            try:
                # 处理AI代码生成请求
                result = await handle_ai_code_generation(bot, event, config)
                if result:
                    return
                    
                # 处理重载命令
                result = await handle_reload_command(bot, event, config)
                if result:
                    return
                    
                # 处理帮助命令
                result = await handle_help_command(bot, event, config)
                if result:
                    return
                    
            except Exception as e:
                print(f"Error in AI code handler: {e}")
                traceback.print_exc()
        
    except Exception as e:
        print(f"❌ AI代码生成插件加载失败: {e}")
        traceback.print_exc()
