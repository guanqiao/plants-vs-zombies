"""
速度组件 - 实体的运动属性
"""

from dataclasses import dataclass
from ..component import Component


@dataclass
class VelocityComponent(Component):
    """
    速度组件
    
    存储实体的运动速度和方向
    
    Attributes:
        vx: X轴速度（像素/秒）
        vy: Y轴速度（像素/秒）
        base_speed: 基础速度
        speed_multiplier: 速度倍率（用于减速/加速效果）
    """
    vx: float = 0.0
    vy: float = 0.0
    base_speed: float = 0.0
    speed_multiplier: float = 1.0
    
    def get_actual_speed(self) -> float:
        """获取实际速度"""
        return self.base_speed * self.speed_multiplier
    
    def set_velocity(self, vx: float, vy: float) -> None:
        """设置速度"""
        self.vx = vx
        self.vy = vy
    
    def apply_multiplier(self, multiplier: float) -> None:
        """应用速度倍率"""
        self.speed_multiplier = multiplier
    
    def reset_multiplier(self) -> None:
        """重置速度倍率"""
        self.speed_multiplier = 1.0
