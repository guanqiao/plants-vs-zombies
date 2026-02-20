"""
网格位置组件 - 实体在网格系统中的位置
"""

from dataclasses import dataclass
from ..component import Component


@dataclass
class GridPositionComponent(Component):
    """
    网格位置组件
    
    存储实体在网格系统中的行列位置
    
    Attributes:
        row: 行索引（0-4）
        col: 列索引（0-8）
        is_occupied: 该位置是否被占用
    """
    row: int
    col: int
    is_occupied: bool = False
    
    def get_key(self) -> tuple:
        """获取位置键值，用于字典索引"""
        return (self.row, self.col)
    
    def is_valid(self, max_row: int = 4, max_col: int = 8) -> bool:
        """检查位置是否有效"""
        return 0 <= self.row <= max_row and 0 <= self.col <= max_col
