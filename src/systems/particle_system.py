import pygame
import random
import math
from typing import List, Tuple, Optional


class Particle:
    """粒子类"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int],
                 velocity: Tuple[float, float] = (0, 0),
                 lifetime: float = 1.0, size: int = 5,
                 gravity: float = 0, fade: bool = True):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.original_size = size
        self.gravity = gravity
        self.fade = fade
        self.alpha = 255
        self.is_alive = True
    
    def update(self, dt: float):
        """更新粒子状态"""
        if not self.is_alive:
            return
        
        self.lifetime -= dt
        
        if self.lifetime <= 0:
            self.is_alive = False
            return
        
        self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if self.fade:
            life_ratio = self.lifetime / self.max_lifetime
            self.alpha = int(255 * life_ratio)
            self.size = max(1, int(self.original_size * life_ratio))
    
    def render(self, screen: pygame.Surface):
        """渲染粒子"""
        if not self.is_alive or self.alpha <= 0:
            return
        
        color = (*self.color, self.alpha)
        surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, color, (self.size, self.size), self.size)
        screen.blit(surface, (int(self.x - self.size), int(self.y - self.size)))


class ParticleSystem:
    """粒子系统"""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def emit(self, x: float, y: float, color: Tuple[int, int, int],
             count: int = 1, lifetime: float = 1.0,
             speed_range: Tuple[float, float] = (-50, 50),
             size_range: Tuple[int, int] = (3, 8),
             gravity: float = 0):
        """发射粒子"""
        for _ in range(count):
            vx = random.uniform(*speed_range)
            vy = random.uniform(*speed_range)
            size = random.randint(*size_range)
            
            particle = Particle(
                x, y, color,
                velocity=(vx, vy),
                lifetime=lifetime,
                size=size,
                gravity=gravity
            )
            self.particles.append(particle)
    
    def create_explosion(self, x: float, y: float, intensity: int = 20):
        """创建爆炸效果"""
        colors = [(255, 100, 0), (255, 200, 0), (255, 50, 0), (255, 255, 100)]
        
        for _ in range(intensity):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = random.choice(colors)
            lifetime = random.uniform(0.3, 0.8)
            size = random.randint(4, 12)
            
            particle = Particle(
                x, y, color,
                velocity=(vx, vy),
                lifetime=lifetime,
                size=size,
                gravity=50,
                fade=True
            )
            self.particles.append(particle)
    
    def create_sun_collect(self, x: float, y: float):
        """创建阳光收集效果"""
        colors = [(255, 255, 0), (255, 200, 0), (255, 255, 100)]
        
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(30, 80)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = random.choice(colors)
            
            particle = Particle(
                x, y, color,
                velocity=(vx, vy),
                lifetime=0.5,
                size=random.randint(3, 6),
                fade=True
            )
            self.particles.append(particle)
    
    def create_hit_effect(self, x: float, y: float, color: Tuple[int, int, int] = (255, 0, 0)):
        """创建击中效果"""
        for _ in range(5):
            vx = random.uniform(-30, 30)
            vy = random.uniform(-30, 30)
            
            particle = Particle(
                x, y, color,
                velocity=(vx, vy),
                lifetime=0.3,
                size=random.randint(2, 5),
                fade=True
            )
            self.particles.append(particle)
    
    def create_death_effect(self, x: float, y: float, color: Tuple[int, int, int] = (128, 128, 128)):
        """创建死亡效果"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 100)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            particle = Particle(
                x, y, color,
                velocity=(vx, vy),
                lifetime=random.uniform(0.5, 1.0),
                size=random.randint(3, 8),
                gravity=100,
                fade=True
            )
            self.particles.append(particle)
    
    def update(self, dt: float):
        """更新所有粒子"""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive:
                self.particles.remove(particle)
    
    def render(self, screen: pygame.Surface):
        """渲染所有粒子"""
        for particle in self.particles:
            particle.render(screen)
    
    def clear(self):
        """清除所有粒子"""
        self.particles.clear()
