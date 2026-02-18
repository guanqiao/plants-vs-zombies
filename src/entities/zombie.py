import pygame
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class ZombieType(Enum):
    """僵尸类型枚举"""
    NORMAL = auto()
    CONEHEAD = auto()
    BUCKETHEAD = auto()
    RUNNER = auto()
    GARGANTUAR = auto()


ZOMBIE_CONFIGS = {
    ZombieType.NORMAL: {
        'health': 100,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 80,
        'color': (128, 128, 128),
        'score_value': 10,
    },
    ZombieType.CONEHEAD: {
        'health': 200,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (255, 140, 0),
        'score_value': 20,
    },
    ZombieType.BUCKETHEAD: {
        'health': 400,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (169, 169, 169),
        'score_value': 30,
    },
    ZombieType.RUNNER: {
        'health': 80,
        'speed': -60,
        'damage': 15,
        'width': 45,
        'height': 75,
        'color': (220, 220, 220),
        'score_value': 15,
    },
    ZombieType.GARGANTUAR: {
        'health': 1500,
        'speed': -15,
        'damage': 100,
        'width': 80,
        'height': 120,
        'color': (105, 105, 105),
        'score_value': 100,
    },
}


class Zombie:
    """僵尸基类"""
    
    def __init__(self, zombie_type: ZombieType, x: float, y: float):
        self.zombie_type = zombie_type
        self.x = x
        self.y = y
        
        config = ZOMBIE_CONFIGS.get(zombie_type, {})
        self.health = config.get('health', 100)
        self.base_speed = config.get('speed', -30)
        self.speed = self.base_speed
        self.damage = config.get('damage', 20)
        self.width = config.get('width', 50)
        self.height = config.get('height', 80)
        self.color = config.get('color', (128, 128, 128))
        self.score_value = config.get('score_value', 10)
        
        self.row: int = 0
        self.is_attacking = False
        self.attack_cooldown = 0.0
        self.attack_interval = 1.0
        
        self.slow_factor = 1.0
        self.slow_duration = 0.0
        
        self.animation_time = 0.0
    
    def take_damage(self, damage: int):
        """受到伤害"""
        self.health -= damage
    
    def is_dead(self) -> bool:
        """是否死亡"""
        return self.health <= 0
    
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def apply_slow(self, factor: float, duration: float):
        """应用减速效果"""
        self.slow_factor = factor
        self.slow_duration = duration
        self.speed = self.base_speed * factor
    
    def remove_slow(self):
        """移除减速效果"""
        self.slow_factor = 1.0
        self.slow_duration = 0.0
        self.speed = self.base_speed
    
    def attack(self, plant):
        """攻击植物"""
        if self.attack_cooldown <= 0:
            plant.take_damage(self.damage)
            self.attack_cooldown = self.attack_interval
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新僵尸状态"""
        self.animation_time += dt
        
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.remove_slow()
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        if not self.is_attacking:
            self.x += self.speed * dt
        
        if self.is_dead():
            game_manager.remove_zombie(self)
    
    def render(self, screen: pygame.Surface):
        """渲染僵尸"""
        rect = self.get_rect()
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        
        self._render_details(screen)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染僵尸细节"""
        eye_y = self.y - self.height // 4
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - 10), int(eye_y)), 5)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x + 10), int(eye_y)), 5)
        
        if self.slow_duration > 0:
            pygame.draw.rect(screen, (0, 100, 255), self.get_rect(), 3)
