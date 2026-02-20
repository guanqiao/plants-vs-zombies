"""
粒子系统 - 处理游戏中的粒子效果 - 增强版

包括：
- 粒子发射器
- 粒子更新和渲染
- 多种粒子形状（圆形、星形、菱形、心形等）
- 多种粒子效果（爆炸、击中、收集等）
- 使用Material Design配色
"""

import random
import math
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade

from ..core.theme_colors import (
    Color, GameColors, StatusColors, EffectColors, SECONDARY, SECONDARY_LIGHT, WHITE
)


class ParticleShape(Enum):
    """粒子形状枚举"""
    CIRCLE = auto()      # 圆形
    STAR = auto()        # 星形
    DIAMOND = auto()     # 菱形
    HEART = auto()       # 心形
    SQUARE = auto()      # 方形
    TRIANGLE = auto()    # 三角形
    SPARK = auto()       # 火花
    RING = auto()        # 环形
    CROSS = auto()       # 十字


@dataclass
class Particle:
    """
    粒子类 - 增强版
    
    表示单个粒子
    """
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: Color
    alpha_decay: float = 1.0
    size_decay: float = 0.0
    gravity: float = 0.0
    shape: ParticleShape = ParticleShape.CIRCLE
    rotation: float = 0.0
    rotation_speed: float = 0.0
    initial_size: float = 0.0
    size_curve: str = "linear"  # linear, grow, shrink, grow_shrink
    
    # 新增：颜色渐变
    end_color: Optional[Color] = None
    color_lerp: float = 0.0
    
    def __post_init__(self):
        if self.initial_size == 0.0:
            self.initial_size = self.size
        
        # 确保颜色是 Color 对象
        if not isinstance(self.color, Color):
            self.color = Color(*self.color[:3], 255)
        if self.end_color is not None and not isinstance(self.end_color, Color):
            self.end_color = Color(*self.end_color[:3], 255)
    
    @property
    def is_alive(self) -> bool:
        """检查粒子是否存活"""
        return self.life > 0
    
    @property
    def life_ratio(self) -> float:
        """获取生命周期比例"""
        return self.life / self.max_life
    
    def get_current_color(self) -> Color:
        """获取当前颜色（支持渐变）"""
        # 确保颜色是 Color 对象
        color = self.color if isinstance(self.color, Color) else Color(*self.color[:3], 255)
        
        if self.end_color is None:
            return color.with_alpha(int(255 * self.life_ratio))
        
        end_color = self.end_color if isinstance(self.end_color, Color) else Color(*self.end_color[:3], 255)
        
        t = 1.0 - self.life_ratio
        r = int(color.r + (end_color.r - color.r) * t)
        g = int(color.g + (end_color.g - color.g) * t)
        b = int(color.b + (end_color.b - color.b) * t)
        a = int(color.a * self.life_ratio)
        return Color(r, g, b, a)
    
    def update(self, dt: float) -> None:
        """更新粒子状态"""
        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 应用重力
        self.vy -= self.gravity * dt
        
        # 更新生命周期
        self.life -= dt
        
        # 更新旋转
        self.rotation += self.rotation_speed * dt
        
        # 更新大小（根据曲线）
        self._update_size()
    
    def _update_size(self) -> None:
        """根据曲线更新大小"""
        life_ratio = self.life_ratio
        
        if self.size_curve == "linear":
            if self.size_decay > 0:
                self.size = max(0, self.size - self.size_decay * 0.016)
        elif self.size_curve == "grow":
            self.size = self.initial_size * (1.0 - life_ratio) * 2.0
        elif self.size_curve == "shrink":
            self.size = self.initial_size * life_ratio
        elif self.size_curve == "grow_shrink":
            if life_ratio > 0.5:
                self.size = self.initial_size * (1.0 - life_ratio) * 2.0
            else:
                self.size = self.initial_size * life_ratio * 2.0


class ParticleRenderer:
    """
    粒子渲染器 - 批量渲染优化版
    
    使用批量渲染技术提高性能
    """
    
    # 批量渲染缓冲区
    _circle_batch: List[Tuple[float, float, float, Color]] = []
    _line_batch: List[Tuple[float, float, float, float, Color, float]] = []
    _polygon_batch: List[Tuple[List[Tuple[float, float]], Color]] = []
    
    @classmethod
    def begin_batch(cls) -> None:
        """开始批量渲染"""
        cls._circle_batch.clear()
        cls._line_batch.clear()
        cls._polygon_batch.clear()
    
    @classmethod
    def end_batch(cls) -> None:
        """结束批量渲染并执行绘制"""
        # 批量绘制圆形
        if cls._circle_batch:
            for x, y, radius, color in cls._circle_batch:
                arcade.draw_circle_filled(x, y, radius, color.rgba)
        
        # 批量绘制线条
        if cls._line_batch:
            for x1, y1, x2, y2, color, width in cls._line_batch:
                arcade.draw_line(x1, y1, x2, y2, color.rgba, width)
        
        # 批量绘制多边形
        if cls._polygon_batch:
            for points, color in cls._polygon_batch:
                arcade.draw_polygon_filled(points, color.rgba)
    
    @staticmethod
    def draw_particle(particle: Particle) -> None:
        """绘制粒子 - 使用批量渲染"""
        if particle.size <= 0:
            return
        
        color = particle.get_current_color()
        shape = particle.shape
        
        if shape == ParticleShape.CIRCLE:
            ParticleRenderer._batch_circle(particle, color)
        elif shape == ParticleShape.STAR:
            ParticleRenderer._batch_star(particle, color)
        elif shape == ParticleShape.DIAMOND:
            ParticleRenderer._batch_diamond(particle, color)
        elif shape == ParticleShape.HEART:
            ParticleRenderer._batch_heart(particle, color)
        elif shape == ParticleShape.SQUARE:
            ParticleRenderer._batch_square(particle, color)
        elif shape == ParticleShape.TRIANGLE:
            ParticleRenderer._batch_triangle(particle, color)
        elif shape == ParticleShape.SPARK:
            ParticleRenderer._batch_spark(particle, color)
        elif shape == ParticleShape.RING:
            ParticleRenderer._batch_ring(particle, color)
        elif shape == ParticleShape.CROSS:
            ParticleRenderer._batch_cross(particle, color)
    
    @classmethod
    def _batch_circle(cls, particle: Particle, color: Color) -> None:
        """批量添加圆形粒子"""
        cls._circle_batch.append((particle.x, particle.y, particle.size, color))
        # 简化：不再绘制高光以减少绘制调用
    
    @staticmethod
    def _draw_circle(particle: Particle, color: Color) -> None:
        """绘制圆形粒子（单独绘制模式，保留用于兼容性）"""
        arcade.draw_circle_filled(
            particle.x, particle.y,
            particle.size,
            color.rgba
        )
    
    @classmethod
    def _batch_star(cls, particle: Particle, color: Color) -> None:
        """批量添加星形粒子"""
        x, y = particle.x, particle.y
        size = particle.size
        
        # 计算五角星顶点
        points = []
        for i in range(5):
            # 外顶点
            angle = particle.rotation + math.radians(i * 72 - 90)
            points.append((
                x + math.cos(angle) * size,
                y + math.sin(angle) * size
            ))
            # 内顶点
            angle = particle.rotation + math.radians(i * 72 + 36 - 90)
            points.append((
                x + math.cos(angle) * size * 0.4,
                y + math.sin(angle) * size * 0.4
            ))
        
        cls._polygon_batch.append((points, color))
    
    @staticmethod
    def _draw_star(particle: Particle, color: Color) -> None:
        """绘制星形粒子（单独绘制模式）"""
        ParticleRenderer._batch_star(particle, color)
    
    @classmethod
    def _batch_diamond(cls, particle: Particle, color: Color) -> None:
        """批量添加菱形粒子"""
        x, y = particle.x, particle.y
        size = particle.size
        
        # 菱形四个顶点
        points = [
            (x, y + size),           # 上
            (x + size * 0.7, y),     # 右
            (x, y - size),           # 下
            (x - size * 0.7, y),     # 左
        ]
        
        cls._polygon_batch.append((points, color))
    
    @staticmethod
    def _draw_diamond(particle: Particle, color: Color) -> None:
        """绘制菱形粒子（单独绘制模式）"""
        ParticleRenderer._batch_diamond(particle, color)
    
    @classmethod
    def _batch_heart(cls, particle: Particle, color: Color) -> None:
        """批量添加心形粒子（简化为圆形以提高性能）"""
        # 简化为圆形以提高批量渲染效率
        cls._circle_batch.append((particle.x, particle.y, particle.size * 0.8, color))
    
    @staticmethod
    def _draw_heart(particle: Particle, color: Color) -> None:
        """绘制心形粒子（单独绘制模式）"""
        ParticleRenderer._batch_heart(particle, color)
    
    @classmethod
    def _batch_square(cls, particle: Particle, color: Color) -> None:
        """批量添加方形粒子"""
        x, y = particle.x, particle.y
        size = particle.size
        half = size * 0.7
        
        # 方形用四个顶点表示
        points = [
            (x - half, y - half),
            (x + half, y - half),
            (x + half, y + half),
            (x - half, y + half),
        ]
        cls._polygon_batch.append((points, color))
    
    @staticmethod
    def _draw_square(particle: Particle, color: Color) -> None:
        """绘制方形粒子（单独绘制模式）"""
        ParticleRenderer._batch_square(particle, color)
    
    @classmethod
    def _batch_triangle(cls, particle: Particle, color: Color) -> None:
        """批量添加三角形粒子"""
        x, y = particle.x, particle.y
        size = particle.size
        
        # 等边三角形
        angle = particle.rotation
        points = []
        for i in range(3):
            a = angle + math.radians(i * 120 - 90)
            points.append((
                x + math.cos(a) * size,
                y + math.sin(a) * size
            ))
        
        cls._polygon_batch.append((points, color))
    
    @staticmethod
    def _draw_triangle(particle: Particle, color: Color) -> None:
        """绘制三角形粒子（单独绘制模式）"""
        ParticleRenderer._batch_triangle(particle, color)
    
    @classmethod
    def _batch_spark(cls, particle: Particle, color: Color) -> None:
        """批量添加火花粒子（简化为圆形以提高性能）"""
        # 简化为圆形以提高批量渲染效率
        cls._circle_batch.append((particle.x, particle.y, particle.size, color))
    
    @staticmethod
    def _draw_spark(particle: Particle, color: Color) -> None:
        """绘制火花粒子（单独绘制模式）"""
        ParticleRenderer._batch_spark(particle, color)
    
    @classmethod
    def _batch_ring(cls, particle: Particle, color: Color) -> None:
        """批量添加环形粒子（简化为圆形以提高性能）"""
        # 简化为圆形以提高批量渲染效率
        cls._circle_batch.append((particle.x, particle.y, particle.size * 0.9, color))
    
    @staticmethod
    def _draw_ring(particle: Particle, color: Color) -> None:
        """绘制环形粒子（单独绘制模式）"""
        ParticleRenderer._batch_ring(particle, color)
    
    @classmethod
    def _batch_cross(cls, particle: Particle, color: Color) -> None:
        """批量添加十字粒子（简化为圆形以提高性能）"""
        # 简化为圆形以提高批量渲染效率
        cls._circle_batch.append((particle.x, particle.y, particle.size * 0.7, color))
    
    @staticmethod
    def _draw_cross(particle: Particle, color: Color) -> None:
        """绘制十字粒子（单独绘制模式）"""
        ParticleRenderer._batch_cross(particle, color)


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
                   color: Color,
                   angle_min: float = 0, angle_max: float = 360,
                   gravity: float = 0.0,
                   shape: ParticleShape = ParticleShape.CIRCLE,
                   rotation_speed_range: Tuple[float, float] = (0, 0),
                   size_curve: str = "linear",
                   end_color: Optional[Color] = None) -> None:
        """
        发射一组粒子
        
        Args:
            count: 粒子数量
            speed_min, speed_max: 速度范围
            life_min, life_max: 生命周期范围
            size_min, size_max: 大小范围
            color: 颜色
            angle_min, angle_max: 角度范围（度）
            gravity: 重力
            shape: 粒子形状
            rotation_speed_range: 旋转速度范围
            size_curve: 大小变化曲线
            end_color: 结束颜色（用于渐变）
        """
        for _ in range(count):
            angle = math.radians(random.uniform(angle_min, angle_max))
            speed = random.uniform(speed_min, speed_max)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            life = random.uniform(life_min, life_max)
            size = random.uniform(size_min, size_max)
            rotation_speed = random.uniform(rotation_speed_range[0], rotation_speed_range[1])
            
            particle = Particle(
                x=self.x,
                y=self.y,
                vx=vx,
                vy=vy,
                life=life,
                max_life=life,
                size=size,
                color=color,
                alpha_decay=1.0 / life if life > 0 else 0,
                size_decay=0.0,
                gravity=gravity,
                shape=shape,
                rotation=random.uniform(0, 360),
                rotation_speed=rotation_speed,
                size_curve=size_curve,
                end_color=end_color
            )
            
            self.emit(particle)
    
    def update(self, dt: float) -> None:
        """更新所有粒子"""
        for particle in self.particles:
            particle.update(dt)
        
        self.particles = [p for p in self.particles if p.is_alive]
        
        if not self.particles:
            self.is_active = False
    
    def render(self) -> None:
        """渲染所有粒子 - 使用批量渲染"""
        if not self.particles:
            return
        
        # 开始批量渲染
        ParticleRenderer.begin_batch()
        
        # 添加所有粒子到批次
        for particle in self.particles:
            ParticleRenderer.draw_particle(particle)
        
        # 执行批量绘制
        ParticleRenderer.end_batch()
    
    def is_finished(self) -> bool:
        """检查发射器是否完成"""
        return not self.is_active and not self.particles


class ParticleSystem:
    """
    粒子系统管理器 - 增强版
    
    管理所有粒子发射器，使用Material Design配色
    """
    
    def __init__(self):
        self.emitters: List[ParticleEmitter] = []
    
    def update(self, dt: float) -> None:
        """更新所有发射器"""
        for emitter in self.emitters:
            emitter.update(dt)
        
        self.emitters = [e for e in self.emitters if not e.is_finished()]
    
    def render(self) -> None:
        """渲染所有发射器"""
        for emitter in self.emitters:
            emitter.render()
    
    def create_explosion(self, x: float, y: float, 
                        color: Optional[Color] = None,
                        count: int = 25,
                        size: float = 6.0) -> ParticleEmitter:
        """
        创建爆炸效果 - 增强版
        
        Args:
            x, y: 爆炸位置
            color: 主要颜色（默认使用EffectColors.EXPLOSION_CORE）
            count: 粒子数量
            size: 基础大小
        """
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = EffectColors.EXPLOSION_CORE
        
        # 核心火花（星形）
        emitter.emit_burst(
            count=count // 3,
            speed_min=100, speed_max=200,
            life_min=0.3, life_max=0.6,
            size_min=size * 0.8, size_max=size * 1.5,
            color=SECONDARY_LIGHT,
            angle_min=0, angle_max=360,
            gravity=50.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-180, 180),
            size_curve="shrink",
            end_color=EffectColors.EXPLOSION_OUTER
        )
        
        # 火焰粒子
        emitter.emit_burst(
            count=count // 2,
            speed_min=60, speed_max=150,
            life_min=0.4, life_max=0.8,
            size_min=size * 0.5, size_max=size * 1.2,
            color=color,
            angle_min=0, angle_max=360,
            gravity=100.0,
            shape=ParticleShape.DIAMOND,
            size_curve="shrink",
            end_color=EffectColors.EXPLOSION_OUTER
        )
        
        # 烟雾粒子
        emitter.emit_burst(
            count=count // 3,
            speed_min=20, speed_max=60,
            life_min=0.6, life_max=1.2,
            size_min=size * 1.5, size_max=size * 3.0,
            color=EffectColors.EXPLOSION_SMOKE.with_alpha(150),
            angle_min=0, angle_max=360,
            gravity=-30.0,
            shape=ParticleShape.CIRCLE,
            size_curve="grow"
        )
        
        # 火花
        emitter.emit_burst(
            count=count // 4,
            speed_min=80, speed_max=180,
            life_min=0.2, life_max=0.4,
            size_min=2, size_max=4,
            color=SECONDARY,
            angle_min=0, angle_max=360,
            shape=ParticleShape.SPARK,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_hit_effect(self, x: float, y: float,
                         color: Optional[Color] = None,
                         count: int = 12) -> ParticleEmitter:
        """创建击中效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = SECONDARY_LIGHT
        
        # 火花
        emitter.emit_burst(
            count=count,
            speed_min=40, speed_max=100,
            life_min=0.2, life_max=0.5,
            size_min=2, size_max=5,
            color=color,
            angle_min=0, angle_max=360,
            shape=ParticleShape.SPARK,
            size_curve="shrink"
        )
        
        # 小碎片
        emitter.emit_burst(
            count=count // 2,
            speed_min=30, speed_max=80,
            life_min=0.3, life_max=0.6,
            size_min=1, size_max=3,
            color=WHITE.with_alpha(200),
            angle_min=0, angle_max=360,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_collect_effect(self, x: float, y: float,
                             color: Optional[Color] = None,
                             count: int = 18) -> ParticleEmitter:
        """创建收集效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = SECONDARY
        
        # 星形粒子向上飘
        emitter.emit_burst(
            count=count,
            speed_min=50, speed_max=120,
            life_min=0.4, life_max=0.8,
            size_min=3, size_max=7,
            color=color,
            angle_min=0, angle_max=360,
            gravity=-60.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-120, 120),
            size_curve="shrink",
            end_color=SECONDARY_LIGHT
        )
        
        # 小圆点
        emitter.emit_burst(
            count=count // 2,
            speed_min=30, speed_max=80,
            life_min=0.3, life_max=0.6,
            size_min=2, size_max=4,
            color=WHITE.with_alpha(200),
            angle_min=0, angle_max=360,
            gravity=-40.0,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_plant_effect(self, x: float, y: float,
                           color: Optional[Color] = None,
                           count: int = 15) -> ParticleEmitter:
        """创建种植效果（增强版）"""
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = GameColors.PLANT_PEASHOOTER
        
        # 土粒向上喷发
        emitter.emit_burst(
            count=count,
            speed_min=40, speed_max=100,
            life_min=0.4, life_max=0.8,
            size_min=3, size_max=6,
            color=GameColors.DIRT,
            angle_min=180, angle_max=360,
            gravity=150.0,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        # 绿色闪光（植物能量）
        emitter.emit_burst(
            count=count // 2,
            speed_min=15, speed_max=50,
            life_min=0.3, life_max=0.6,
            size_min=4, size_max=10,
            color=color.lighten(0.3),
            angle_min=0, angle_max=360,
            gravity=-40.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-120, 120),
            size_curve="grow_shrink"
        )
        
        # 小草叶
        emitter.emit_burst(
            count=5,
            speed_min=25, speed_max=60,
            life_min=0.5, life_max=1.0,
            size_min=5, size_max=12,
            color=GameColors.GRASS_LIGHT,
            angle_min=200, angle_max=340,
            gravity=100.0,
            shape=ParticleShape.TRIANGLE,
            rotation_speed_range=(-180, 180),
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_zombie_death_effect(self, x: float, y: float,
                                   count: int = 30) -> ParticleEmitter:
        """创建僵尸死亡效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        # 灰色碎片
        emitter.emit_burst(
            count=count // 2,
            speed_min=40, speed_max=120,
            life_min=0.4, life_max=1.0,
            size_min=3, size_max=8,
            color=GameColors.ZOMBIE_SHIRT,
            angle_min=0, angle_max=360,
            gravity=100.0,
            shape=ParticleShape.SQUARE,
            rotation_speed_range=(-180, 180),
            size_curve="shrink"
        )
        
        # 绿色皮肤碎片
        emitter.emit_burst(
            count=count // 3,
            speed_min=30, speed_max=100,
            life_min=0.3, life_max=0.8,
            size_min=2, size_max=6,
            color=GameColors.ZOMBIE_SKIN,
            angle_min=0, angle_max=360,
            gravity=120.0,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        # 红色粒子（血迹）
        emitter.emit_burst(
            count=count // 3,
            speed_min=25, speed_max=80,
            life_min=0.3, life_max=0.7,
            size_min=2, size_max=5,
            color=StatusColors.ERROR.darken(0.2),
            angle_min=0, angle_max=360,
            gravity=150.0,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_projectile_trail(self, x: float, y: float,
                                color: Optional[Color] = None,
                                size: float = 3.5) -> ParticleEmitter:
        """创建投射物尾迹效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = GameColors.PEA_NORMAL
        
        emitter.emit_burst(
            count=2,
            speed_min=0, speed_max=15,
            life_min=0.1, life_max=0.3,
            size_min=size * 0.5, size_max=size,
            color=color.with_alpha(180),
            angle_min=0, angle_max=360,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_sun_glow(self, x: float, y: float,
                       count: int = 10) -> ParticleEmitter:
        """创建阳光发光效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        # 黄色光晕
        emitter.emit_burst(
            count=count,
            speed_min=15, speed_max=40,
            life_min=0.5, life_max=1.2,
            size_min=2, size_max=6,
            color=SECONDARY_LIGHT,
            angle_min=0, angle_max=360,
            gravity=-30.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-60, 60),
            size_curve="grow_shrink"
        )
        
        # 橙色核心
        emitter.emit_burst(
            count=count // 2,
            speed_min=10, speed_max=25,
            life_min=0.3, life_max=0.7,
            size_min=1, size_max=4,
            color=SECONDARY,
            angle_min=0, angle_max=360,
            shape=ParticleShape.CIRCLE,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_ice_effect(self, x: float, y: float,
                         count: int = 18) -> ParticleEmitter:
        """创建寒冰效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        # 冰晶
        emitter.emit_burst(
            count=count,
            speed_min=30, speed_max=80,
            life_min=0.4, life_max=1.0,
            size_min=2, size_max=5,
            color=EffectColors.ICE_OUTER,
            angle_min=0, angle_max=360,
            gravity=-40.0,
            shape=ParticleShape.DIAMOND,
            rotation_speed_range=(-120, 120),
            size_curve="shrink",
            end_color=EffectColors.ICE_CORE
        )
        
        # 雪花
        emitter.emit_burst(
            count=count // 2,
            speed_min=15, speed_max=50,
            life_min=0.6, life_max=1.2,
            size_min=1, size_max=3,
            color=EffectColors.ICE_SPARKLE.with_alpha(200),
            angle_min=0, angle_max=360,
            gravity=-60.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-45, 45),
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_fire_effect(self, x: float, y: float,
                          count: int = 25) -> ParticleEmitter:
        """创建火焰效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        # 红色火焰核心
        emitter.emit_burst(
            count=count // 2,
            speed_min=40, speed_max=100,
            life_min=0.3, life_max=0.7,
            size_min=4, size_max=8,
            color=EffectColors.FIRE_CORE,
            angle_min=180, angle_max=360,
            gravity=-120.0,
            shape=ParticleShape.TRIANGLE,
            rotation_speed_range=(-80, 80),
            size_curve="grow_shrink"
        )
        
        # 橙色火焰外层
        emitter.emit_burst(
            count=count // 2,
            speed_min=25, speed_max=80,
            life_min=0.4, life_max=0.9,
            size_min=3, size_max=7,
            color=EffectColors.FIRE_MIDDLE,
            angle_min=180, angle_max=360,
            gravity=-100.0,
            shape=ParticleShape.CIRCLE,
            size_curve="grow_shrink"
        )
        
        # 黄色火花
        emitter.emit_burst(
            count=count // 3,
            speed_min=50, speed_max=120,
            life_min=0.2, life_max=0.5,
            size_min=1, size_max=4,
            color=EffectColors.FIRE_OUTER,
            angle_min=0, angle_max=360,
            shape=ParticleShape.SPARK,
            size_curve="shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_sparkle_effect(self, x: float, y: float,
                             color: Optional[Color] = None,
                             count: int = 12) -> ParticleEmitter:
        """创建闪烁效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        if color is None:
            color = WHITE
        
        emitter.emit_burst(
            count=count,
            speed_min=20, speed_max=60,
            life_min=0.3, life_max=0.8,
            size_min=1, size_max=4,
            color=color,
            angle_min=0, angle_max=360,
            gravity=-50.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-150, 150),
            size_curve="grow_shrink"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_cherry_bomb_explosion(self, x: float, y: float) -> ParticleEmitter:
        """创建樱桃炸弹爆炸效果（增强版）"""
        emitter = ParticleEmitter(x, y)
        
        # 核心爆炸
        emitter.emit_burst(
            count=35,
            speed_min=120, speed_max=250,
            life_min=0.3, life_max=0.7,
            size_min=10, size_max=18,
            color=SECONDARY,
            angle_min=0, angle_max=360,
            gravity=60.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-360, 360),
            size_curve="shrink",
            end_color=EffectColors.EXPLOSION_OUTER
        )
        
        # 火焰环
        emitter.emit_burst(
            count=50,
            speed_min=60, speed_max=180,
            life_min=0.4, life_max=1.0,
            size_min=6, size_max=12,
            color=EffectColors.EXPLOSION_CORE,
            angle_min=0, angle_max=360,
            gravity=40.0,
            shape=ParticleShape.DIAMOND,
            rotation_speed_range=(-200, 200),
            size_curve="shrink"
        )
        
        # 烟雾
        emitter.emit_burst(
            count=25,
            speed_min=25, speed_max=60,
            life_min=0.8, life_max=1.8,
            size_min=18, size_max=30,
            color=EffectColors.EXPLOSION_SMOKE.with_alpha(120),
            angle_min=0, angle_max=360,
            gravity=-30.0,
            shape=ParticleShape.CIRCLE,
            size_curve="grow"
        )
        
        # 冲击波环
        emitter.emit_burst(
            count=8,
            speed_min=150, speed_max=200,
            life_min=0.2, life_max=0.4,
            size_min=15, size_max=25,
            color=SECONDARY_LIGHT.with_alpha(150),
            angle_min=0, angle_max=360,
            shape=ParticleShape.RING,
            size_curve="grow"
        )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_pea_hit(self, x: float, y: float, is_frozen: bool = False) -> ParticleEmitter:
        """创建豌豆击中效果 - 增强版"""
        emitter = ParticleEmitter(x, y)
        
        if is_frozen:
            # 冰豌豆击中
            emitter.emit_burst(
                count=10,
                speed_min=40, speed_max=80,
                life_min=0.3, life_max=0.6,
                size_min=2, size_max=5,
                color=EffectColors.ICE_OUTER,
                angle_min=0, angle_max=360,
                gravity=-30.0,
                shape=ParticleShape.DIAMOND,
                rotation_speed_range=(-120, 120),
                size_curve="shrink",
                end_color=EffectColors.ICE_CORE
            )
            
            # 冰晶碎片
            emitter.emit_burst(
                count=6,
                speed_min=30, speed_max=60,
                life_min=0.4, life_max=0.7,
                size_min=1, size_max=3,
                color=EffectColors.ICE_SPARKLE.with_alpha(200),
                angle_min=0, angle_max=360,
                shape=ParticleShape.SPARK,
                size_curve="shrink"
            )
        else:
            # 普通豌豆击中
            emitter.emit_burst(
                count=8,
                speed_min=40, speed_max=80,
                life_min=0.2, life_max=0.5,
                size_min=2, size_max=4,
                color=GameColors.PEA_NORMAL.lighten(0.3),
                angle_min=0, angle_max=360,
                shape=ParticleShape.CIRCLE,
                size_curve="shrink"
            )
            
            # 小碎片
            emitter.emit_burst(
                count=5,
                speed_min=50, speed_max=100,
                life_min=0.15, life_max=0.3,
                size_min=1, size_max=3,
                color=WHITE.with_alpha(200),
                angle_min=0, angle_max=360,
                shape=ParticleShape.SPARK,
                size_curve="shrink"
            )
        
        self.emitters.append(emitter)
        return emitter
    
    def create_level_up_effect(self, x: float, y: float) -> ParticleEmitter:
        """创建升级效果"""
        emitter = ParticleEmitter(x, y)
        
        # 金色星形
        emitter.emit_burst(
            count=20,
            speed_min=60, speed_max=150,
            life_min=0.5, life_max=1.0,
            size_min=4, size_max=10,
            color=SECONDARY,
            angle_min=0, angle_max=360,
            gravity=-40.0,
            shape=ParticleShape.STAR,
            rotation_speed_range=(-180, 180),
            size_curve="grow_shrink"
        )
        
        # 闪光粒子
        emitter.emit_burst(
            count=15,
            speed_min=40, speed_max=100,
            life_min=0.4, life_max=0.8,
            size_min=2, size_max=6,
            color=WHITE,
            angle_min=0, angle_max=360,
            gravity=-30.0,
            shape=ParticleShape.SPARK,
            size_curve="shrink"
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
