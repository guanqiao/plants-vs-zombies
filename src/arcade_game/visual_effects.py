"""
视觉反馈特效系统 - 提供攻击和特殊效果的视觉反馈

包括：
- 攻击闪光效果
- 波纹扩散效果
- 爆炸闪光效果
- 冰霜视觉效果
- 冲击波效果
"""

import math
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class EffectType(Enum):
    """特效类型"""
    FLASH = auto()        # 闪光
    RIPPLE = auto()       # 波纹
    EXPLOSION = auto()    # 爆炸
    FROST = auto()        # 冰霜
    SHOCKWAVE = auto()    # 冲击波
    HIT_SPARK = auto()    # 击中火花
    PLANTING_RING = auto() # 种植魔法圈
    PORTAL = auto()        # 传送门
    GLOW = auto()          # 发光效果


@dataclass
class VisualEffect:
    """视觉特效基类"""
    x: float
    y: float
    effect_type: EffectType
    life: float
    max_life: float
    is_alive: bool = True
    
    def update(self, dt: float) -> None:
        """更新特效"""
        self.life -= dt
        if self.life <= 0:
            self.is_alive = False
    
    @property
    def progress(self) -> float:
        """获取进度 (0-1)"""
        return 1.0 - (self.life / self.max_life)


@dataclass
class FlashEffect(VisualEffect):
    """闪光效果"""
    radius: float = 50.0
    color: Tuple[int, int, int] = (255, 255, 255)
    intensity: float = 1.0
    
    def __post_init__(self):
        self.effect_type = EffectType.FLASH


@dataclass
class RippleEffect(VisualEffect):
    """波纹效果"""
    radius: float = 10.0
    max_radius: float = 100.0
    color: Tuple[int, int, int] = (255, 255, 255)
    thickness: float = 3.0
    
    def __post_init__(self):
        self.effect_type = EffectType.RIPPLE
    
    def update(self, dt: float) -> None:
        super().update(dt)
        # 半径随时间扩大
        self.radius = self.max_radius * self.progress


@dataclass
class ExplosionEffect(VisualEffect):
    """爆炸效果"""
    radius: float = 20.0
    max_radius: float = 150.0
    color: Tuple[int, int, int] = (255, 150, 50)
    ring_count: int = 3
    
    def __post_init__(self):
        self.effect_type = EffectType.EXPLOSION
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.radius = self.max_radius * self.progress


@dataclass
class FrostEffect(VisualEffect):
    """冰霜效果"""
    radius: float = 60.0
    crystal_count: int = 8
    rotation: float = 0.0
    rotation_speed: float = 90.0
    
    def __post_init__(self):
        self.effect_type = EffectType.FROST
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.rotation += self.rotation_speed * dt


@dataclass
class ShockwaveEffect(VisualEffect):
    """冲击波效果"""
    radius: float = 10.0
    max_radius: float = 200.0
    color: Tuple[int, int, int] = (255, 200, 100)
    wave_count: int = 2
    
    def __post_init__(self):
        self.effect_type = EffectType.SHOCKWAVE
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.radius = self.max_radius * self.progress


@dataclass
class HitSparkEffect(VisualEffect):
    """击中火花效果"""
    spark_count: int = 6
    length: float = 20.0
    color: Tuple[int, int, int] = (255, 255, 100)
    
    def __post_init__(self):
        self.effect_type = EffectType.HIT_SPARK


@dataclass
class PlantingRingEffect(VisualEffect):
    """种植魔法圈效果"""
    radius: float = 40.0
    max_radius: float = 60.0
    color: Tuple[int, int, int] = (100, 200, 100)
    ring_count: int = 3
    
    def __post_init__(self):
        self.effect_type = EffectType.PLANTING_RING
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.radius = self.max_radius * (1.0 - self.progress * 0.5)


@dataclass
class PortalEffect(VisualEffect):
    """传送门效果"""
    radius: float = 30.0
    max_radius: float = 50.0
    color: Tuple[int, int, int] = (150, 100, 200)
    rotation: float = 0.0
    rotation_speed: float = 180.0
    
    def __post_init__(self):
        self.effect_type = EffectType.PORTAL
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.rotation += self.rotation_speed * dt
        self.radius = self.max_radius * (1.0 - self.progress * 0.3)


@dataclass
class GlowEffect(VisualEffect):
    """发光效果"""
    radius: float = 40.0
    max_radius: float = 60.0
    color: Tuple[int, int, int] = (255, 255, 200)
    pulse_speed: float = 2.0
    phase: float = 0.0
    
    def __post_init__(self):
        self.effect_type = EffectType.GLOW
    
    def update(self, dt: float) -> None:
        super().update(dt)
        self.phase += self.pulse_speed * dt
        self.radius = self.max_radius * (0.7 + 0.3 * math.sin(self.phase))


class VisualEffectsSystem:
    """
    视觉特效系统
    
    管理和渲染所有视觉特效
    """
    
    def __init__(self):
        self.effects: List[VisualEffect] = []
    
    def update(self, dt: float) -> None:
        """更新所有特效"""
        for effect in self.effects:
            effect.update(dt)
        
        # 移除已结束的特效
        self.effects = [e for e in self.effects if e.is_alive]
    
    def render(self) -> None:
        """渲染所有特效"""
        for effect in self.effects:
            self._render_effect(effect)
    
    def _render_effect(self, effect: VisualEffect) -> None:
        """渲染单个特效"""
        if effect.effect_type == EffectType.FLASH:
            self._render_flash(effect)
        elif effect.effect_type == EffectType.RIPPLE:
            self._render_ripple(effect)
        elif effect.effect_type == EffectType.EXPLOSION:
            self._render_explosion(effect)
        elif effect.effect_type == EffectType.FROST:
            self._render_frost(effect)
        elif effect.effect_type == EffectType.SHOCKWAVE:
            self._render_shockwave(effect)
        elif effect.effect_type == EffectType.HIT_SPARK:
            self._render_hit_spark(effect)
        elif effect.effect_type == EffectType.PLANTING_RING:
            self._render_planting_ring(effect)
        elif effect.effect_type == EffectType.PORTAL:
            self._render_portal(effect)
        elif effect.effect_type == EffectType.GLOW:
            self._render_glow(effect)
    
    def _render_flash(self, effect: FlashEffect) -> None:
        """渲染闪光效果"""
        alpha = int(255 * (1.0 - effect.progress) * effect.intensity)
        
        # 多层发光
        for i in range(3):
            r = effect.radius * (1.0 + i * 0.3)
            a = max(0, alpha - i * 50)
            if a > 0:
                color = (*effect.color, a)
                arcade.draw_circle_filled(effect.x, effect.y, r, color)
    
    def _render_ripple(self, effect: RippleEffect) -> None:
        """渲染波纹效果"""
        alpha = int(200 * (1.0 - effect.progress))
        color = (*effect.color, alpha)
        
        # 绘制圆环
        arcade.draw_circle_outline(
            effect.x, effect.y,
            effect.radius, color,
            max(1, effect.thickness * (1.0 - effect.progress))
        )
    
    def _render_explosion(self, effect: ExplosionEffect) -> None:
        """渲染爆炸效果"""
        alpha = int(255 * (1.0 - effect.progress))
        
        # 绘制多层爆炸环
        for i in range(effect.ring_count):
            ring_progress = max(0, effect.progress - i * 0.15)
            if ring_progress < 1.0:
                r = effect.max_radius * ring_progress
                a = int(alpha * (1.0 - ring_progress))
                
                # 内部颜色
                inner_color = (effect.color[0], effect.color[1], effect.color[2], a)
                arcade.draw_circle_outline(effect.x, effect.y, r, inner_color, 4 - i)
        
        # 中心闪光
        if effect.progress < 0.3:
            flash_alpha = int(255 * (1.0 - effect.progress / 0.3))
            arcade.draw_circle_filled(
                effect.x, effect.y,
                effect.radius * 0.5,
                (255, 255, 200, flash_alpha)
            )
    
    def _render_frost(self, effect: FrostEffect) -> None:
        """渲染冰霜效果"""
        alpha = int(200 * (1.0 - effect.progress))
        
        # 绘制冰晶
        for i in range(effect.crystal_count):
            angle = math.radians(effect.rotation + i * (360 / effect.crystal_count))
            
            # 冰晶形状
            crystal_length = effect.radius * (0.8 + 0.2 * math.sin(effect.progress * math.pi))
            
            # 主干
            x1 = effect.x + math.cos(angle) * effect.radius * 0.3
            y1 = effect.y + math.sin(angle) * effect.radius * 0.3
            x2 = effect.x + math.cos(angle) * crystal_length
            y2 = effect.y + math.sin(angle) * crystal_length
            
            color = (200, 230, 255, alpha)
            arcade.draw_line(x1, y1, x2, y2, color, 3)
            
            # 分支
            branch_angle1 = angle + math.radians(30)
            branch_angle2 = angle - math.radians(30)
            branch_length = crystal_length * 0.4
            
            bx1 = effect.x + math.cos(angle) * crystal_length * 0.6
            by1 = effect.y + math.sin(angle) * crystal_length * 0.6
            
            arcade.draw_line(
                bx1, by1,
                bx1 + math.cos(branch_angle1) * branch_length,
                by1 + math.sin(branch_angle1) * branch_length,
                color, 2
            )
            arcade.draw_line(
                bx1, by1,
                bx1 + math.cos(branch_angle2) * branch_length,
                by1 + math.sin(branch_angle2) * branch_length,
                color, 2
            )
        
        # 中心圆
        arcade.draw_circle_filled(
            effect.x, effect.y,
            effect.radius * 0.2,
            (220, 240, 255, alpha)
        )
    
    def _render_shockwave(self, effect: ShockwaveEffect) -> None:
        """渲染冲击波效果"""
        alpha = int(180 * (1.0 - effect.progress))
        
        # 绘制多个波
        for i in range(effect.wave_count):
            wave_progress = max(0, effect.progress - i * 0.2)
            if wave_progress < 1.0:
                r = effect.max_radius * wave_progress
                a = int(alpha * (1.0 - wave_progress))
                
                # 渐变圆环
                color = (*effect.color, a)
                arcade.draw_circle_outline(effect.x, effect.y, r, color, 6 - i * 2)
                
                # 内部填充（半透明）
                inner_color = (effect.color[0], effect.color[1], effect.color[2], a // 3)
                arcade.draw_circle_filled(effect.x, effect.y, r, inner_color)
    
    def _render_hit_spark(self, effect: HitSparkEffect) -> None:
        """渲染击中火花效果"""
        alpha = int(255 * (1.0 - effect.progress))
        length = effect.length * (1.0 - effect.progress * 0.5)
        
        # 绘制放射状火花
        for i in range(effect.spark_count):
            angle = math.radians(i * (360 / effect.spark_count) + effect.progress * 180)
            
            x1 = effect.x
            y1 = effect.y
            x2 = effect.x + math.cos(angle) * length
            y2 = effect.y + math.sin(angle) * length
            
            color = (*effect.color, alpha)
            arcade.draw_line(x1, y1, x2, y2, color, 2)
            
            # 火花末端小点
            arcade.draw_circle_filled(x2, y2, 2, color)
    
    def _render_planting_ring(self, effect: PlantingRingEffect) -> None:
        """渲染种植魔法圈效果"""
        alpha = int(200 * (1.0 - effect.progress))
        
        # 绘制多层魔法圈
        for i in range(effect.ring_count):
            ring_offset = i * 0.2
            if effect.progress > ring_offset:
                ring_progress = min(1.0, (effect.progress - ring_offset) / 0.8)
                r = effect.max_radius * (0.6 + 0.4 * ring_progress)
                a = int(alpha * (1.0 - ring_progress))
                
                color = (*effect.color, a)
                thickness = 4 - i
                
                # 绘制圆环
                arcade.draw_circle_outline(effect.x, effect.y, r, color, max(1, thickness))
                
                # 绘制符文装饰
                if i == 0:
                    rune_count = 8
                    for j in range(rune_count):
                        rune_angle = math.radians(j * (360 / rune_count))
                        rune_x = effect.x + math.cos(rune_angle) * r
                        rune_y = effect.y + math.sin(rune_angle) * r
                        arcade.draw_circle_filled(rune_x, rune_y, 4, color)
    
    def _render_portal(self, effect: PortalEffect) -> None:
        """渲染传送门效果"""
        alpha = int(200 * (1.0 - effect.progress))
        
        # 绘制多层旋转圆环
        for i in range(3):
            offset_angle = math.radians(effect.rotation + i * 60)
            r = effect.radius * (1.0 - i * 0.2)
            a = int(alpha * (1.0 - i * 0.2))
            
            color = (*effect.color, a)
            arcade.draw_circle_outline(effect.x, effect.y, r, color, 3 - i)
            
            # 绘制旋转粒子
            particle_count = 6
            for j in range(particle_count):
                particle_angle = offset_angle + math.radians(j * (360 / particle_count))
                px = effect.x + math.cos(particle_angle) * r
                py = effect.y + math.sin(particle_angle) * r
                arcade.draw_circle_filled(px, py, 3, color)
        
        # 中心发光
        center_alpha = int(150 * (1.0 - effect.progress))
        arcade.draw_circle_filled(
            effect.x, effect.y,
            effect.radius * 0.3,
            (*effect.color, center_alpha)
        )
    
    def _render_glow(self, effect: GlowEffect) -> None:
        """渲染发光效果"""
        alpha = int(200 * (1.0 - effect.progress))
        
        # 绘制多层光晕
        for i in range(3):
            r = effect.radius * (1.0 + i * 0.3)
            a = int(alpha * (1.0 - i * 0.25))
            color = (*effect.color, a)
            arcade.draw_circle_filled(effect.x, effect.y, r, color)
        
        # 核心高光
        arcade.draw_circle_filled(
            effect.x, effect.y,
            effect.radius * 0.3,
            (*effect.color, alpha)
        )
    
    # === 创建特效的工厂方法 ===
    
    def create_flash(self, x: float, y: float, 
                    radius: float = 50.0,
                    color: Tuple[int, int, int] = (255, 255, 255),
                    duration: float = 0.2,
                    intensity: float = 1.0) -> FlashEffect:
        """创建闪光效果"""
        effect = FlashEffect(
            x=x, y=y,
            effect_type=EffectType.FLASH,
            life=duration, max_life=duration,
            radius=radius, color=color, intensity=intensity
        )
        self.effects.append(effect)
        return effect
    
    def create_ripple(self, x: float, y: float,
                     max_radius: float = 100.0,
                     color: Tuple[int, int, int] = (255, 255, 255),
                     duration: float = 0.5) -> RippleEffect:
        """创建波纹效果"""
        effect = RippleEffect(
            x=x, y=y,
            effect_type=EffectType.RIPPLE,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_explosion(self, x: float, y: float,
                        max_radius: float = 150.0,
                        color: Tuple[int, int, int] = (255, 150, 50),
                        duration: float = 0.6) -> ExplosionEffect:
        """创建爆炸效果"""
        effect = ExplosionEffect(
            x=x, y=y,
            effect_type=EffectType.EXPLOSION,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_frost(self, x: float, y: float,
                    radius: float = 60.0,
                    duration: float = 0.8) -> FrostEffect:
        """创建冰霜效果"""
        effect = FrostEffect(
            x=x, y=y,
            effect_type=EffectType.FROST,
            life=duration, max_life=duration,
            radius=radius
        )
        self.effects.append(effect)
        return effect
    
    def create_shockwave(self, x: float, y: float,
                        max_radius: float = 200.0,
                        color: Tuple[int, int, int] = (255, 200, 100),
                        duration: float = 0.5) -> ShockwaveEffect:
        """创建冲击波效果"""
        effect = ShockwaveEffect(
            x=x, y=y,
            effect_type=EffectType.SHOCKWAVE,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_hit_spark(self, x: float, y: float,
                        length: float = 20.0,
                        color: Tuple[int, int, int] = (255, 255, 100),
                        duration: float = 0.3) -> HitSparkEffect:
        """创建击中火花效果"""
        effect = HitSparkEffect(
            x=x, y=y,
            effect_type=EffectType.HIT_SPARK,
            life=duration, max_life=duration,
            length=length, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_cherry_bomb_visual(self, x: float, y: float) -> None:
        """创建樱桃炸弹视觉效果"""
        # 大爆炸
        self.create_explosion(x, y, max_radius=180, color=(255, 100, 50), duration=0.8)
        # 冲击波
        self.create_shockwave(x, y, max_radius=220, color=(255, 200, 100), duration=0.6)
        # 闪光
        self.create_flash(x, y, radius=100, color=(255, 255, 200), duration=0.3, intensity=1.5)
    
    def create_pea_hit_visual(self, x: float, y: float, is_frozen: bool = False) -> None:
        """创建豌豆击中视觉效果"""
        if is_frozen:
            self.create_frost(x, y, radius=40, duration=0.5)
            self.create_hit_spark(x, y, length=15, color=(150, 200, 255), duration=0.25)
        else:
            self.create_hit_spark(x, y, length=15, color=(100, 255, 100), duration=0.2)
            self.create_ripple(x, y, max_radius=30, color=(100, 255, 100), duration=0.3)
    
    def create_zombie_hit_visual(self, x: float, y: float) -> None:
        """创建僵尸被击中视觉效果"""
        self.create_hit_spark(x, y, length=12, color=(255, 200, 100), duration=0.2)
    
    def create_plant_death_visual(self, x: float, y: float) -> None:
        """创建植物死亡视觉效果"""
        self.create_ripple(x, y, max_radius=50, color=(100, 200, 100), duration=0.4)
    
    def create_sun_spawn_visual(self, x: float, y: float) -> None:
        """创建阳光生成视觉效果"""
        self.create_flash(x, y, radius=30, color=(255, 255, 150), duration=0.2)
        self.create_ripple(x, y, max_radius=40, color=(255, 255, 100), duration=0.4)
    
    def create_planting_ring(self, x: float, y: float,
                            max_radius: float = 60.0,
                            color: Tuple[int, int, int] = (100, 200, 100),
                            duration: float = 0.6) -> PlantingRingEffect:
        """创建种植魔法圈效果"""
        effect = PlantingRingEffect(
            x=x, y=y,
            effect_type=EffectType.PLANTING_RING,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_portal(self, x: float, y: float,
                     max_radius: float = 50.0,
                     color: Tuple[int, int, int] = (150, 100, 200),
                     duration: float = 0.8) -> PortalEffect:
        """创建传送门效果"""
        effect = PortalEffect(
            x=x, y=y,
            effect_type=EffectType.PORTAL,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_glow(self, x: float, y: float,
                   max_radius: float = 60.0,
                   color: Tuple[int, int, int] = (255, 255, 200),
                   duration: float = 0.8) -> GlowEffect:
        """创建发光效果"""
        effect = GlowEffect(
            x=x, y=y,
            effect_type=EffectType.GLOW,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_planting_visual(self, x: float, y: float) -> None:
        """创建种植视觉效果组合"""
        self.create_planting_ring(x, y, max_radius=60, color=(100, 200, 100), duration=0.6)
        self.create_glow(x, y, max_radius=40, color=(150, 255, 150), duration=0.4)
        self.create_ripple(x, y, max_radius=50, color=(100, 200, 100), duration=0.5)
    
    def create_zombie_spawn_visual(self, x: float, y: float) -> None:
        """创建僵尸生成视觉效果"""
        self.create_portal(x, y, max_radius=50, color=(150, 100, 200), duration=0.8)
        self.create_ripple(x, y, max_radius=60, color=(150, 100, 200), duration=0.6)
    
    def clear(self) -> None:
        """清除所有特效"""
        self.effects.clear()
    
    def get_active_count(self) -> int:
        """获取活动特效数量"""
        return len(self.effects)
