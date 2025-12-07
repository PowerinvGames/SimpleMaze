# python/ui/MazeRenderer.py
"""
迷宫渲染器 - 简化版，移除缩放逻辑
"""
import pygame

from python.constants import ColorConstants, GameConstants
from python.core.models.GameModels import GameState
from python.core.models.MazeModels import MazeData
from python.logger import logger


class MazeRenderer:
    """迷宫渲染器 - 固定大小，居中显示"""

    def __init__(self, cell_size: int = GameConstants.CELL_SIZE):
        """初始化渲染器"""
        self.cell_size = cell_size
        self.colors = {
            'wall': ColorConstants.WALL,
            'path': ColorConstants.PATH,
            'player': ColorConstants.PLAYER,
            'exit': ColorConstants.EXIT,
            'grid': ColorConstants.GRID
        }

    def draw(self, maze_data: MazeData, game_state: GameState, surface: pygame.Surface) -> pygame.Surface:
        """
        在给定的Surface上绘制迷宫

        Args:
            maze_data: 迷宫数据对象
            game_state: 游戏状态对象
            surface: 要绘制到的Surface

        Returns:
            绘制完成的Surface
        """
        if not maze_data or not game_state or not surface:
            logger.warning("迷宫渲染器参数无效")
            return surface

        try:
            # 清空Surface（使用透明色）
            surface.fill((255, 255, 255, 0))

            # 绘制所有单元格
            for row in range(maze_data.height):
                for col in range(maze_data.width):
                    # 计算单元格位置
                    x = col * self.cell_size
                    y = row * self.cell_size

                    rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                    # 确定单元格类型和颜色
                    from python.core.models.GameModels import Position
                    pos = Position(row, col)

                    if pos == game_state.player_position:
                        color = self.colors['player']
                    elif pos == game_state.exit_position:
                        color = self.colors['exit']
                    elif maze_data.is_wall(pos):
                        color = self.colors['wall']
                    else:
                        color = self.colors['path']

                    # 绘制单元格
                    pygame.draw.rect(surface, color, rect)

                    # 绘制网格线
                    if maze_data.is_wall(pos):
                        pygame.draw.rect(surface, self.colors['grid'], rect, 1)

            return surface

        except Exception as e:
            logger.error(f"绘制迷宫失败: {e}")
            return surface
