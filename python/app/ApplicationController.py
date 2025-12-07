# python/app/ApplicationController.py（修改版）
"""
应用程序控制器 - 协调游戏服务和UI
"""
import threading

from python.constants import GameConstants, ResourcePaths, ServerConstants
from python.core.game.MazeGameService import MazeGameService
from python.logger import logger
from python.server.HttpGameServer import HttpGameServer
from python.server.McpGameServer import McpGameServer
from python.ui.GameWindow import GameWindow


class ApplicationController:
    """应用程序控制器"""

    def __init__(self):
        self.game_service = None
        self.http_server = None
        self.mcp_server = None
        self.game_window = None
        self.mcp_thread = None

    def initialize(self, args):
        """初始化应用程序"""
        logger.info("开始初始化应用程序")

        # 确保资源目录存在
        ResourcePaths.ensure_resources_dir()

        # 解析命令行参数
        maze_width = args.maze_width if hasattr(args, 'maze_width') else GameConstants.MAZE_WIDTH
        maze_height = args.maze_height if hasattr(args, 'maze_height') else GameConstants.MAZE_HEIGHT
        http_host = args.host if hasattr(args, 'host') else ServerConstants.DEFAULT_HOST
        http_port = args.port if hasattr(args, 'port') else ServerConstants.DEFAULT_PORT

        # MCP服务器端口（HTTP端口+1）
        mcp_port = http_port + 1

        # 创建游戏服务
        self.game_service = MazeGameService(maze_width, maze_height)
        logger.info(f"游戏服务初始化完成 (迷宫尺寸: {maze_width}x{maze_height})")

        # 创建HTTP服务器
        self.http_server = HttpGameServer(self.game_service, http_host, http_port)
        self.http_server.start()
        logger.info(f"HTTP服务器启动完成: {self.http_server.get_server_url()}")

        # 创建MCP服务器（在单独线程中运行）
        self._start_mcp_server(http_host, mcp_port)

        # 创建游戏窗口
        self.game_window = GameWindow(self.game_service, self.http_server)
        logger.info("游戏窗口初始化完成")

        logger.info("应用程序初始化完成")

    def _start_mcp_server(self, host: str, port: int):
        """启动MCP服务器线程"""

        def run_mcp_server():
            try:
                self.mcp_server = McpGameServer(self.game_service)
                self.mcp_server.run(host=host, port=port)
            except Exception as e:
                logger.error(f"MCP服务器运行错误: {e}")

        self.mcp_thread = threading.Thread(
            target=run_mcp_server,
            daemon=True,
            name="MCP-Server-Thread"
        )
        self.mcp_thread.start()

        logger.info(f"MCP服务器启动完成: http://{host}:{port}")

    def run(self):
        """运行应用程序"""
        if not all([self.game_service, self.http_server, self.mcp_server]):
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
        http_url = self.http_server.get_server_url()
        mcp_url = f"http://{self.http_server.host}:{self.http_server.port + 1}"

        info_lines = [
            "=" * 60,
            "迷宫AI游戏",
            "=" * 60,
            f"HTTP API服务器: {http_url}",
            f"MCP SSE服务器: {mcp_url}",
            "",
            "控制方式:",
            "  - 界面按钮: 使用方向控制面板",
            "  - 键盘: WASD或方向键控制方向，空格键等待",
            "  - HTTP API: 通过RESTful API远程控制",
            "  - MCP协议: 通过SSE协议供AI调用",
            "",
            "HTTP API接口:",
            "  - GET  /api/health     - 健康检查",
            "  - GET  /api/state      - 获取游戏状态",
            "  - POST /api/move       - 移动玩家",
            "  - POST /api/reset      - 重置当前关卡",
            "  - POST /api/new-level  - 生成新关卡",
            "",
            "MCP工具 (通过SSE):",
            "  - get_game_state - 获取游戏状态",
            "  - move_player(direction) - 移动玩家 (direction: up/down/left/right/wait)",
            "  - reset_level - 重置当前关卡",
            "  - new_level - 生成新关卡",
            "",
            "使用示例 (使用MCP客户端如Claude Desktop):",
            '  配置MCP服务器:',
            '  {',
            f'    "command": "python",',
            f'    "args": ["python/server/mcp/run_mcp_server.py", "--host", "{self.http_server.host}", "--port", "{self.http_server.port + 1}"]',
            '  }',
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
            self.http_server.stop()
            logger.info("HTTP服务器已停止")

        logger.info("应用程序关闭完成")
