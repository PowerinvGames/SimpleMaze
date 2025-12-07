# python/server/mcp/McpGameServer.py
"""
精简版MCP服务器 - 只提供核心功能，使用fastmcp
"""
from mcp.server.fastmcp import FastMCP

from python.app.GameEventBus import EventType, GameEventBus
from python.core.game.MazeGameService import MazeGameService
from python.core.models.GameModels import Direction
from python.logger import logger


class McpGameServer:
    """迷宫游戏MCP服务器"""

    def __init__(self, game_service: MazeGameService):
        self.game_service = game_service
        self.mcp = FastMCP("maze-game-mcp")
        self.event_bus = GameEventBus()

        # 注册工具
        self._register_tools()

    def _register_tools(self):
        """注册MCP工具"""

        @self.mcp.tool()
        async def get_game_state() -> str:
            """获取当前游戏状态信息"""
            try:
                game_state = self.game_service.get_current_state()
                player_pos = game_state.player_position
                exit_pos = game_state.exit_position

                status = "已完成" if game_state.is_completed else "进行中"

                return f"""当前游戏状态：
• 迷宫尺寸：{game_state.maze_size.width} × {game_state.maze_size.height}
• 玩家位置：列{player_pos.col}, 行{player_pos.row}
• 出口位置：列{exit_pos.col}, 行{exit_pos.row}
• 移动次数：{game_state.move_count}
• 游戏状态：{status}

{"🎯 恭喜！玩家已到达出口！" if game_state.is_completed else "🏃 请继续探索迷宫..."}
"""
            except Exception as e:
                return f"获取游戏状态失败: {str(e)}"

        @self.mcp.tool()
        async def move_player(direction: str) -> str:
            """移动玩家到指定方向

            Args:
                direction: 移动方向，可选值：up(上), down(下), left(左), right(右), wait(等待)
            """
            try:
                direction_enum = Direction(direction.lower())
                move_response = self.game_service.move_player(direction_enum)

                logger.info(f"MCP移动执行结果：{move_response}")

                # 通过事件总线通知所有监听者
                self.event_bus.emit(
                    EventType.PLAYER_MOVED,
                    {
                        "direction": direction_enum.value,
                        "result": move_response.to_dict(),
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

                if move_response.success:
                    if move_response.result.value == "already_at_exit":
                        return "玩家已在出口位置，无需移动。"
                    elif move_response.result.value == "success":
                        new_pos = move_response.game_state.player_position

                        if move_response.game_state.is_completed:
                            return f"""✅ 移动成功！玩家已到达出口！
• 新位置：列{new_pos.col}, 行{new_pos.row}
• 总移动次数：{move_response.game_state.move_count}
• 🎉 恭喜完成迷宫！"""
                        else:
                            return f"""✅ 移动成功！
• 新位置：列{new_pos.col}, 行{new_pos.row}
• 总移动次数：{move_response.game_state.move_count}
• 状态：游戏中..."""
                    else:
                        return f"移动结果：{move_response.result.value}"
                else:
                    if move_response.result.value == "wall":
                        return "❌ 移动失败：撞到墙了！"
                    elif move_response.result.value == "out_of_bounds":
                        return "❌ 移动失败：超出迷宫边界！"
                    else:
                        return f"移动失败：{move_response.message}"

            except ValueError:
                return f"无效的方向：{direction}。请使用：up, down, left, right, wait"
            except Exception as e:
                return f"移动失败: {str(e)}"

        @self.mcp.tool()
        async def reset_level() -> str:
            """重置当前关卡，将玩家放回起点"""
            try:
                game_state = self.game_service.reset_current_level()
                player_pos = game_state.player_position

                # 通过事件总线通知
                self.event_bus.emit(
                    EventType.LEVEL_RESET,
                    {
                        "game_state": game_state.to_dict()
                    }
                )

                self.event_bus.emit(
                    EventType.GAME_STATE_UPDATED,
                    {
                        "game_state": game_state.to_dict()
                    }
                )

                return f"""✅ 迷宫已重置！
• 玩家已回到起点：列{player_pos.col}, 行{player_pos.row}
• 移动次数已清零：0
• 游戏状态：进行中

可以重新开始探索迷宫了！"""
            except Exception as e:
                return f"重置失败: {str(e)}"

        @self.mcp.tool()
        async def new_level() -> str:
            """生成全新迷宫关卡"""
            try:
                game_state = self.game_service.generate_new_level()
                player_pos = game_state.player_position
                exit_pos = game_state.exit_position

                # 通过事件总线通知
                self.event_bus.emit(
                    EventType.NEW_LEVEL_GENERATED,
                    {
                        "game_state": game_state.to_dict()
                    }
                )

                self.event_bus.emit(
                    EventType.GAME_STATE_UPDATED,
                    {
                        "game_state": game_state.to_dict()
                    }
                )

                return f"""✨ 新迷宫已生成！
• 玩家起点：列{player_pos.col}, 行{player_pos.row}
• 出口位置：列{exit_pos.col}, 行{exit_pos.row}
• 移动次数：0
• 游戏状态：进行中

祝你好运！"""
            except Exception as e:
                return f"生成新迷宫失败: {str(e)}"

        # 添加一个帮助工具
        @self.mcp.tool()
        async def help() -> str:
            """显示所有可用工具和说明"""
            return """可用工具：
1. get_game_state - 获取当前游戏状态信息
2. move_player(direction) - 移动玩家到指定方向
   参数: direction - 可选值：up(上), down(下), left(左), right(右), wait(等待)
3. reset_level - 重置当前关卡，将玩家放回起点
4. new_level - 生成全新迷宫关卡

使用示例：
- 获取状态: get_game_state()
- 向上移动: move_player("up")
- 重置关卡: reset_level()
- 新关卡: new_level()
"""

    def run(self, host: str = "127.0.0.1", port: int = 8081):
        """运行MCP服务器"""
        logger.info(f"启动MCP服务器在 {host}:{8000}")

        # 运行fastmcp服务器
        self.mcp.run(transport="sse")
