# python/server/HttpGameServer.py
"""
基于 Flask 的 HTTP 游戏服务器
"""
import socket
import threading
from typing import Optional

from flask import Flask, jsonify, request

from python.app.GameEventBus import EventType, GameEventBus
from python.core.game.MazeGameService import MazeGameService
from python.core.models.GameModels import Direction, GameState
from python.logger import logger


class HttpGameServer:
    """HTTP游戏服务器"""

    def __init__(self, game_service: MazeGameService, host: str = "127.0.0.1", port: int = 8000):
        self.game_service = game_service
        self.host = host
        self.port = port
        self.server_thread: Optional[threading.Thread] = None
        self.flask_app: Optional[Flask] = None
        self.event_bus = GameEventBus()

        # 创建 Flask 应用
        self.flask_app = Flask(__name__)
        self._setup_routes()

    def _find_available_port(self, start_port: int = 8000, port_range: int = 100) -> int:
        """寻找可用端口"""
        for port in range(start_port, start_port + port_range):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind((self.host, port))
                    return port
            except OSError:
                continue
        raise RuntimeError(f"在端口 {start_port} 到 {start_port + port_range - 1} 范围内未找到可用端口")

    def _setup_routes(self):
        """设置 API 路由"""

        def standard_response(success: bool, message: str, data: Optional[dict] = None):
            """标准JSON响应"""
            response_data = {"success": success, "message": message}
            if data:
                response_data["data"] = data
            return jsonify(response_data)

        @self.flask_app.route('/api/health', methods=['GET'])
        def health_check():
            """健康检查端点"""
            return standard_response(True, "服务器运行正常", {"status": "healthy"})

        @self.flask_app.route('/api/state', methods=['GET'])
        def get_game_state():
            """获取当前游戏状态"""
            try:
                state: GameState = self.game_service.get_current_state()
                return standard_response(True, "状态获取成功", state.to_dict())
            except Exception as e:
                logger.error(f"获取状态失败: {e}")
                return standard_response(False, f"获取状态失败: {str(e)}"), 500

        @self.flask_app.route('/api/move', methods=['POST'])
        def make_move():
            """执行移动指令"""
            try:
                # 从请求体中获取JSON数据
                request_data = request.get_json()
                if not request_data or 'direction' not in request_data:
                    return standard_response(False, "请求格式错误，缺少'direction'字段"), 400

                # 将字符串转换为Direction枚举
                direction = Direction(request_data['direction'])

                # 调用游戏核心逻辑
                move_result = self.game_service.move_player(direction)

                # 通过事件总线通知所有监听者
                self.event_bus.emit(
                    EventType.PLAYER_MOVED,
                    {
                        "direction": direction.value,
                        "result": move_result.to_dict(),
                        "game_state": self.game_service.get_current_state().to_dict()
                    }
                )

                # 如果游戏状态改变，发送更新事件
                self.event_bus.emit(
                    EventType.GAME_STATE_UPDATED,
                    {
                        "game_state": self.game_service.get_current_state().to_dict()
                    }
                )

                return standard_response(
                    move_result.success,
                    move_result.message,
                    move_result.to_dict()
                )
            except ValueError as e:
                logger.warning(f"请求参数错误: {e}")
                return standard_response(False, f"请求参数错误: {str(e)}"), 400
            except Exception as e:
                logger.error(f"服务器内部错误: {e}")
                return standard_response(False, f"服务器内部错误: {str(e)}"), 500

        @self.flask_app.route('/api/reset', methods=['POST'])
        def reset_current_level():
            """重置当前关卡 (人工触发)"""
            try:
                new_state: GameState = self.game_service.reset_current_level()

                # 通过事件总线通知
                self.event_bus.emit(
                    EventType.LEVEL_RESET,
                    {
                        "game_state": new_state.to_dict()
                    }
                )

                self.event_bus.emit(
                    EventType.GAME_STATE_UPDATED,
                    {
                        "game_state": new_state.to_dict()
                    }
                )

                return standard_response(
                    success=True,
                    message="当前关卡已重置",
                    data=new_state.to_dict()
                )
            except Exception as e:
                logger.error(f"重置失败: {e}")
                return standard_response(False, f"重置失败: {str(e)}"), 500

        @self.flask_app.route('/api/new-level', methods=['POST'])
        def generate_new_level():
            """生成全新关卡 (人工触发)"""
            try:
                new_state: GameState = self.game_service.generate_new_level()

                # 通过事件总线通知
                self.event_bus.emit(
                    EventType.NEW_LEVEL_GENERATED,
                    {
                        "game_state": new_state.to_dict()
                    }
                )

                self.event_bus.emit(
                    EventType.GAME_STATE_UPDATED,
                    {
                        "game_state": new_state.to_dict()
                    }
                )

                return standard_response(
                    success=True,
                    message="新关卡已生成",
                    data=new_state.to_dict()
                )
            except Exception as e:
                logger.error(f"生成新关卡失败: {e}")
                return standard_response(False, f"生成新关卡失败: {str(e)}"), 500

        # 添加CORS支持
        @self.flask_app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            return response

    def start(self):
        """在后台线程中启动 HTTP 服务器"""

        def run_server():
            logger.info(f"HTTP服务器启动在 http://{self.host}:{self.port}")
            self.flask_app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

        if self.port is None:
            self.port = self._find_available_port()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        """停止 HTTP 服务器"""
        logger.info("HTTP服务器停止")
        # Flask 运行在独立线程中，设置为守护线程后随主线程退出
        if self.server_thread:
            self.server_thread.daemon = True

    def get_server_url(self) -> str:
        """获取服务器基础URL"""
        return f"http://{self.host}:{self.port}"

    def get_event_bus(self) -> GameEventBus:
        """获取事件总线"""
        return self.event_bus
