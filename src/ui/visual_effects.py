import pygame
import random
from typing import List, Tuple, Optional


class HealthBar:
    """血条组件"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 max_health: int = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health
        self.border_color = (0, 0, 0)
        self.background_color = (100, 100, 100)
        self.health_color = (0, 255, 0)
        self.low_health_color = (255, 0, 0)
        self.low_health_threshold = 0.3
    
    def update(self, current_health: int, max_health: int = None):
        """更新血条"""
        self.current_health = max(0, current_health)
        if max_health:
            self.max_health = max_health
    
    def render(self, screen: pygame.Surface):
        """渲染血条"""
        background_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.background_color, background_rect)
        
        health_ratio = self.current_health / self.max_health if self.max_health > 0 else 0
        health_width = int(self.width * health_ratio)
        
        if health_ratio < self.low_health_threshold:
            color = self.low_health_color
        else:
            color = self.health_color
        
        health_rect = pygame.Rect(self.x, self.y, health_width, self.height)
        pygame.draw.rect(screen, color, health_rect)
        
        pygame.draw.rect(screen, self.border_color, background_rect, 2)


class DamageNumber:
    """伤害数字"""
    
    def __init__(self, x: float, y: float, damage: int, 
                 color: Tuple[int, int, int] = (255, 0, 0),
                 lifetime: float = 1.0):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.alpha = 255
        self.is_alive = True
        self.vy = -50
        self.font = pygame.font.Font(None, 24)
    
    def update(self, dt: float):
        """更新伤害数字"""
        if not self.is_alive:
            return
        
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.is_alive = False
            return
        
        self.y += self.vy * dt
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
    
    def render(self, screen: pygame.Surface):
        """渲染伤害数字"""
        if not self.is_alive:
            return
        
        text = self.font.render(str(self.damage), True, self.color)
        text.set_alpha(self.alpha)
        
        text_rect = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, text_rect)


class ScreenShake:
    """屏幕震动效果"""
    
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.timer = 0
    
    def start(self, intensity: int = 10, duration: float = 0.3):
        """开始震动"""
        self.intensity = intensity
        self.duration = duration
        self.timer = 0
    
    def update(self, dt: float) -> Tuple[int, int]:
        """更新震动，返回偏移量"""
        if self.duration <= 0:
            return (0, 0)
        
        self.timer += dt
        
        if self.timer >= self.duration:
            self.stop()
            return (0, 0)
        
        progress = self.timer / self.duration
        current_intensity = self.intensity * (1 - progress)
        
        offset_x = random.randint(-int(current_intensity), int(current_intensity))
        offset_y = random.randint(-int(current_intensity), int(current_intensity))
        
        return (offset_x, offset_y)
    
    def stop(self):
        """停止震动"""
        self.intensity = 0
        self.duration = 0
        self.timer = 0
    
    def is_shaking(self) -> bool:
        """是否正在震动"""
        return self.duration > 0


class VisualEffectsManager:
    """视觉效果管理器"""
    
    def __init__(self):
        self.damage_numbers: List[DamageNumber] = []
        self.screen_shake = ScreenShake()
    
    def add_damage_number(self, x: float, y: float, damage: int,
                          color: Tuple[int, int, int] = (255, 0, 0),
                          lifetime: float = 1.0):
        """添加伤害数字"""
        damage_num = DamageNumber(x, y, damage, color, lifetime)
        self.damage_numbers.append(damage_num)
    
    def trigger_shake(self, intensity: int = 10, duration: float = 0.3):
        """触发屏幕震动"""
        self.screen_shake.start(intensity, duration)
    
    def update(self, dt: float):
        """更新所有视觉效果"""
        self.screen_shake.update(dt)
        
        for damage_num in self.damage_numbers[:]:
            damage_num.update(dt)
            if not damage_num.is_alive:
                self.damage_numbers.remove(damage_num)
    
    def render(self, screen: pygame.Surface):
        """渲染所有视觉效果"""
        for damage_num in self.damage_numbers:
            damage_num.render(screen)
    
    def clear(self):
        """清除所有效果"""
        self.damage_numbers.clear()
        self.screen_shake.stop()
