# python/utils/FontManager.py
"""
字体管理器 - 专门处理pygame-gui字体问题
"""
import os
from typing import Any, Dict

import pygame

from python.constants import ResourcePaths
from python.logger import logger


class FontManager:
    """字体管理器类"""

    def __init__(self):
        self.font_path = None
        self._load_font()

    def _load_font(self):
        """加载字体文件"""
        # 优先使用项目字体
        if os.path.exists(ResourcePaths.FONT_FILE):
            self.font_path = ResourcePaths.FONT_FILE
            logger.info(f"使用项目字体: {self.font_path}")
        else:
            # 备选系统字体
            system_fonts = [
                "C:/Windows/Fonts/msyh.ttc",  # Windows微软雅黑
                "C:/Windows/Fonts/simsun.ttc",  # Windows宋体
                "/System/Library/Fonts/PingFang.ttc",  # macOS苹方
            ]

            for font in system_fonts:
                if os.path.exists(font):
                    self.font_path = font
                    logger.info(f"使用系统字体: {self.font_path}")
                    break

        if not self.font_path:
            logger.warning("未找到字体文件，将使用pygame-gui默认字体")

    def get_theme_config(self) -> Dict[str, Any]:
        """获取字体主题配置"""
        if not self.font_path:
            return {}

        return {
            'font_name': 'custom_font',
            'font_size': 14,
            'font_file': self.font_path,
            'bold_font_file': self.font_path,
            'italic_font_file': self.font_path,
            'bold_italic_font_file': self.font_path,
        }

    def setup_ui_manager_fonts(self, ui_manager) -> bool:
        """
        为pygame-gui UI管理器设置字体

        Args:
            ui_manager: pygame_gui.UIManager实例

        Returns:
            是否成功设置字体
        """
        try:
            if not self.font_path or not os.path.exists(self.font_path):
                logger.warning("字体文件不存在，使用默认字体")
                return False

            # 测试字体是否能被pygame加载
            test_font = pygame.font.Font(self.font_path, 14)
            test_surface = test_font.render("测试", True, (0, 0, 0))

            if test_surface.get_width() == 0:
                logger.warning("字体渲染测试失败")
                return False

            # 为pygame-gui添加字体路径
            ui_manager.add_font_paths(
                font_name='custom_font',
                regular_path=self.font_path,
                bold_path=self.font_path,
                italic_path=self.font_path,
                bold_italic_path=self.font_path
            )

            # 预加载常用字体尺寸
            font_sizes = [12, 14, 16, 18, 20, 22]
            for size in font_sizes:
                ui_manager.preload_fonts([
                    {'name': 'custom_font', 'point_size': size, 'style': 'regular'},
                    {'name': 'custom_font', 'point_size': size, 'style': 'bold'},
                ])

            # 创建主题配置
            theme_data = {
                "default": {
                    "font": {
                        "name": "custom_font",
                        "size": 14,
                        "bold": False,
                        "italic": False
                    }
                },
                "label": {
                    "font": {
                        "name": "custom_font",
                        "size": 14,
                        "bold": False,
                        "italic": False
                    }
                },
                "button": {
                    "font": {
                        "name": "custom_font",
                        "size": 14,
                        "bold": False,
                        "italic": False
                    }
                },
                "#title_label": {
                    "font": {
                        "name": "custom_font",
                        "size": 18,
                        "bold": True,
                        "italic": False
                    }
                },
            }

            # 应用主题
            ui_manager.get_theme().load_theme(theme_data)

            logger.info("UI字体设置成功")
            return True

        except Exception as e:
            logger.error(f"设置UI字体失败: {e}")
            return False

    def create_pygame_font(self, size: int = 14) -> pygame.font.Font:
        """创建pygame字体对象（用于非UI渲染）"""
        try:
            if self.font_path and os.path.exists(self.font_path):
                return pygame.font.Font(self.font_path, size)
        except Exception as e:
            logger.error(f"创建pygame字体失败: {e}")

        # 回退到系统字体
        return pygame.font.SysFont(None, size)
