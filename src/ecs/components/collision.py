"""
碰撞组件 - 实体的碰撞检测属性
"""

from dataclasses import dataclass
from typing import Set


@dataclass
class CollisionComponent:
    """
    碰撞组件
    
    存储实体的碰撞检测属性
    
    Attributes:
        width: 碰撞盒宽度
        height: 碰撞盒高度
        is_trigger: 是否为触发器（不阻挡移动）
        layer: 碰撞层
        collides_with: 可以碰撞的层集合
        is_active: 碰撞检测是否激活
    """
    width: float
    height: float
    is_trigger: bool = False
    layer: int = 0
    collides_with: Set[int] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.collides_with is None:
            self.collides_with = set()
    
    def can_collide_with(self, other_layer: int) -> bool:
        """检查是否可以与指定层碰撞"""
        return other_layer in self.collides_with
    
    def get_bounds(self, x: float, y: float) -> tuple:
        """
        获取碰撞边界
        
        Returns:
            (left, right, bottom, top)
        """
        half_width = self.width / 2
        half_height = self.height / 2
        return (
            x - half_width,
            x + half_width,
            y - half_height,
            y + half_height
        )
    
    def intersects(self, x1: float, y1: float, other: 'CollisionComponent', x2: float, y2: float) -> bool:
        """检查是否与其他碰撞盒相交"""
        if not self.is_active or not other.is_active:
            return False
        
        left1, right1, bottom1, top1 = self.get_bounds(x1, y1)
        left2, right2, bottom2, top2 = other.get_bounds(x2, y2)
        
        return (left1 < right2 and right1 > left2 and
                bottom1 < top2 and top1 > bottom2)