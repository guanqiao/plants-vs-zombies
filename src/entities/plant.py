import pygame
from enum import Enum, auto
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


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


PLANT_CONFIGS = {
    PlantType.SUNFLOWER: {
        'cost': 50,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (255, 255, 0),
    },
    PlantType.PEASHOOTER: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 200, 0),
    },
    PlantType.WALLNUT: {
        'cost': 50,
        'health': 400,
        'width': 60,
        'height': 80,
        'color': (139, 69, 19),
    },
    PlantType.SNOW_PEA: {
        'cost': 175,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (135, 206, 250),
    },
    PlantType.CHERRY_BOMB: {
        'cost': 150,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (220, 20, 60),
    },
    PlantType.POTATO_MINE: {
        'cost': 25,
        'health': 100,
        'width': 60,
        'height': 40,
        'color': (160, 82, 45),
    },
    PlantType.REPEATER: {
        'cost': 200,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 150, 0),
    },
    PlantType.CHOMPER: {
        'cost': 150,
        'health': 100,
        'width': 80,
        'height': 80,
        'color': (128, 0, 128),
    },
    PlantType.THREEPEATER: {
        'cost': 325,
        'health': 100,
        'width': 60,
        'height': 80,
        'color': (0, 180, 0),
    },
    PlantType.MELON_PULT: {
        'cost': 300,
        'health': 100,
        'width': 70,
        'height': 80,
        'color': (0, 150, 0),
    },
    PlantType.WINTER_MELON: {
        'cost': 500,
        'health': 100,
        'width': 70,
        'height': 80,
        'color': (100, 150, 200),
    },
    PlantType.TALL_NUT: {
        'cost': 125,
        'health': 800,
        'width': 60,
        'height': 100,
        'color': (160, 120, 80),
    },
    PlantType.SPIKEWEED: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 40,
        'color': (100, 100, 100),
    },
    PlantType.MAGNET_SHROOM: {
        'cost': 100,
        'health': 100,
        'width': 60,
        'height': 70,
        'color': (128, 0, 128),
    },
    PlantType.PUMPKIN: {
        'cost': 125,
        'health': 400,
        'width': 70,
        'height': 70,
        'color': (255, 140, 0),
    },
}


class Plant(ABC):
    """植物基类"""
    
    def __init__(self, plant_type: PlantType, x: float, y: float):
        self.plant_type = plant_type
        self.x = x
        self.y = y
        
        config = PLANT_CONFIGS.get(plant_type, {})
        self.cost = config.get('cost', 100)
        self.health = config.get('health', 100)
        self.width = config.get('width', 60)
        self.height = config.get('height', 80)
        self.color = config.get('color', (0, 200, 0))
        
        self.row: int = 0
        self.col: int = 0
        self.animation_time = 0.0
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
    
    def is_dead(self) -> bool:
        """是否死亡"""
        return self.health <= 0
    
    def get_cost(self) -> int:
        """获取成本"""
        return self.cost
    
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新植物状态"""
        self.animation_time += dt
        self._update_behavior(dt, game_manager)
    
    @abstractmethod
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新植物特有行为，子类实现"""
        pass
    
    def render(self, screen: pygame.Surface):
        """渲染植物"""
        rect = self.get_rect()
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        
        self._render_details(screen)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染植物细节，子类可重写"""
        pass
