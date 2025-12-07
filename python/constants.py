# python/constants.py
"""
应用程序常量配置
"""
import os
from typing import Any, Dict


class UIConstants:
    """UI相关常量"""
    # 窗口尺寸
    WINDOW_WIDTH = 1370
    WINDOW_HEIGHT = 730

    # 布局比例
    CONTROL_PANEL_WIDTH = 240

    # 边距和内边距
    WINDOW_MARGIN = 10
    PANEL_PADDING = 15
    ELEMENT_SPACING = 10
    BUTTON_SPACING = 8

    # 字体大小
    FONT_SIZE_SMALL = 12
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_LARGE = 16
    FONT_SIZE_TITLE = 18
    FONT_SIZE_XLARGE = 22

    # 控件高度
    LABEL_HEIGHT = 30
    BUTTON_HEIGHT_SMALL = 40
    BUTTON_HEIGHT_NORMAL = 45
    BUTTON_HEIGHT_LARGE = 50
    BUTTON_WIDTH_SMALL = 80
    BUTTON_WIDTH_NORMAL = 120
    BUTTON_WIDTH_LARGE = 200

    # 面板高度（相对值）
    INFO_PANEL_HEIGHT = 200
    CONTROL_PANEL_HEIGHT = 242
    FUNCTION_PANEL_HEIGHT = 242

    # 背景颜色
    BACKGROUND_COLOR = (240, 240, 240)
    PANEL_BACKGROUND_COLOR = (220, 220, 220)
    BORDER_COLOR = (180, 180, 180)

    @classmethod
    def calculate_layout(cls, window_width: int, window_height: int) -> Dict[str, Any]:
        """根据窗口大小计算布局尺寸"""
        # 计算控制面板和迷宫面板宽度
        control_panel_width = cls.CONTROL_PANEL_WIDTH
        maze_panel_width = window_width - control_panel_width

        # 计算面板内实际可用宽度（减去边距）
        control_content_width = control_panel_width - 2 * cls.WINDOW_MARGIN - 6

        # 计算各面板高度
        info_panel_height = cls.INFO_PANEL_HEIGHT
        control_panel_height_px = cls.CONTROL_PANEL_HEIGHT
        function_panel_height = cls.FUNCTION_PANEL_HEIGHT

        # 计算按钮网格布局
        grid_cell_size = min(cls.BUTTON_WIDTH_NORMAL,
                             control_content_width // 3 - cls.BUTTON_SPACING * 2)
        grid_center_x = control_content_width // 2

        return {
            'window_width': window_width,
            'window_height': window_height,
            'control_panel_width': control_panel_width,
            'maze_panel_width': maze_panel_width,
            'control_content_width': control_content_width,
            'info_panel_height': info_panel_height,
            'control_panel_height': control_panel_height_px,
            'function_panel_height': function_panel_height,
            'grid_cell_size': grid_cell_size,
            'grid_center_x': grid_center_x
        }


class GameConstants:
    """游戏相关常量"""
    # 迷宫尺寸
    MAZE_WIDTH = 55
    MAZE_HEIGHT = 35
    MAZE_MIN_SCALE = 0.5
    MAZE_MAX_SCALE = 2.0

    # 迷宫渲染
    CELL_SIZE = 20
    MIN_CELL_SIZE = 10
    MAX_CELL_SIZE = 40
    MAZE_PADDING = 40
    MIN_SCALE = 0.5
    MAX_SCALE = 2.0


class ColorConstants:
    """颜色常量"""
    # 迷宫颜色
    WALL = (44, 62, 80)  # 深蓝灰
    PATH = (236, 240, 241)  # 浅灰
    PLAYER = (231, 76, 60)  # 红色
    EXIT = (46, 204, 113)  # 绿色
    GRID = (189, 195, 199)  # 网格线

    # UI颜色
    TEXT_PRIMARY = (52, 73, 94)  # 深灰色文本
    TEXT_SECONDARY = (127, 140, 141)  # 中灰色文本
    TEXT_DISABLED = (149, 165, 166)  # 浅灰色文本
    TEXT_LIGHT = (236, 240, 241)  # 白色文本

    # 按钮颜色
    BUTTON_NORMAL = (52, 152, 219)  # 蓝色按钮
    BUTTON_HOVER = (41, 128, 185)  # 深蓝色按钮
    BUTTON_PRESSED = (32, 102, 148)  # 更深的蓝色按钮
    BUTTON_DISABLED = (189, 195, 199)  # 灰色按钮

    # 面板颜色
    PANEL_BG = (220, 220, 220)
    PANEL_BORDER = (180, 180, 180)

    # 状态颜色
    STATUS_PLAYING = (52, 152, 219)  # 蓝色
    STATUS_COMPLETED = (46, 204, 113)  # 绿色
    STATUS_ERROR = (231, 76, 60)  # 红色


class UIContent:
    """UI文本内容"""
    # 窗口标题
    WINDOW_TITLE = "迷宫AI游戏 - API地址：{host}"

    # 游戏信息面板
    GAME_INFO_TITLE = "游戏信息"
    MOVE_COUNT_LABEL = "移动次数: {count}"
    STATUS_LABEL = "状态: {status}"
    POSITION_LABEL = "玩家: ({col}, {row})"
    EXIT_LABEL = "出口: ({col}, {row})"
    STATUS_PLAYING = "进行中"
    STATUS_COMPLETED = "已完成"

    # 控制面板
    CONTROL_TITLE = "方向控制"
    UP_BUTTON = "上"
    DOWN_BUTTON = "下"
    LEFT_BUTTON = "左"
    RIGHT_BUTTON = "右"
    WAIT_BUTTON = "等待"

    # 功能面板
    FUNCTION_TITLE = "游戏操作"
    RESET_BUTTON = "重置当前关卡"
    NEW_LEVEL_BUTTON = "生成新关卡"

    # 按钮提示
    KEYBOARD_HINT = "键盘快捷键: W/A/S/D 或方向键移动，R 重置，N 新关卡"


class ResourcePaths:
    """资源文件路径"""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
    FONT_FILE = os.path.join(RESOURCES_DIR, "HarmonyOS_SansSC_Regular.ttf")
    UI_STRINGS_FILE = os.path.join(RESOURCES_DIR, "ui_strings.properties")

    @classmethod
    def ensure_resources_dir(cls):
        """确保资源目录存在"""
        if not os.path.exists(cls.RESOURCES_DIR):
            os.makedirs(cls.RESOURCES_DIR)


class ServerConstants:
    """服务器相关常量"""
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8080
    MIN_PORT = 1024
    MAX_PORT = 65535
    PORT_RANGE = 100
