# python/core/maze/MazeGenerator.py
"""
迷宫生成器
"""
import random
from typing import List

from python.core.models.MazeModels import MazeData
from python.logger import logger


class MazeGenerator:
    """迷宫生成器"""

    def __init__(self, width: int = 55, height: int = 35) -> None:
        # 确保尺寸为奇数以保证墙体厚度为1
        self.width: int = width if width % 2 == 1 else width + 1
        self.height: int = height if height % 2 == 1 else height + 1

    def generate(self) -> MazeData:
        """生成迷宫数据"""
        logger.info(f"开始生成迷宫 (尺寸: {self.width}x{self.height})")

        # 初始化网格，全部设为墙
        grid: List[List[int]] = [
            [1 for _ in range(self.width)]
            for _ in range(self.height)
        ]

        # 使用递归回溯算法生成迷宫
        self._recursive_backtrack(grid, 1, 1)

        # 创建迷宫数据对象
        maze_data = MazeData(
            grid=grid,
            width=self.width,
            height=self.height
        )

        logger.info("迷宫生成完成")
        return maze_data

    def _recursive_backtrack(self, grid: List[List[int]], col: int, row: int) -> None:
        """递归回溯算法核心实现"""
        grid[row][col] = 0

        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_col, new_row = col + dx, row + dy

            if (1 <= new_col < self.width - 1) and (1 <= new_row < self.height - 1) and grid[new_row][new_col] == 1:
                wall_col, wall_row = col + dx // 2, row + dy // 2
                grid[wall_row][wall_col] = 0
                self._recursive_backtrack(grid, new_col, new_row)
