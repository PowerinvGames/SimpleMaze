# python/core/game/MazeGameService.py
"""
游戏核心逻辑服务
"""
from typing import Optional, Tuple

from python.core.maze.MazeGenerator import MazeGenerator
from python.core.models.GameModels import *
from python.core.models.MazeModels import MazeData
from python.logger import logger


class MazeGameService:
    """迷宫游戏核心服务"""

    def __init__(self, maze_width: int = 55, maze_height: int = 35):
        self.maze_width: int = maze_width
        self.maze_height: int = maze_height
        self.maze_data: Optional[MazeData] = None
        self.game_state: Optional[GameState] = None
        self._initialize_game()

    def _initialize_game(self) -> None:
        """初始化新游戏"""
        logger.info("初始化新游戏")

        generator = MazeGenerator(self.maze_width, self.maze_height)
        self.maze_data = generator.generate()

        # 设置起点（左下角）和终点（右上角）
        start_pos = Position(row=self.maze_data.height - 2, col=0)
        exit_pos = Position(row=1, col=self.maze_data.width - 1)

        # 打通入口和出口
        self.maze_data.grid[self.maze_data.height - 2][0] = 0
        self.maze_data.grid[self.maze_data.height - 2][1] = 0
        self.maze_data.grid[1][self.maze_data.width - 2] = 0
        self.maze_data.grid[1][self.maze_data.width - 1] = 0

        self.game_state = GameState(
            maze_size=MazeSize(self.maze_data.width, self.maze_data.height),
            player_position=start_pos,
            exit_position=exit_pos,
            move_count=0,
            is_completed=False
        )

        logger.info(f"游戏初始化完成 (玩家位置: {start_pos}, 出口位置: {exit_pos})")

    def move_player(self, direction: Direction) -> MoveResponse:
        """移动玩家"""
        logger.debug(f"尝试移动玩家方向: {direction.value}")

        if self.game_state is None or self.maze_data is None:
            logger.error("游戏未初始化")
            raise RuntimeError("Game not initialized")

        if self.game_state.is_completed:
            logger.info("游戏已完成，无法移动")
            return MoveResponse(
                success=True,
                result=MoveResult.ALREADY_AT_EXIT,
                game_state=self.game_state.clone(),
                message="Already at exit"
            )

        if direction == Direction.WAIT:
            logger.debug("玩家选择等待")
            return MoveResponse(
                success=True,
                result=MoveResult.SUCCESS,
                game_state=self.game_state.clone(),
                message="Wait action"
            )

        # 计算新位置
        new_row, new_col = self._calculate_new_position(direction)

        # 边界检查
        if not self._is_within_bounds(new_row, new_col):
            logger.warning(f"移动越界: ({new_row}, {new_col})")
            return MoveResponse(
                success=False,
                result=MoveResult.OUT_OF_BOUNDS,
                game_state=self.game_state.clone(),
                message="Move out of bounds"
            )

        new_position = Position(row=new_row, col=new_col)

        # 墙体检查
        if self.maze_data.is_wall(new_position):
            logger.warning(f"撞墙: ({new_row}, {new_col})")
            return MoveResponse(
                success=False,
                result=MoveResult.WALL,
                game_state=self.game_state.clone(),
                message="Hit a wall"
            )

        # 执行移动
        self.game_state.player_position = new_position
        self.game_state.move_count += 1

        # 检查是否到达出口
        if new_position == self.game_state.exit_position:
            self.game_state.is_completed = True
            logger.info(f"玩家到达出口! 总移动次数: {self.game_state.move_count}")

        logger.debug(f"移动成功，新位置: ({new_row}, {new_col})")
        return MoveResponse(
            success=True,
            result=MoveResult.SUCCESS,
            game_state=self.game_state.clone(),
            message="Move successful"
        )

    def _calculate_new_position(self, direction: Direction) -> Tuple[int, int]:
        """计算新位置坐标"""
        row, col = self.game_state.player_position.row, self.game_state.player_position.col

        if direction == Direction.UP:
            return row - 1, col
        elif direction == Direction.DOWN:
            return row + 1, col
        elif direction == Direction.LEFT:
            return row, col - 1
        elif direction == Direction.RIGHT:
            return row, col + 1
        else:
            return row, col

    def _is_within_bounds(self, row: int, col: int) -> bool:
        """检查位置是否在边界内"""
        return (0 <= row < self.maze_data.height and
                0 <= col < self.maze_data.width)

    def reset_current_level(self) -> GameState:
        """重置当前关卡（玩家回到起点）"""
        logger.info("重置当前关卡")

        if self.game_state is None:
            raise RuntimeError("Game not initialized")

        self.game_state.player_position = Position(
            row=self.maze_data.height - 2,
            col=1
        )
        self.game_state.move_count = 0
        self.game_state.is_completed = False

        logger.info(f"关卡重置完成 (玩家位置重置)")
        return self.game_state.clone()

    def generate_new_level(self) -> GameState:
        """生成全新关卡"""
        logger.info("生成新关卡")
        self._initialize_game()
        return self.game_state.clone()

    def get_current_state(self) -> GameState:
        """获取当前游戏状态"""
        if self.game_state is None:
            raise RuntimeError("Game not initialized")
        return self.game_state.clone()

    def get_maze_data(self) -> Optional[MazeData]:
        """获取迷宫数据"""
        return self.maze_data
