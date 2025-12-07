# python/ui/SceneManager.py
"""
场景管理器 - 管理场景切换和生命周期
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pygame


class Scene(ABC):
    """场景基类"""

    def __init__(self, name: str, scene_manager: 'SceneManager'):
        self.name = name
        self.scene_manager = scene_manager
        self.initialized = False

    @abstractmethod
    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """进入场景时调用"""
        pass

    @abstractmethod
    def on_exit(self) -> None:
        """退出场景时调用"""
        pass

    @abstractmethod
    def handle_events(self, events) -> None:
        """处理事件"""
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        """更新场景逻辑"""
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """绘制场景"""
        pass


class SceneManager:
    """场景管理器"""

    def __init__(self):
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[str] = None
        self.transition_data: Optional[Dict[str, Any]] = None

    def add_scene(self, scene: Scene) -> None:
        """添加场景"""
        self.scenes[scene.name] = scene

    def switch_to(self, scene_name: str, data: Optional[Dict[str, Any]] = None) -> None:
        """切换到指定场景"""
        if scene_name in self.scenes:
            self.next_scene = scene_name
            self.transition_data = data

    def _perform_switch(self) -> None:
        """执行场景切换"""
        if self.next_scene and self.next_scene in self.scenes:
            # 退出当前场景
            if self.current_scene:
                self.current_scene.on_exit()

            # 进入新场景
            self.current_scene = self.scenes[self.next_scene]
            self.current_scene.on_enter(self.transition_data)

            # 重置切换状态
            self.next_scene = None
            self.transition_data = None

    def update(self, dt: float) -> None:
        """更新场景管理器"""
        # 检查是否需要切换场景
        if self.next_scene:
            self._perform_switch()

        # 更新当前场景
        if self.current_scene:
            self.current_scene.update(dt)

    def handle_events(self, events) -> None:
        """处理事件"""
        if self.current_scene:
            self.current_scene.handle_events(events)

    def draw(self, screen: pygame.Surface) -> None:
        """绘制当前场景"""
        if self.current_scene:
            self.current_scene.draw(screen)

    def get_current_scene(self) -> Optional[Scene]:
        """获取当前场景"""
        return self.current_scene
