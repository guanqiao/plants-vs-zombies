"""
投射物相关组件
"""

from dataclasses import dataclass
from enum import Enum, auto


class ProjectileType(Enum):
    """投射物类型枚举"""
    PEA = auto()
    FROZEN_PEA = auto()
    CHERRY_BOMB = auto()
    MELON = auto()
    FROZEN_MELON = auto()
    SPIKE = auto()


@dataclass
class ProjectileTypeComponent:
    """投射物类型组件"""
    projectile_type: ProjectileType


@dataclass
class ProjectileComponent:
    """
    投射物组件
    
    存储投射物的属性和行为
    
    Attributes:
        damage: 伤害值
        speed: 飞行速度
        is_splash: 是否溅射伤害
        splash_radius: 溅射半径
        applies_slow: 是否施加减速效果
        slow_factor: 减速倍率
        slow_duration: 减速持续时间
        pierce_count: 穿透次数（0表示不穿透）
        lifetime: 生命周期（秒）
    """
    damage: int = 20
    speed: float = 300.0
    is_splash: bool = False
    splash_radius: float = 50.0
    applies_slow: bool = False
    slow_factor: float = 0.5
    slow_duration: float = 3.0
    pierce_count: int = 0
    lifetime: float = 5.0
    
    def update_lifetime(self, dt: float) -> bool:
        """
        更新生命周期
        
        Returns:
            是否仍然存活
        """
        self.lifetime -= dt
        return self.lifetime > 0


# 投射物配置字典
PROJECTILE_CONFIGS = {
    ProjectileType.PEA: {
        'damage': 20,
        'speed': 300.0,
        'color': (0, 255, 0),
        'width': 15,
        'height': 15,
    },
    ProjectileType.FROZEN_PEA: {
        'damage': 20,
        'speed': 300.0,
        'color': (135, 206, 250),
        'width': 15,
        'height': 15,
        'applies_slow': True,
        'slow_factor': 0.5,
        'slow_duration': 3.0,
    },
    ProjectileType.CHERRY_BOMB: {
        'damage': 500,
        'speed': 0.0,
        'color': (220, 20, 60),
        'width': 60,
        'height': 60,
        'is_splash': True,
        'splash_radius': 100.0,
        'lifetime': 0.5,
    },
    ProjectileType.MELON: {
        'damage': 80,
        'speed': 200.0,
        'color': (0, 100, 0),
        'width': 30,
        'height': 30,
        'is_splash': True,
        'splash_radius': 50.0,
    },
    ProjectileType.FROZEN_MELON: {
        'damage': 80,
        'speed': 200.0,
        'color': (100, 150, 200),
        'width': 30,
        'height': 30,
        'is_splash': True,
        'splash_radius': 50.0,
        'applies_slow': True,
        'slow_factor': 0.5,
        'slow_duration': 3.0,
    },
    ProjectileType.SPIKE: {
        'damage': 20,
        'speed': 0.0,
        'color': (100, 100, 100),
        'width': 60,
        'height': 20,
    },
}