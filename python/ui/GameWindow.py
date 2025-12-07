# python/ui/GameWindow.py
"""
游戏主窗口 - 场景管理器容器
"""
import pygame

from python.logger import logger
from python.ui.SceneManager import SceneManager


class GameWindow:
    """游戏主窗口 - 场景管理器容器"""

    def __init__(self):
        self.screen = None
        self.clock = None
        self.scene_manager = None
        self.running = True

        logger.info("游戏窗口初始化开始")

    def initialize(self) -> None:
        """初始化窗口和场景管理器"""
        # 初始化pygame
        pygame.init()

        # 窗口设置
        from python.constants import UIConstants
        self.screen = pygame.display.set_mode(
            (UIConstants.WINDOW_WIDTH, UIConstants.WINDOW_HEIGHT)
        )
        pygame.display.set_caption("迷宫AI游戏 - 启动中...")

        # 创建时钟
        self.clock = pygame.time.Clock()

        # 创建场景管理器
        self.scene_manager = SceneManager()

        logger.info("游戏窗口初始化完成")

    def add_scene(self, scene) -> None:
        """添加场景到管理器"""
        self.scene_manager.add_scene(scene)

    def switch_to_scene(self, scene_name: str, data: dict = None) -> None:
        """切换到指定场景"""
        self.scene_manager.switch_to(scene_name, data)

    def run(self) -> None:
        """运行主循环"""
        logger.info("开始游戏主循环")

        while self.running:
            # 计算时间增量
            dt = self.clock.tick(60) / 1000.0

            # 处理事件
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            # 传递事件给场景管理器
            self.scene_manager.handle_events(events)

            # 更新场景管理器
            self.scene_manager.update(dt)

            # 绘制当前场景
            self.scene_manager.draw(self.screen)

            # 更新显示
            pygame.display.flip()

        # 清理资源
        self._cleanup()
        logger.info("游戏主循环结束")

    def _cleanup(self) -> None:
        """清理资源"""
        pygame.quit()
        logger.info("游戏窗口资源清理完成")

    def stop(self) -> None:
        """停止窗口运行"""
        self.running = False
