import pygame
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class ProjectileType(Enum):
    """投射物类型枚举"""
    PEA = auto()
    FROZEN_PEA = auto()
    CHERRY_BOMB = auto()


PROJECTILE_CONFIGS = {
    ProjectileType.PEA: {
        'damage': 20,
        'speed': 300,
        'width': 15,
        'height': 15,
        'color': (0, 200, 0),
    },
    ProjectileType.FROZEN_PEA: {
        'damage': 20,
        'speed': 300,
        'width': 15,
        'height': 15,
        'color': (135, 206, 250),
    },
    ProjectileType.CHERRY_BOMB: {
        'damage': 300,
        'speed': 0,
        'width': 100,
        'height': 100,
        'color': (255, 0, 0),
    },
}


class Projectile:
    """投射物类"""
    
    SCREEN_WIDTH = 900
    
    def __init__(self, projectile_type: ProjectileType, x: float, y: float, row: int):
        self.projectile_type = projectile_type
        self.x = x
        self.y = y
        self.row = row
        
        config = PROJECTILE_CONFIGS.get(projectile_type, {})
        self.damage = config.get('damage', 20)
        self.speed = config.get('speed', 300)
        self.width = config.get('width', 15)
        self.height = config.get('height', 15)
        self.color = config.get('color', (0, 200, 0))
        
        self._dead = False
    
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def is_dead(self) -> bool:
        """是否死亡"""
        return self._dead
    
    def on_hit(self):
        """命中目标"""
        self._dead = True
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新投射物状态"""
        self.x += self.speed * dt
        
        if self.x > self.SCREEN_WIDTH:
            self._dead = True
        
        if self.is_dead():
            game_manager.remove_projectile(self)
    
    def render(self, screen: pygame.Surface):
        """渲染投射物"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.width // 2)
        
        if self.projectile_type == ProjectileType.FROZEN_PEA:
            pygame.draw.circle(screen, (200, 230, 255), (int(self.x), int(self.y)), self.width // 3)
