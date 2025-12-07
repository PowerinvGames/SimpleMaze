# python/ui/components/ControlPanel.py
"""
方向控制面板组件 - 修复鼠标悬停触发问题
"""
from typing import Callable

import pygame
import pygame_gui

from python.constants import *
from python.logger import logger


class ControlPanel:
    """方向控制面板"""

    def __init__(self, ui_manager: pygame_gui.UIManager, container_rect: pygame.Rect,
                 on_direction_selected: Callable[[str], None],
                 container: pygame_gui.elements.UIPanel = None):
        """
        初始化控制面板

        Args:
            ui_manager: UI管理器
            container_rect: 面板位置和大小
            on_direction_selected: 方向选择回调函数
            container: 父容器（可选）
        """
        self.manager = ui_manager
        self.container = container
        self.container_rect = container_rect
        self.on_direction_selected = on_direction_selected

        # 计算内容区域
        self.content_width = container_rect.width - 2 * UIConstants.PANEL_PADDING
        self.content_height = container_rect.height - 2 * UIConstants.PANEL_PADDING

        # UI元素字典
        self.ui_elements = {}

        # 按钮映射
        self.button_mapping = {}

        # 按钮状态跟踪
        self.button_states = {}

        # 创建面板
        self._create_panel()
        self._create_content()

        logger.debug("方向控制面板初始化完成")

    def _create_panel(self):
        """创建面板容器"""
        if self.container:
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                container=self.container,
                object_id='#ctrl_panel'
            )
        else:
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                object_id='#ctrl_panel'
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
            text=UIContent.CONTROL_TITLE,
            manager=self.manager,
            container=panel,
            object_id='#title_label'
        )

        # 计算按钮布局
        button_area_height = self.content_height - title_height - UIConstants.ELEMENT_SPACING
        button_size = self._calculate_button_size(button_area_height)

        # 计算按钮位置（网格布局）
        grid_width = 3 * button_size + 2 * UIConstants.BUTTON_SPACING
        grid_height = 3 * button_size + 2 * UIConstants.BUTTON_SPACING
        grid_x = (self.content_width - grid_width) // 2 + UIConstants.PANEL_PADDING
        grid_y = UIConstants.PANEL_PADDING + title_height + (button_area_height - grid_height) // 2

        # 创建方向按钮网格
        self._create_button_grid(panel, grid_x, grid_y, button_size)

    def _calculate_button_size(self, available_height: int) -> int:
        """计算按钮大小"""
        # 按钮区域可以容纳3个按钮和2个间距
        max_button_size = (available_height - 2 * UIConstants.BUTTON_SPACING) // 3

        # 限制按钮大小范围
        min_size = min(UIConstants.BUTTON_WIDTH_SMALL, max_button_size)
        max_size = min(UIConstants.BUTTON_WIDTH_NORMAL, max_button_size)

        # 取合适的尺寸
        button_size = max(min_size, max_size // 2)

        # 确保不会超过内容宽度
        max_content_width = (self.content_width - 2 * UIConstants.BUTTON_SPACING) // 3
        button_size = min(button_size, max_content_width)

        return button_size

    def _create_button_grid(self, panel: pygame_gui.elements.UIPanel,
                            grid_x: int, grid_y: int, button_size: int):
        """创建按钮网格"""
        spacing = UIConstants.BUTTON_SPACING

        # 上按钮 (1, 1)
        self.ui_elements['btn_up'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                grid_x + button_size + spacing,
                grid_y,
                button_size,
                button_size
            ),
            text=UIContent.UP_BUTTON,
            manager=self.manager,
            container=panel,
            object_id='#btn_up'
        )
        self.button_mapping[self.ui_elements['btn_up']] = 'up'
        self.button_states[self.ui_elements['btn_up']] = {'pressed': False, 'hover': False}

        # 左按钮 (2, 0)
        self.ui_elements['btn_left'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                grid_x,
                grid_y + button_size + spacing,
                button_size,
                button_size
            ),
            text=UIContent.LEFT_BUTTON,
            manager=self.manager,
            container=panel,
            object_id='#btn_left'
        )
        self.button_mapping[self.ui_elements['btn_left']] = 'left'
        self.button_states[self.ui_elements['btn_left']] = {'pressed': False, 'hover': False}

        # 等待按钮 (2, 1)
        self.ui_elements['btn_wait'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                grid_x + button_size + spacing,
                grid_y + button_size + spacing,
                button_size,
                button_size
            ),
            text=UIContent.WAIT_BUTTON,
            manager=self.manager,
            container=panel
        )
        self.button_mapping[self.ui_elements['btn_wait']] = 'wait'
        self.button_states[self.ui_elements['btn_wait']] = {'pressed': False, 'hover': False}

        # 右按钮 (2, 2)
        self.ui_elements['btn_right'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                grid_x + 2 * (button_size + spacing),
                grid_y + button_size + spacing,
                button_size,
                button_size
            ),
            text=UIContent.RIGHT_BUTTON,
            manager=self.manager,
            container=panel,
            object_id='#btn_right'
        )
        self.button_mapping[self.ui_elements['btn_right']] = 'right'
        self.button_states[self.ui_elements['btn_right']] = {'pressed': False, 'hover': False}

        # 下按钮 (3, 1)
        self.ui_elements['btn_down'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                grid_x + button_size + spacing,
                grid_y + 2 * (button_size + spacing),
                button_size,
                button_size
            ),
            text=UIContent.DOWN_BUTTON,
            manager=self.manager,
            container=panel,
            object_id='#btn_down'
        )
        self.button_mapping[self.ui_elements['btn_down']] = 'down'
        self.button_states[self.ui_elements['btn_down']] = {'pressed': False, 'hover': False}

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
            # 重新计算布局
            self.container_rect = pygame.Rect(self.container_rect.topleft, dimensions)
            self.content_width = dimensions[0] - 2 * UIConstants.PANEL_PADDING
            self.content_height = dimensions[1] - 2 * UIConstants.PANEL_PADDING

    def handle_event(self, event) -> bool:
        """
        处理事件

        Returns:
            是否处理了事件
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.button_mapping:
                direction = self.button_mapping[event.ui_element]
                logger.debug(f"方向按钮点击: {direction}")

                if self.on_direction_selected:
                    self.on_direction_selected(direction)

                return True

        return False

    def update(self, time_delta: float):
        """更新面板状态"""
        # 控制面板不需要每帧更新
        pass

    def kill(self):
        """销毁面板"""
        for element in self.ui_elements.values():
            if hasattr(element, 'kill'):
                element.kill()
        self.ui_elements.clear()
        self.button_mapping.clear()
        self.button_states.clear()
