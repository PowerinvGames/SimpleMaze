# python/core/models/MazeModels.py
"""
迷宫数据模型
"""
from dataclasses import dataclass
from typing import List

from python.core.models.GameModels import Position


@dataclass
class MazeData:
    """迷宫数据容器"""
    grid: List[List[int]]
    width: int
    height: int

    def is_wall(self, position: Position) -> bool:
        """检查指定位置是否是墙"""
        if 0 <= position.row < self.height and 0 <= position.col < self.width:
            return self.grid[position.row][position.col] == 1
        return True

    def is_path(self, position: Position) -> bool:
        """检查指定位置是否是路径"""
        if 0 <= position.row < self.height and 0 <= position.col < self.width:
            return self.grid[position.row][position.col] == 0
        return False

    def clone(self) -> 'MazeData':
        """创建副本"""
        return MazeData(
            grid=[row[:] for row in self.grid],
            width=self.width,
            height=self.height
        )
