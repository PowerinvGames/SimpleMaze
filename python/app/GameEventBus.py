# python/app/GameEventBus.py
"""
游戏事件总线系统
"""
from enum import Enum
from typing import Any, Callable, Dict

from python.logger import logger


class EventType(Enum):
    """事件类型枚举"""
    GAME_STATE_UPDATED = "game_state_updated"
    PLAYER_MOVED = "player_moved"
    LEVEL_RESET = "level_reset"
    NEW_LEVEL_GENERATED = "new_level_generated"
    WINDOW_RESIZED = "window_resized"
    KEY_PRESSED = "key_pressed"
    BUTTON_CLICKED = "button_clicked"


class GameEvent:
    """游戏事件类"""

    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = time.time()

    def __str__(self) -> str:
        return f"GameEvent({self.event_type.value}, data={self.data})"


import time


class GameEventBus:
    """
    游戏事件总线 - 实现观察者模式
    用于解耦游戏逻辑与UI显示
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameEventBus, cls).__new__(cls)
            cls._instance._init_singleton()
        return cls._instance

    def _init_singleton(self):
        """初始化单例"""
        self._listeners: Dict[EventType, list] = {}
        self._event_history = []
        self._max_history_size = 100

    def subscribe(self, event_type: EventType, callback: Callable[[GameEvent], None]):
        """订阅事件"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            logger.debug(f"已订阅事件: {event_type.value}")

    def unsubscribe(self, event_type: EventType, callback: Callable[[GameEvent], None]):
        """取消订阅事件"""
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
                logger.debug(f"已取消订阅事件: {event_type.value}")

    def emit(self, event_type: EventType, data: Dict[str, Any] = None):
        """触发事件"""
        event = GameEvent(event_type, data)

        # 记录事件历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)

        # 通知订阅者
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"事件处理失败: {event_type.value}, 错误: {e}")

        logger.debug(f"事件已触发: {event}")

    def get_event_history(self) -> list:
        """获取事件历史"""
        return self._event_history.copy()

    def clear_event_history(self):
        """清空事件历史"""
        self._event_history.clear()

    def clear_all_listeners(self):
        """清空所有监听器"""
        self._listeners.clear()
        self.clear_event_history()
