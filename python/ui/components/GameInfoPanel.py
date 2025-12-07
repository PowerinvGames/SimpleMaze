# python/ui/components/GameInfoPanel.py
"""
游戏信息面板组件
"""
import pygame
import pygame_gui

from python.constants import *
from python.logger import logger


class GameInfoPanel:
    """游戏信息面板"""

    def __init__(self, ui_manager: pygame_gui.UIManager, container_rect: pygame.Rect,
                 container: pygame_gui.elements.UIPanel = None):
        """
        初始化游戏信息面板

        Args:
            ui_manager: UI管理器
            container_rect: 面板位置和大小
            container: 父容器（可选）
        """
        self.manager = ui_manager
        self.container = container
        self.container_rect = container_rect

        # 计算内容区域（减去内边距）
        self.content_width = container_rect.width - 2 * UIConstants.PANEL_PADDING
        self.content_height = container_rect.height - 2 * UIConstants.PANEL_PADDING

        # UI元素字典
        self.ui_elements = {}

        # 创建面板
        self._create_panel()
        self._create_content()

        logger.debug("游戏信息面板初始化完成")

    def _create_panel(self):
        """创建面板容器"""
        if self.container:
            # 如果提供了父容器，在容器内创建面板
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                container=self.container,
                object_id='#info_panel'
            )
        else:
            # 否则直接创建面板
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                object_id='#info_panel'
            )

    def _create_content(self):
        """创建面板内容"""
        panel = self.ui_elements['panel']

        # 标题
        title_height = UIConstants.LABEL_HEIGHT + 5
        self.ui_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                UIConstants.PANEL_PADDING,
                self.content_width,
                title_height
            ),
            text=UIContent.GAME_INFO_TITLE,
            manager=self.manager,
            container=panel,
            object_id='#title_label'
        )

        # 信息标签
        label_y = UIConstants.PANEL_PADDING + title_height + UIConstants.ELEMENT_SPACING
        label_height = (self.content_height - title_height - 5 * UIConstants.ELEMENT_SPACING) // 4

        # 移动次数
        self.ui_elements['move_count'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                label_y,
                self.content_width,
                label_height
            ),
            text=UIContent.MOVE_COUNT_LABEL.format(count=0),
            manager=self.manager,
            container=panel
        )

        # 状态
        self.ui_elements['status'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                label_y + label_height + UIConstants.ELEMENT_SPACING,
                self.content_width,
                label_height
            ),
            text=UIContent.STATUS_LABEL.format(status=UIContent.STATUS_PLAYING),
            manager=self.manager,
            container=panel
        )

        # 玩家位置
        self.ui_elements['position'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                label_y + 2 * (label_height + UIConstants.ELEMENT_SPACING),
                self.content_width,
                label_height
            ),
            text=UIContent.POSITION_LABEL.format(col=0, row=0),
            manager=self.manager,
            container=panel
        )

        # 出口位置
        self.ui_elements['exit'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                label_y + 3 * (label_height + UIConstants.ELEMENT_SPACING),
                self.content_width,
                label_height
            ),
            text=UIContent.EXIT_LABEL.format(col=0, row=0),
            manager=self.manager,
            container=panel
        )

    def update_game_state(self, game_state: Dict[str, Any]):
        """更新游戏状态显示"""
        try:
            if not game_state:
                return

            # 获取位置信息
            player_pos = game_state.get("player_position", {"col": 0, "row": 0})
            exit_pos = game_state.get("exit_position", {"col": 0, "row": 0})

            # 更新标签文本
            self.ui_elements['move_count'].set_text(
                UIContent.MOVE_COUNT_LABEL.format(count=game_state.get("move_count", 0))
            )

            status = UIContent.STATUS_COMPLETED if game_state.get("is_completed", False) else UIContent.STATUS_PLAYING
            self.ui_elements['status'].set_text(
                UIContent.STATUS_LABEL.format(status=status)
            )

            self.ui_elements['position'].set_text(
                UIContent.POSITION_LABEL.format(
                    col=player_pos.get("col", 0),
                    row=player_pos.get("row", 0)
                )
            )

            self.ui_elements['exit'].set_text(
                UIContent.EXIT_LABEL.format(
                    col=exit_pos.get("col", 0),
                    row=exit_pos.get("row", 0)
                )
            )

        except Exception as e:
            logger.error(f"更新游戏信息面板失败: {e}")

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
            # 重新计算内容布局
            self.container_rect = pygame.Rect(self.container_rect.topleft, dimensions)
            self.content_width = dimensions[0] - 2 * UIConstants.PANEL_PADDING
            self.content_height = dimensions[1] - 2 * UIConstants.PANEL_PADDING

    def handle_event(self, event) -> bool:
        """
        处理事件

        Returns:
            是否处理了事件
        """
        # 游戏信息面板不需要处理交互事件
        return False

    def update(self, time_delta: float):
        """更新面板状态"""
        # 游戏信息面板不需要每帧更新
        pass

    def kill(self):
        """销毁面板"""
        for element in self.ui_elements.values():
            if hasattr(element, 'kill'):
                element.kill()
        self.ui_elements.clear()
