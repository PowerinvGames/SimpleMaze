# python/ui/scenes/SplashScene.py
"""
启动画面场景
"""
import threading
import time
from typing import Any, Dict, Optional

import pygame

from python.logger import logger
from python.ui.SceneManager import Scene


class SplashScene(Scene):
    """启动画面场景"""

    def __init__(self, name: str, scene_manager):
        super().__init__(name, scene_manager)

        # 服务器启动完成回调
        self.on_servers_ready = None

        # 场景状态
        self.start_time = 0
        self.min_display_time = 2.0  # 最少显示2秒
        self.display_duration = 3.0  # 计划显示3秒
        self.servers_ready = False
        self.main_scene_ready = False

        # 服务器启动状态
        self.http_server_ready = False
        self.mcp_server_ready = False

        # UI元素
        self.font_large = None
        self.font_normal = None
        self.font_small = None
        self.logo = None
        self.animation_progress = 0.0

        # 服务器启动线程
        self.server_start_thread = None

    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """进入场景"""
        logger.info("进入Splash场景")

        # 从data中获取回调函数
        if data:
            self.on_servers_ready = data.get('on_servers_ready')
            start_servers_func = data.get('start_servers')
        else:
            logger.warning("Splash场景未收到数据")
            return

        # 初始化时间
        self.start_time = time.time()

        # 初始化字体
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # 重置状态
        self.animation_progress = 0.0
        self.servers_ready = False

        # 在新线程中启动服务器
        if start_servers_func:
            self.server_start_thread = threading.Thread(
                target=self._start_servers_in_thread,
                args=(start_servers_func,),
                daemon=True,
                name="Server-Start-Thread"
            )
            self.server_start_thread.start()
        else:
            logger.warning("未提供服务器启动函数，将跳过服务器启动")
            self.servers_ready = True

    def on_exit(self) -> None:
        """退出场景"""
        logger.info("退出Splash场景")

    def _start_servers_in_thread(self, start_servers_func):
        """在新线程中启动服务器"""
        try:
            logger.info("开始启动服务器...")

            # 调用服务器启动函数
            start_servers_func()

            # 标记服务器已就绪
            self.servers_ready = True
            logger.info("服务器启动完成")

        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
            # 即使失败也标记为就绪，避免卡在启动画面
            self.servers_ready = True

    def _check_ready_to_switch(self) -> bool:
        """检查是否可以切换到主场景"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # 检查条件：
        # 1. 已经显示了最少时间
        # 2. 服务器已就绪
        if (elapsed_time >= self.min_display_time and
                self.servers_ready):
            return True

        return False

    def handle_events(self, events) -> None:
        """处理事件"""
        for event in events:
            # 允许用户跳过启动画面
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                logger.info("用户跳过启动画面")
                # 强制标记服务器已就绪，允许切换
                self.servers_ready = True

    def update(self, dt: float) -> None:
        """更新场景逻辑"""
        # 更新动画进度
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.animation_progress = min(elapsed_time / self.display_duration, 1.0)

        # 检查是否可以切换到主场景
        if self._check_ready_to_switch():
            logger.info("条件满足，准备切换到主游戏场景")

            # 通过回调通知ApplicationController切换到主游戏场景
            if self.on_servers_ready:
                self.on_servers_ready()
            else:
                # 如果没有回调，直接通过场景管理器切换（不带数据）
                logger.warning("没有找到服务器就绪回调，将直接切换场景")
                self.scene_manager.switch_to("main_game")

    def draw(self, screen: pygame.Surface) -> None:
        """绘制启动画面"""
        # 清屏 - 使用渐变色背景
        bg_color = (25, 35, 45)
        screen.fill(bg_color)

        # 获取屏幕尺寸
        screen_width, screen_height = screen.get_size()

        # 绘制Logo或游戏标题
        title = self.font_large.render("迷宫AI大冒险", True, (220, 220, 220))
        title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
        screen.blit(title, title_rect)

        # 绘制副标题
        subtitle = self.font_normal.render("AI Maze Adventure", True, (180, 180, 200))
        subtitle_rect = subtitle.get_rect(center=(screen_width // 2, screen_height // 2 + 10))
        screen.blit(subtitle, subtitle_rect)

        # 绘制加载状态
        loading_text = "服务端启动中" if not self.servers_ready else "服务端已就绪"
        loading_color = (255, 200, 100) if not self.servers_ready else (100, 255, 150)
        loading = self.font_normal.render(loading_text, True, loading_color)
        loading_rect = loading.get_rect(center=(screen_width // 2, screen_height // 2 + 80))
        screen.blit(loading, loading_rect)

        # 绘制加载进度条
        bar_width = 300
        bar_height = 20
        bar_x = (screen_width - bar_width) // 2
        bar_y = screen_height // 2 + 130

        # 进度条背景
        pygame.draw.rect(screen, (60, 60, 70), (bar_x, bar_y, bar_width, bar_height), border_radius=10)

        # 进度条前景
        progress_width = int(bar_width * self.animation_progress)
        if progress_width > 0:
            # 使用渐变色
            for i in range(progress_width):
                color_value = int(100 + 155 * (i / progress_width))
                pygame.draw.rect(screen, (color_value, 150, 255),
                                 (bar_x + i, bar_y, 1, bar_height))

        # 进度条边框
        pygame.draw.rect(screen, (100, 100, 120), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=10)

        # 绘制服务器状态
        server_status = []
        if self.servers_ready:
            server_status.append("✓ 所有服务已就绪")
        else:
            server_status.append("⏳ 正在启动服务器...")

        # 绘制状态信息
        for i, status in enumerate(server_status):
            status_surface = self.font_small.render(status, True, (180, 180, 200))
            status_rect = status_surface.get_rect(center=(screen_width // 2, bar_y + 40 + i * 25))
            screen.blit(status_surface, status_rect)

        # 绘制提示文字
        if not self.servers_ready:
            hint = self.font_small.render("按任意键跳过...", True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(screen_width // 2, screen_height - 50))
            screen.blit(hint, hint_rect)

        # 绘制版权信息
        copyright_text = self.font_small.render("© 2024 迷宫AI游戏 | AI Generated Project", True, (120, 120, 140))
        copyright_rect = copyright_text.get_rect(center=(screen_width // 2, screen_height - 20))
        screen.blit(copyright_text, copyright_rect)
