# python/ui/components/FunctionPanel.py
"""
功能面板组件
"""
import pygame
import pygame_gui
from typing import Callable, Dict
from python.constants import *
from python.logger import logger


class FunctionPanel:
    """功能操作面板"""

    def __init__(self, ui_manager: pygame_gui.UIManager, container_rect: pygame.Rect,
                 on_reset: Callable[[], None],
                 on_new_level: Callable[[], None],
                 container: pygame_gui.elements.UIPanel = None):
        """
        初始化功能面板

        Args:
            ui_manager: UI管理器
            container_rect: 面板位置和大小
            on_reset: 重置回调函数
            on_new_level: 新关卡回调函数
            container: 父容器（可选）
        """
        self.manager = ui_manager
        self.container = container
        self.container_rect = container_rect
        self.on_reset = on_reset
        self.on_new_level = on_new_level

        # 计算内容区域
        self.content_width = container_rect.width - 2 * UIConstants.PANEL_PADDING
        self.content_height = container_rect.height - 2 * UIConstants.PANEL_PADDING

        # UI元素字典
        self.ui_elements = {}

        # 创建面板
        self._create_panel()
        self._create_content()

        logger.debug("功能操作面板初始化完成")

    def _create_panel(self):
        """创建面板容器"""
        if self.container:
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                container=self.container,
                object_id='#func_panel'
            )
        else:
            self.ui_elements['panel'] = pygame_gui.elements.UIPanel(
                relative_rect=self.container_rect,
                manager=self.manager,
                object_id='#func_panel'
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
            text=UIContent.FUNCTION_TITLE,
            manager=self.manager,
            container=panel,
            object_id='#title_label'
        )

        # 计算按钮布局 - 现在只有2个按钮
        button_area_height = self.content_height - title_height - UIConstants.ELEMENT_SPACING
        button_height = self._calculate_button_height(button_area_height)

        # 按钮宽度（填满内容宽度）
        button_width = self.content_width

        # 计算按钮垂直间距 - 2个按钮，有3个间距（顶部、中间、底部）
        button_spacing = (button_area_height - 2 * button_height) // 3

        # 按钮起始Y坐标
        button_y = UIConstants.PANEL_PADDING + title_height + button_spacing

        # 创建功能按钮 - 只有重置和新关卡
        self.ui_elements['btn_reset'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                button_y,
                button_width,
                button_height
            ),
            text=UIContent.RESET_BUTTON,
            manager=self.manager,
            container=panel
        )

        self.ui_elements['btn_new'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                UIConstants.PANEL_PADDING,
                button_y + button_height + button_spacing,
                button_width,
                button_height
            ),
            text=UIContent.NEW_LEVEL_BUTTON,
            manager=self.manager,
            container=panel
        )

    def _calculate_button_height(self, available_height: int) -> int:
        """计算按钮高度"""
        # 有2个按钮和3个间距
        max_button_height = (available_height - 2 * UIConstants.BUTTON_SPACING) // 2

        # 限制按钮高度范围
        button_height = min(max_button_height, UIConstants.BUTTON_HEIGHT_NORMAL)
        button_height = max(button_height, UIConstants.BUTTON_HEIGHT_SMALL)

        return button_height

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
            if event.ui_element == self.ui_elements['btn_reset']:
                logger.debug("重置按钮点击")
                if self.on_reset:
                    self.on_reset()
                return True

            elif event.ui_element == self.ui_elements['btn_new']:
                logger.debug("新关卡按钮点击")
                if self.on_new_level:
                    self.on_new_level()
                return True

        return False

    def update(self, time_delta: float):
        """更新面板状态"""
        # 功能面板不需要每帧更新
        pass

    def kill(self):
        """销毁面板"""
        for element in self.ui_elements.values():
            if hasattr(element, 'kill'):
                element.kill()
        self.ui_elements.clear()
