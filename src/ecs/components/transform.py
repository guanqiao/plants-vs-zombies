"""
变换组件 - 实体的位置、旋转和缩放
"""

from dataclasses import dataclass


@dataclass
class TransformComponent:
    """
    变换组件
    
    存储实体在2D空间中的位置、旋转角度和缩放比例
    
    Attributes:
        x: X坐标（像素）
        y: Y坐标（像素）
        rotation: 旋转角度（度）
        scale: 缩放比例
    """
    x: float
    y: float
    rotation: float = 0.0
    scale: float = 1.0
    
    def set_position(self, x: float, y: float) -> None:
        """设置位置"""
        self.x = x
        self.y = y
    
    def translate(self, dx: float, dy: float) -> None:
        """平移"""
        self.x += dx
        self.y += dy