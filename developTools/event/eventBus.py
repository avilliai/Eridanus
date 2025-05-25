"""
全局事件总线
提供全局的事件总线实例供热重载系统使用
"""

from .bus import EventBus

# 全局事件总线实例
event_bus = EventBus()

__all__ = ['event_bus']
