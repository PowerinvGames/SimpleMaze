# python/app/ApplicationController.py
"""
应用程序控制器 - 协调游戏服务和UI
"""
from python.constants import GameConstants, ResourcePaths, ServerConstants
from python.core.game.MazeGameService import MazeGameService
from python.logger import logger
from python.server.HttpGameServer import HttpGameServer
from python.ui.GameWindow import GameWindow


class ApplicationController:
    """应用程序控制器"""

    def __init__(self):
        self.game_service = None
        self.http_server = None
        self.game_window = None

    def initialize(self, args):
        """初始化应用程序"""
        logger.info("开始初始化应用程序")

        # 确保资源目录存在
        ResourcePaths.ensure_resources_dir()

        # 解析命令行参数
        maze_width = args.maze_width if hasattr(args, 'maze_width') else GameConstants.MAZE_WIDTH
        maze_height = args.maze_height if hasattr(args, 'maze_height') else GameConstants.MAZE_HEIGHT
        host = args.host if hasattr(args, 'host') else ServerConstants.DEFAULT_HOST
        port = args.port if hasattr(args, 'port') else ServerConstants.DEFAULT_PORT

        # 创建游戏服务
        self.game_service = MazeGameService(maze_width, maze_height)
        logger.info(f"游戏服务初始化完成 (迷宫尺寸: {maze_width}x{maze_height})")

        # 创建HTTP服务器
        self.http_server = HttpGameServer(self.game_service, host, port)
        self.http_server.start()
        logger.info(f"HTTP服务器启动完成: {self.http_server.get_server_url()}")

        # 创建游戏窗口
        self.game_window = GameWindow(self.game_service, self.http_server)
        logger.info("游戏窗口初始化完成")

        logger.info("应用程序初始化完成")

    def run(self):
        """运行应用程序"""
        if not all([self.game_service, self.http_server, self.game_window]):
            raise RuntimeError("应用程序未正确初始化")

        # 显示启动信息
        self._print_startup_info()

        # 运行主循环
        try:
            self.game_window.run()
        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        except Exception as e:
            logger.error(f"应用程序运行错误: {e}")
        finally:
            self.shutdown()

    def _print_startup_info(self):
        """打印启动信息"""
        info_lines = [
            "=" * 60,
            "迷宫AI游戏",
            "=" * 60,
            f"API服务器: {self.http_server.get_server_url()}",
            "控制方式:",
            "  - 界面按钮: 使用方向控制面板",
            "  - 键盘: WASD或方向键控制方向，空格键等待",
            "  - HTTP API: 通过RESTful API远程控制",
            "",
            "HTTP API接口:",
            "  - GET  /api/health     - 健康检查",
            "  - GET  /api/state      - 获取游戏状态",
            "  - POST /api/move       - 移动玩家",
            "  - POST /api/reset      - 重置当前关卡",
            "  - POST /api/new-level  - 生成新关卡",
            "=" * 60
        ]

        for line in info_lines:
            print(line)

    def shutdown(self):
        """关闭应用程序"""
        logger.info("正在关闭应用程序...")

        # 清理资源
        if self.game_window:
            logger.info("游戏窗口已关闭")

        if self.http_server:
            logger.info("HTTP服务器已停止")

        logger.info("应用程序关闭完成")
