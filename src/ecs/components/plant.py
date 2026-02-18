"""
植物相关组件
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class PlantType(Enum):
    """植物类型枚举"""
    SUNFLOWER = auto()
    PEASHOOTER = auto()
    WALLNUT = auto()
    SNOW_PEA = auto()
    CHERRY_BOMB = auto()
    POTATO_MINE = auto()
    REPEATER = auto()
    CHOMPER = auto()
    THREEPEATER = auto()
    MELON_PULT = auto()
    WINTER_MELON = auto()
    TALL_NUT = auto()
    SPIKEWEED = auto()
    MAGNET_SHROOM = auto()
    PUMPKIN = auto()


@dataclass
class PlantTypeComponent:
    """植物类型组件"""
    plant_type: PlantType


@dataclass
class PlantComponent:
    """
    植物组件
    
    存储植物特有的属性和状态
    
    Attributes:
        cost: 阳光成本
        attack_cooldown: 攻击冷却时间（秒）
        attack_timer: 当前攻击计时器
        attack_damage: 攻击力
        attack_range: 攻击范围（像素）
        is_ready: 是否准备好攻击
        special_timer: 特殊技能计时器
        is_armed: 是否已激活（如土豆雷）
    """
    cost: int = 100
    attack_cooldown: float = 1.5
    attack_timer: float = 0.0
    attack_damage: int = 20
    attack_range: float = 800.0
    is_ready: bool = True
    special_timer: float = 0.0
    is_armed: bool = True
    
    def update_timer(self, dt: float) -> None:
        """更新攻击计时器"""
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = 0
                self.is_ready = True
    
    def start_cooldown(self) -> None:
        """开始攻击冷却"""
        self.attack_timer = self.attack_cooldown
        self.is_ready = False
    
    def can_attack(self) -> bool:
        """检查是否可以攻击"""
        return self.is_ready and self.is_armed


# 植物配置字典
PLANT_CONFIGS = {
    PlantType.SUNFLOWER: {
        'cost': 50,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (255, 255, 0),
        'attack_cooldown': 5.0,
        'attack_damage': 0,
    },
    PlantType.PEASHOOTER: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 200, 0),
        'attack_cooldown': 1.5,
        'attack_damage': 20,
    },
    PlantType.WALLNUT: {
        'cost': 50,
        'health': 400,
        'width': 60,
        'height': 80,
        'color': (139, 69, 19),
        'attack_cooldown': 0.0,
        'attack_damage': 0,
    },
    PlantType.SNOW_PEA: {
        'cost': 175,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (135, 206, 250),
        'attack_cooldown': 1.5,
        'attack_damage': 20,
    },
    PlantType.CHERRY_BOMB: {
        'cost': 150,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (220, 20, 60),
        'attack_cooldown': 0.1,
        'attack_damage': 500,
    },
    PlantType.POTATO_MINE: {
        'cost': 25,
        'health': 100,
        'width': 60,
        'height': 40,
        'color': (160, 82, 45),
        'attack_cooldown': 15.0,
        'attack_damage': 500,
        'is_armed': False,
    },
    PlantType.REPEATER: {
        'cost': 200,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 150, 0),
        'attack_cooldown': 1.5,
        'attack_damage': 20,
    },
    PlantType.CHOMPER: {
        'cost': 150,
        'health': 100,
        'width': 80,
        'height': 80,
        'color': (128, 0, 128),
        'attack_cooldown': 30.0,
        'attack_damage': 1000,
    },
    PlantType.THREEPEATER: {
        'cost': 325,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 180, 0),
        'attack_cooldown': 1.5,
        'attack_damage': 20,
    },
    PlantType.MELON_PULT: {
        'cost': 300,
        'health': 100,
        'width': 70,
        'height': 80,
        'color': (0, 150, 0),
        'attack_cooldown': 3.0,
        'attack_damage': 80,
    },
    PlantType.WINTER_MELON: {
        'cost': 500,
        'health': 100,
        'width': 70,
        'height': 80,
        'color': (100, 150, 200),
        'attack_cooldown': 3.0,
        'attack_damage': 80,
    },
    PlantType.TALL_NUT: {
        'cost': 125,
        'health': 800,
        'width': 60,
        'height': 100,
        'color': (160, 120, 80),
        'attack_cooldown': 0.0,
        'attack_damage': 0,
    },
    PlantType.SPIKEWEED: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 40,
        'color': (100, 100, 100),
        'attack_cooldown': 0.5,
        'attack_damage': 20,
    },
    PlantType.MAGNET_SHROOM: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 70,
        'color': (128, 0, 128),
        'attack_cooldown': 5.0,
        'attack_damage': 0,
    },
    PlantType.PUMPKIN: {
        'cost': 125,
        'health': 400,
        'width': 70,
        'height': 70,
        'color': (255, 140, 0),
        'attack_cooldown': 0.0,
        'attack_damage': 0,
    },
}