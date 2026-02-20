"""
精灵组件 - 实体的视觉表现
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import arcade
from ..component import Component


@dataclass
class SpriteComponent(Component):
    """
    精灵组件
    
    存储实体的视觉属性，用于渲染
    
    Attributes:
        color: RGB颜色元组
        width: 宽度（像素）
        height: 高度（像素）
        sprite_path: 精灵图片路径（可选）
        alpha: 透明度（0-255）
    """
    color: Tuple[int, int, int]
    width: int
    height: int
    sprite_path: Optional[str] = None
    alpha: int = 255
    
    def get_rect(self, x: float, y: float) -> arcade.XYWH:
        """获取矩形区域"""
        return arcade.XYWH(x, y, self.width, self.height)
    
    def get_left(self, x: float) -> float:
        """获取左边界"""
        return x - self.width / 2
    
    def get_right(self, x: float) -> float:
        """获取右边界"""
        return x + self.width / 2
    
    def get_bottom(self, y: float) -> float:
        """获取下边界"""
        return y - self.height / 2
    
    def get_top(self, y: float) -> float:
        """获取上边界"""
        return y + self.height / 2
