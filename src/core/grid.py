import pygame
from typing import Optional, Tuple


class Grid:
    """草坪网格系统 - 管理5行9列的游戏区域"""
    
    ROWS = 5
    COLS = 9
    CELL_WIDTH = 80
    CELL_HEIGHT = 100
    OFFSET_X = 100
    OFFSET_Y = 100
    
    def __init__(self):
        self.cells = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]
    
    def get_cell_position(self, row: int, col: int) -> Tuple[int, int]:
        """获取指定格子的左上角像素坐标"""
        x = self.OFFSET_X + col * self.CELL_WIDTH
        y = self.OFFSET_Y + row * self.CELL_HEIGHT
        return (x, y)
    
    def get_cell_center(self, row: int, col: int) -> Tuple[int, int]:
        """获取指定格子的中心像素坐标"""
        x, y = self.get_cell_position(row, col)
        return (x + self.CELL_WIDTH // 2, y + self.CELL_HEIGHT // 2)
    
    def get_cell_from_position(self, x: int, y: int) -> Tuple[int, int]:
        """从像素坐标获取格子坐标，返回(row, col)"""
        col = (x - self.OFFSET_X) // self.CELL_WIDTH
        row = (y - self.OFFSET_Y) // self.CELL_HEIGHT
        return (row, col)
    
    def is_valid_cell(self, row: int, col: int) -> bool:
        """检查格子坐标是否有效"""
        return 0 <= row < self.ROWS and 0 <= col < self.COLS
    
    def is_cell_occupied(self, row: int, col: int) -> bool:
        """检查格子是否被占用"""
        if not self.is_valid_cell(row, col):
            return False
        return self.cells[row][col] is not None
    
    def get_plant_at(self, row: int, col: int):
        """获取指定格子的植物"""
        if not self.is_valid_cell(row, col):
            return None
        return self.cells[row][col]
    
    def place_plant(self, row: int, col: int, plant) -> bool:
        """在指定格子放置植物"""
        if not self.is_valid_cell(row, col):
            return False
        if self.is_cell_occupied(row, col):
            return False
        
        self.cells[row][col] = plant
        plant.row = row
        plant.col = col
        plant.x, plant.y = self.get_cell_center(row, col)
        return True
    
    def remove_plant(self, row: int, col: int):
        """移除指定格子的植物"""
        if not self.is_valid_cell(row, col):
            return None
        
        plant = self.cells[row][col]
        self.cells[row][col] = None
        return plant
    
    def render(self, screen: pygame.Surface):
        """渲染网格"""
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x, y = self.get_cell_position(row, col)
                rect = pygame.Rect(x, y, self.CELL_WIDTH, self.CELL_HEIGHT)
                
                if (row + col) % 2 == 0:
                    color = (34, 139, 34)
                else:
                    color = (50, 205, 50)
                
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
