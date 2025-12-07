# python/ui/components/MazePanel.py
"""
迷宫显示面板组件
"""
import pygame
import pygame_gui

from python.core.game.MazeGameService import MazeGameService
from python.logger import logger
from python.ui.MazeRenderer import MazeRenderer


class MazePanel:
    """迷宫显示面板"""

    def __init__(self, ui_manager: pygame_gui.UIManager, container_rect: pygame.Rect,
                 game_service: MazeGameService, maze_renderer: MazeRenderer):
        """
        初始化迷宫显示面板

        Args:
            ui_manager: UI管理器
            container_rect: 面板位置和大小
            game_service: 游戏服务
            maze_renderer: 迷宫渲染器
        """
        self.manager = ui_manager
        self.container_rect = container_rect
        self.game_service = game_service
        self.maze_renderer = maze_renderer
        self.maze_surface = None

        # UI元素字典
        self.ui_elements = {}

        # 创建面板
        self._create_panel()

        # 初始刷新
        self._refresh_maze_surface()

        logger.debug("迷宫显示面板初始化完成")

    def _create_panel(self):
        """创建面板容器"""
        self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
            relative_rect=self.container_rect,
            manager=self.manager,
            object_id='#maze_panel'
        )

    def _refresh_maze_surface(self):
        """刷新迷宫Surface"""
        maze_data = self.game_service.get_maze_data()
        if not maze_data:
            return

        # 计算迷宫原始尺寸
        maze_width = maze_data.width * self.maze_renderer.cell_size
        maze_height = maze_data.height * self.maze_renderer.cell_size

        # 使用固定尺寸（原始尺寸）
        self.maze_surface = pygame.Surface((maze_width, maze_height), pygame.SRCALPHA)

        logger.debug(f"迷宫Surface创建: {maze_width}x{maze_height}")

    def update(self):
        """更新面板显示"""
        maze_data = self.game_service.get_maze_data()
        game_state = self.game_service.get_current_state()

        if maze_data and game_state and self.maze_surface:
            # 重新绘制迷宫
            self.maze_renderer.draw(maze_data, game_state, self.maze_surface)

    def draw(self, screen: pygame.Surface):
        """绘制迷宫到屏幕"""
        if not self.maze_surface:
            return

        # 获取面板位置和大小
        panel = self.ui_elements['panel']
        container_rect = panel.rect

        # 计算居中偏移
        surf_rect = self.maze_surface.get_rect()
        surf_rect.center = container_rect.center

        # 绘制到屏幕上
        screen.blit(self.maze_surface, surf_rect)

    def get_panel(self) -> pygame_gui.elements.UIPanel:
        """获取面板元素"""
        return self.ui_elements.get('panel')

    def set_position(self, position: tuple):
        """设置面板位置"""
        if 'panel' in self.ui_elements:
            self.ui_elements['panel'].set_relative_position(position)

    def set_dimensions(self, dimensions: tuple):
        """设置面板尺寸"""
        if 'panel' in self.ui_elements:
            self.ui_elements['panel'].set_dimensions(dimensions)
            self.container_rect = pygame.Rect(self.container_rect.topleft, dimensions)

    def handle_event(self, event) -> bool:
        """
        处理事件

        Returns:
            是否处理了事件
        """
        # 迷宫面板不需要处理交互事件
        return False

    def kill(self):
        """销毁面板"""
        for element in self.ui_elements.values():
            if hasattr(element, 'kill'):
                element.kill()
        self.ui_elements.clear()
