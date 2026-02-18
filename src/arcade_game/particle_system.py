"""
粒子系统 - 处理游戏中的粒子效果

包括：
- 粒子发射器
- 粒子更新和渲染
- 多种粒子效果（爆炸、击中、收集等）
"""

import random
import math
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
import arcade


@dataclass
class Particle:
    """
    粒子类
    
    表示单个粒子
    """
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: Tuple[int, int, int, int]
    alpha_decay: float = 1.0
    size_decay: float = 0.0
    gravity: float = 0.0
    
    @property
    def is_alive(self) -> bool:
        """检查粒子是否存活"""
        return self.life > 0
    
    @property
    def life_ratio(self) -> float:
        """获取生命周期比例"""
        return self.life / self.max_life
    
    def update(self, dt: float) -> None:
        """更新粒子状态"""
        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 应用重力
        self.vy -= self.gravity * dt
        
        # 更新生命周期
        self.life -= dt
        
        # 更新透明度
        if self.alpha_decay > 0:
            self.color = (
                self.color[0],
                self.color[1],
                self.color[2],
                max(0, self.color[3] - int(self.alpha_decay * dt * 255))
            )
        
        # 更新大小
        if self.size_decay > 0:
            self.size = max(0, self.size - self.size_decay * dt)


class ParticleEmitter:
    """
    粒子发射器
    
    管理一组粒子的生成、更新和渲染
    """
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.particles: List[Particle] = []
        self.is_active = True
    
    def emit(self, particle: Particle) -> None:
        """发射一个粒子"""
        self.particles.append(particle)
    
    def emit_burst(self, count: int, 
                   speed_min: float, speed_max: float,
                   life_min: float, life_max: float,
                   size_min: float, size_max: float,
                   color: Tuple[int, int, int],
                   angle_min: float = 0, angle_max: float = 360,
                   gravity: float = 0.0) -> None:
        """
        发射一组粒子
        
        Args:
            count: 粒子数量
            speed_min, speed_max: 速度范围
            life_min, life_max: 生命周期范围
            size_min, size_max: 大小范围
            color: 颜色 (R, G, B)
            angle_min, angle_max: 角度范围（度）
            gravity: 重力
        """
        for _ in range(count):
            # 随机角度
            angle = math.radians(random.uniform(angle_min, angle_max))
            
            # 随机速度
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # 随机生命周期和大小
            life = random.uniform(life_min, life_max)
            size = random.uniform(size_min, size_max)
            
            # 创建粒子
            particle = Particle(
                x=self.x,
                y=self.y,
                vx=vx,
                vy=vy,
                life=life,
                max_life=life,
                size=size,
                color=(*color, 255),
                alpha_decay=1.0 / life if life > 0 else 0,
                size_decay=0.0,
                gravity=gravity
            )
            
            self.emit(particle)
    
    def update(self, dt: float) -> None:
        """更新所有粒子"""
        # 更新粒子
        for particle in self.particles:
            particle.update(dt)
        
        # 移除死亡粒子
        self.particles = [p for p in self.particles if p.is_alive]
        
        # 如果没有粒子了，标记为非活动
        if not self.particles:
            self.is_active = False
    
    def render(self) -> None:
        """渲染所有粒子"""
        for particle in self.particles:
            if particle.size > 0:
                arcade.draw_circle_filled(
                    particle.x, particle.y,
                    particle.size,
                    particle.color
                )
    
    def is_finished(self) -> bool:
        """检查发射器是否完成"""
        return not self.is_active and not self.particles


class ParticleSystem:
    """
    粒子系统管理器
    
    管理所有粒子发射器
    """
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def update(self, dt: float) -> None:
        """更新所有发射器"""
        # 更新发射器
        for emitter in self.emitters:
            emitter.update(dt)
        
        # 移除完成的发射器
        self.emitters = [e for e in self.emitters if not e.is_finished()]
    
    def render(self) -> None:
        """渲染所有发射器"""
        for emitter in self.emitters:
            emitter.render()
    
    def create_explosion(self, x: float, y: float, 
                        color: Tuple[int, int, int] = (255, 100, 0),
                        count: int = 20,
                        size: float = 5.0) -> ParticleEmitter:
        """
        创建爆炸效果
        
        Args:
            x, y: 位置
            color: 颜色
            count: 粒子数量
            size: 粒子大小
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        emitter.emit_burst(
            count=count,
            speed_min=50, speed_max=150,
            life_min=0.3, life_max=0.8,
            size_min=size * 0.5, size_max=size * 1.5,
            color=color,
            angle_min=0, angle_max=360,
            gravity=100.0
        )
        self.emitters.append(emitter)
        return emitter
    
    def create_hit_effect(self, x: float, y: float,
                         color: Tuple[int, int, int] = (255, 255, 0),
                         count: int = 10) -> ParticleEmitter:
        """
        创建击中效果
        
        Args:
            x, y: 位置
            color: 颜色
            count: 粒子数量
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        emitter.emit_burst(
            count=count,
            speed_min=30, speed_max=80,
            life_min=0.2, life_max=0.5,
            size_min=2, size_max=4,
            color=color,
            angle_min=0, angle_max=360
        )
        self.emitters.append(emitter)
        return emitter
    
    def create_collect_effect(self, x: float, y: float,
                             color: Tuple[int, int, int] = (255, 255, 0),
                             count: int = 15) -> ParticleEmitter:
        """
        创建收集效果
        
        Args:
            x, y: 位置
            color: 颜色
            count: 粒子数量
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        emitter.emit_burst(
            count=count,
            speed_min=40, speed_max=100,
            life_min=0.4, life_max=0.8,
            size_min=3, size_max=6,
            color=color,
            angle_min=0, angle_max=360,
            gravity=-50.0  # 向上飘
        )
        self.emitters.append(emitter)
        return emitter
    
    def create_plant_effect(self, x: float, y: float,
                           color: Tuple[int, int, int] = (0, 200, 0),
                           count: int = 12) -> ParticleEmitter:
        """
        创建种植效果
        
        Args:
            x, y: 位置
            color: 颜色
            count: 粒子数量
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        emitter.emit_burst(
            count=count,
            speed_min=20, speed_max=60,
            life_min=0.3, life_max=0.6,
            size_min=2, size_max=5,
            color=color,
            angle_min=180, angle_max=360  # 向上喷发
        )
        self.emitters.append(emitter)
        return emitter
    
    def create_zombie_death_effect(self, x: float, y: float,
                                   count: int = 25) -> ParticleEmitter:
        """
        创建僵尸死亡效果
        
        Args:
            x, y: 位置
            count: 粒子数量
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        
        # 灰色粒子（僵尸颜色）
        gray_count = count // 2
        red_count = count - gray_count  # 确保总数正确
        
        emitter.emit_burst(
            count=gray_count,
            speed_min=30, speed_max=100,
            life_min=0.4, life_max=0.9,
            size_min=3, size_max=7,
            color=(100, 100, 100),
            angle_min=0, angle_max=360,
            gravity=80.0
        )
        
        # 红色粒子（血迹）
        emitter.emit_burst(
            count=red_count,
            speed_min=20, speed_max=80,
            life_min=0.3, life_max=0.7,
            size_min=2, size_max=5,
            color=(200, 0, 0),
            angle_min=0, angle_max=360,
            gravity=100.0
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_projectile_trail(self, x: float, y: float,
                                color: Tuple[int, int, int] = (0, 255, 0),
                                size: float = 3.0) -> ParticleEmitter:
        """
        创建投射物尾迹效果
        
        Args:
            x, y: 位置
            color: 颜色
            size: 粒子大小
            
        Returns:
            粒子发射器
        """
        emitter = ParticleEmitter(x, y)
        emitter.emit_burst(
            count=1,
            speed_min=0, speed_max=10,
            life_min=0.1, life_max=0.3,
            size_min=size * 0.5, size_max=size,
            color=color,
            angle_min=0, angle_max=360
        )
        self.emitters.append(emitter)
        return emitter
    
    def clear(self) -> None:
        """清除所有发射器"""
        self.emitters.clear()
    
    def get_active_emitter_count(self) -> int:
        """获取活动发射器数量"""
        return len(self.emitters)
    
    def get_total_particle_count(self) -> int:
        """获取总粒子数量"""
        return sum(len(e.particles) for e in self.emitters)
