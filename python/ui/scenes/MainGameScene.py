# python/ui/scenes/MainGameScene.py
"""
主游戏场景 - 包含原来的GameWindow功能
"""
from typing import Optional

import pygame
import pygame_gui

from python.app.GameEventBus import EventType, GameEventBus
from python.constants import *
from python.core.game.MazeGameService import MazeGameService
from python.logger import logger
from python.server.HttpGameServer import HttpGameServer
from python.ui.MazeRenderer import MazeRenderer
from python.ui.SceneManager import Scene
from python.ui.components.ControlPanel import ControlPanel
from python.ui.components.FunctionPanel import FunctionPanel
from python.ui.components.GameInfoPanel import GameInfoPanel
from python.ui.components.MazePanel import MazePanel
from python.utils.FontManager import FontManager


class MainGameScene(Scene):
    """主游戏场景"""

    def __init__(self, name: str, scene_manager):
        super().__init__(name, scene_manager)

        # 游戏服务
        self.game_service: Optional[MazeGameService] = None
        self.http_server: Optional[HttpGameServer] = None

        # UI组件
        self.manager: Optional[pygame_gui.UIManager] = None
        self.font_manager: Optional[FontManager] = None
        self.maze_renderer: Optional[MazeRenderer] = None

        # UI组件
        self.components = {}
        self.ui_elements = {}

        # 事件总线
        self.event_bus = GameEventBus()

        # 窗口尺寸
        self.window_size = (UIConstants.WINDOW_WIDTH, UIConstants.WINDOW_HEIGHT)
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None

        # 布局
        self.layout: Optional[Dict[str, Any]] = None

        # 状态
        self.initialized = False
        self.running = True

    def on_enter(self, data: Optional[Dict[str, Any]] = None) -> None:
        """进入场景"""
        logger.info("进入主游戏场景")

        # 从data中获取游戏服务和服务器
        if data:
            self.game_service = data.get('game_service')
            self.http_server = data.get('http_server')

        if not self.game_service or not self.http_server:
            logger.error("主游戏场景缺少必要的游戏服务或HTTP服务器")
            return

        # 初始化pygame（如果尚未初始化）
        if not pygame.get_init():
            pygame.init()

        # 创建屏幕
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption(UIContent.WINDOW_TITLE.format(
            host=self.http_server.get_server_url() if self.http_server else "localhost:8080"
        ))

        # 创建时钟
        self.clock = pygame.time.Clock()

        # 初始化UI管理器
        self.manager = pygame_gui.UIManager(self.window_size)

        # 初始化字体管理器
        self.font_manager = FontManager()
        self.font_manager.setup_ui_manager_fonts(self.manager)

        # 计算布局
        self.layout = UIConstants.calculate_layout(*self.window_size)

        # 初始化迷宫渲染器
        self.maze_renderer = MazeRenderer(GameConstants.CELL_SIZE)

        # 创建UI组件
        self._create_ui_elements()

        # 订阅事件
        self._setup_event_listeners()

        # 初始刷新
        self._refresh_ui()

        self.initialized = True
        logger.info("主游戏场景初始化完成")

    def on_exit(self) -> None:
        """退出场景"""
        logger.info("退出主游戏场景")
        self._cleanup()

    def _create_ui_elements(self):
        """创建UI元素"""
        # 创建主控制面板容器
        control_panel_rect = pygame.Rect(
            0, 0,
            self.layout['control_panel_width'],
            self.layout['window_height']
        )
        self.ui_elements['control_panel'] = pygame_gui.elements.UIPanel(
            relative_rect=control_panel_rect,
            manager=self.manager,
            object_id='#control_panel'
        )

        # 创建四个UI组件
        self._create_ui_components()

    def _create_ui_components(self):
        """创建UI组件"""
        control_panel = self.ui_elements['control_panel']
        control_content_width = self.layout['control_content_width']

        # 1. 游戏信息面板
        info_panel_rect = pygame.Rect(
            UIConstants.WINDOW_MARGIN,
            UIConstants.WINDOW_MARGIN,
            control_content_width,
            self.layout['info_panel_height']
        )
        self.components['game_info'] = GameInfoPanel(
            ui_manager=self.manager,
            container_rect=info_panel_rect,
            container=control_panel
        )

        # 2. 方向控制面板
        ctrl_panel_top = self.layout['info_panel_height'] + 2 * UIConstants.WINDOW_MARGIN
        ctrl_panel_rect = pygame.Rect(
            UIConstants.WINDOW_MARGIN,
            ctrl_panel_top,
            control_content_width,
            self.layout['control_panel_height']
        )
        self.components['control'] = ControlPanel(
            ui_manager=self.manager,
            container_rect=ctrl_panel_rect,
            on_direction_selected=self._handle_move,
            container=control_panel
        )

        # 3. 功能操作面板
        func_panel_top = (self.layout['info_panel_height'] +
                          self.layout['control_panel_height'] +
                          3 * UIConstants.WINDOW_MARGIN)
        func_panel_rect = pygame.Rect(
            UIConstants.WINDOW_MARGIN,
            func_panel_top,
            control_content_width,
            self.layout['function_panel_height']
        )
        self.components['function'] = FunctionPanel(
            ui_manager=self.manager,
            container_rect=func_panel_rect,
            on_reset=self._reset_level,
            on_new_level=self._new_level,
            container=control_panel
        )

        # 4. 迷宫显示面板
        maze_panel_rect = pygame.Rect(
            self.layout['control_panel_width'], 0,
            self.layout['maze_panel_width'],
            self.layout['window_height']
        )
        self.components['maze'] = MazePanel(
            ui_manager=self.manager,
            container_rect=maze_panel_rect,
            game_service=self.game_service,
            maze_renderer=self.maze_renderer
        )

    def _refresh_ui(self):
        """刷新UI显示"""
        if not self.game_service:
            return

        game_state = self.game_service.get_current_state()
        if not game_state:
            return

        try:
            # 更新游戏信息面板
            self.components['game_info'].update_game_state(game_state.to_dict())

            # 更新迷宫显示
            self.components['maze'].update()

        except Exception as e:
            logger.error(f"刷新UI失败: {e}")

    def _setup_event_listeners(self):
        """设置事件监听器"""
        # 订阅服务器事件
        if self.http_server:
            self.http_server.get_event_bus().subscribe(
                EventType.GAME_STATE_UPDATED,
                self._on_game_state_updated
            )

        # 订阅键盘事件
        self.event_bus.subscribe(EventType.KEY_PRESSED, self._on_key_pressed)

    def _on_game_state_updated(self, event):
        """游戏状态更新事件处理"""
        self._refresh_ui()

    def _on_key_pressed(self, event):
        """按键事件处理"""
        key = event.data.get("key")

        # 方向控制
        direction_mapping = {
            pygame.K_UP: "up",
            pygame.K_w: "up",
            pygame.K_DOWN: "down",
            pygame.K_s: "down",
            pygame.K_LEFT: "left",
            pygame.K_a: "left",
            pygame.K_RIGHT: "right",
            pygame.K_d: "right",
            pygame.K_SPACE: "wait",
        }

        # 功能键
        function_mapping = {
            pygame.K_r: "reset",
            pygame.K_n: "new",
        }

        if key in direction_mapping:
            self._handle_move(direction_mapping[key])
        elif key in function_mapping:
            self._handle_function(function_mapping[key])

    def _handle_move(self, direction: str):
        """处理移动"""
        from python.core.models.GameModels import Direction
        try:
            result = self.game_service.move_player(Direction(direction))

            if result.success:
                self._refresh_ui()

                # 通过事件总线通知
                self.event_bus.emit(EventType.PLAYER_MOVED, {
                    "direction": direction,
                    "result": result.to_dict()
                })

                # 通知服务器
                if self.http_server:
                    self.http_server.get_event_bus().emit(
                        EventType.GAME_STATE_UPDATED,
                        {"game_state": self.game_service.get_current_state().to_dict()}
                    )

        except Exception as e:
            logger.error(f"移动失败: {e}")

    def _handle_function(self, action: str):
        """处理功能操作"""
        if action == "reset":
            self._reset_level()
        elif action == "new":
            self._new_level()

    def _reset_level(self):
        """重置当前关卡"""
        try:
            self.game_service.reset_current_level()
            self._refresh_ui()

            self.event_bus.emit(EventType.LEVEL_RESET, {
                "game_state": self.game_service.get_current_state().to_dict()
            })

        except Exception as e:
            logger.error(f"重置失败: {e}")

    def _new_level(self):
        """生成新关卡"""
        try:
            self.game_service.generate_new_level()
            # 需要重新创建迷宫Surface，因为迷宫尺寸可能变化
            self.components['maze']._refresh_maze_surface()
            self._refresh_ui()

            self.event_bus.emit(EventType.NEW_LEVEL_GENERATED, {
                "game_state": self.game_service.get_current_state().to_dict()
            })

        except Exception as e:
            logger.error(f"生成新关卡失败: {e}")

    def handle_events(self, events) -> None:
        """处理事件"""
        for event in events:
            # 退出事件
            if event.type == pygame.QUIT:
                self.running = False
                return

            # 键盘事件
            elif event.type == pygame.KEYDOWN:
                self.event_bus.emit(EventType.KEY_PRESSED, {"key": event.key})

            # 传递事件给UI管理器
            self.manager.process_events(event)

            # 只处理按钮按下和释放事件，不处理其他UI事件
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                for component in self.components.values():
                    component.handle_event(event)

    def update(self, dt: float) -> None:
        """更新场景逻辑"""
        if not self.initialized or not self.running:
            return

        # 更新UI管理器
        self.manager.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """绘制场景"""
        if not self.initialized:
            return

        # 绘制所有内容
        screen.fill(UIConstants.BACKGROUND_COLOR)
        self.manager.draw_ui(screen)

        # 绘制迷宫（通过MazePanel组件）
        self.components['maze'].draw(screen)

    def _cleanup(self):
        """清理资源"""
        try:
            # 销毁组件
            for component in self.components.values():
                component.kill()

            # 销毁UI元素
            for element in self.ui_elements.values():
                if hasattr(element, 'kill'):
                    element.kill()

            logger.info("主游戏场景资源清理完成")
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

    def is_running(self) -> bool:
        """检查场景是否仍在运行"""
        return self.running
