import pygame
import random
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class Sun:
    """阳光类"""
    
    SIZE = 40
    DEFAULT_VALUE = 25
    DEFAULT_LIFETIME = 8.0
    FALL_SPEED = 50
    
    def __init__(self, x: float, y: float, value: int = DEFAULT_VALUE, 
                 target_y: Optional[float] = None):
        self.x = x
        self.y = y
        self.value = value
        self.target_y = target_y if target_y else y + random.randint(100, 300)
        self.lifetime = self.DEFAULT_LIFETIME
        self.is_collected = False
        self.collect_target: Optional[tuple] = None
        self.collect_speed = 500
    
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.SIZE // 2,
            self.y - self.SIZE // 2,
            self.SIZE,
            self.SIZE
        )
    
    def collect(self):
        """标记为已收集"""
        self.is_collected = True
    
    def is_expired(self) -> bool:
        """是否过期"""
        return self.lifetime <= 0 or self.is_collected
    
    def update(self, dt: float):
        """更新阳光状态"""
        self.lifetime -= dt
        
        if self.is_collected and self.collect_target:
            dx = self.collect_target[0] - self.x
            dy = self.collect_target[1] - self.y
            dist = (dx * dx + dy * dy) ** 0.5
            
            if dist < 10:
                return True
            
            self.x += (dx / dist) * self.collect_speed * dt
            self.y += (dy / dist) * self.collect_speed * dt
        elif self.y < self.target_y:
            self.y += self.FALL_SPEED * dt
            if self.y > self.target_y:
                self.y = self.target_y
        
        return False
    
    def render(self, screen: pygame.Surface):
        """渲染阳光"""
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.SIZE // 2)
        pygame.draw.circle(screen, (255, 200, 0), (int(self.x), int(self.y)), self.SIZE // 2 - 5)
        pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(self.y)), self.SIZE // 4)


class SunSystem:
    """阳光系统 - 管理阳光的生成和收集"""
    
    DEFAULT_SPAWN_INTERVAL = 10.0
    
    def __init__(self):
        self.suns: List[Sun] = []
        self.spawn_timer = 0.0
        self.spawn_interval = self.DEFAULT_SPAWN_INTERVAL
    
    def spawn_sky_sun(self):
        """从天空生成阳光"""
        x = random.randint(150, 750)
        y = 0
        target_y = random.randint(100, 500)
        sun = Sun(x, y, target_y=target_y)
        self.suns.append(sun)
    
    def add_sun_from_plant(self, x: float, y: float, value: int = Sun.DEFAULT_VALUE):
        """植物产生阳光"""
        sun = Sun(x, y - 30, value, target_y=y + 30)
        self.suns.append(sun)
    
    def collect_sun(self, click_x: int, click_y: int, game_manager: 'GameManager') -> bool:
        """尝试收集阳光"""
        for sun in self.suns:
            if sun.is_collected:
                continue
            
            rect = sun.get_rect()
            if rect.collidepoint(click_x, click_y):
                sun.collect()
                sun.collect_target = (50, 30)
                game_manager.add_sun(sun.value)
                return True
        
        return False
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新阳光系统"""
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_sky_sun()
            self.spawn_timer = 0.0
        
        for sun in self.suns[:]:
            finished = sun.update(dt)
            
            if finished or sun.is_expired():
                self.suns.remove(sun)
    
    def render(self, screen: pygame.Surface):
        """渲染所有阳光"""
        for sun in self.suns:
            if not sun.is_collected or sun.collect_target:
                sun.render(screen)
