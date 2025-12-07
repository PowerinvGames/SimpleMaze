# python/core/models/GameModels.py
"""
游戏核心数据模型
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class Direction(Enum):
    """移动方向枚举"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    WAIT = "wait"


class MoveResult(Enum):
    """移动结果枚举"""
    SUCCESS = "success"
    WALL = "wall"
    OUT_OF_BOUNDS = "out_of_bounds"
    ALREADY_AT_EXIT = "already_at_exit"


@dataclass(frozen=True)
class Position:
    """二维坐标位置"""
    row: int
    col: int

    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {"row": self.row, "col": self.col}

    @staticmethod
    def from_dict(data: Dict[str, int]) -> 'Position':
        """从字典创建"""
        return Position(row=data["row"], col=data["col"])

    def __eq__(self, other):
        """比较两个位置是否相等"""
        if not isinstance(other, Position):
            return False
        return self.row == other.row and self.col == other.col


@dataclass
class MazeSize:
    """迷宫尺寸"""
    width: int
    height: int

    def to_dict(self) -> Dict[str, int]:
        """转换为字典"""
        return {"width": self.width, "height": self.height}


@dataclass
class GameState:
    """游戏状态"""
    maze_size: MazeSize
    player_position: Position
    exit_position: Position
    move_count: int = 0
    is_completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "maze_size": self.maze_size.to_dict(),
            "player_position": self.player_position.to_dict(),
            "exit_position": self.exit_position.to_dict(),
            "move_count": self.move_count,
            "is_completed": self.is_completed
        }

    def clone(self) -> 'GameState':
        """创建副本"""
        return GameState(
            maze_size=MazeSize(self.maze_size.width, self.maze_size.height),
            player_position=Position(self.player_position.row, self.player_position.col),
            exit_position=Position(self.exit_position.row, self.exit_position.col),
            move_count=self.move_count,
            is_completed=self.is_completed
        )


class MoveRequest:
    """移动请求"""

    def __init__(self, direction: Direction) -> None:
        self.direction: Direction = direction

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveRequest':
        """从字典创建"""
        direction_str = data.get("direction", "wait")
        return MoveRequest(Direction(direction_str))

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {"direction": self.direction.value}


@dataclass
class MoveResponse:
    """移动响应"""
    success: bool
    result: MoveResult
    game_state: GameState
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "result": self.result.value,
            "scene_info": self.game_state.to_dict(),
            "message": self.message
        }
