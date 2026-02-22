"""
视觉反馈特效系统 - 优化版

优化点：
- 使用批量渲染减少绘制调用
- 简化复杂特效以减少计算
- 合并相似绘制操作
"""

import math
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade

from .visual_effects import (
    EffectType, VisualEffect, FlashEffect, RippleEffect,
    ExplosionEffect, FrostEffect, ShockwaveEffect, HitSparkEffect,
    PlantingRingEffect, PortalEffect, GlowEffect
)
from ..core.performance_monitor import log_draw_call


class OptimizedVisualEffectsSystem:
    """
    优化的视觉特效系统
    
    使用批量渲染技术提高性能
    """
    
    def __init__(self):
        self.effects: List[VisualEffect] = []
        
        # 批量渲染缓冲区
        self._circle_filled_batch: List[Tuple[float, float, float, Tuple[int, ...]]] = []
        self._circle_outline_batch: List[Tuple[float, float, float, Tuple[int, ...], float]] = []
        self._line_batch: List[Tuple[float, float, float, float, Tuple[int, ...], float]] = []
    
    def update(self, dt: float) -> None:
        """更新所有特效"""
        for effect in self.effects:
            effect.update(dt)
        
        # 移除已结束的特效
        self.effects = [e for e in self.effects if e.is_alive]
    
    def render(self) -> None:
        """渲染所有特效 - 使用批量渲染"""
        if not self.effects:
            return
        
        # 清空批次
        self._clear_batches()
        
        # 收集所有绘制命令
        for effect in self.effects:
            self._collect_effect_commands(effect)
        
        # 执行批量绘制
        self._execute_batch_draw()
    
    def _clear_batches(self) -> None:
        """清空批次缓冲区"""
        self._circle_filled_batch.clear()
        self._circle_outline_batch.clear()
        self._line_batch.clear()
    
    def _collect_effect_commands(self, effect: VisualEffect) -> None:
        """收集特效的绘制命令"""
        if effect.effect_type == EffectType.FLASH:
            self._collect_flash_commands(effect)
        elif effect.effect_type == EffectType.RIPPLE:
            self._collect_ripple_commands(effect)
        elif effect.effect_type == EffectType.EXPLOSION:
            self._collect_explosion_commands(effect)
        elif effect.effect_type == EffectType.FROST:
            self._collect_frost_commands(effect)
        elif effect.effect_type == EffectType.SHOCKWAVE:
            self._collect_shockwave_commands(effect)
        elif effect.effect_type == EffectType.HIT_SPARK:
            self._collect_hit_spark_commands(effect)
        elif effect.effect_type == EffectType.PLANTING_RING:
            self._collect_planting_ring_commands(effect)
        elif effect.effect_type == EffectType.PORTAL:
            self._collect_portal_commands(effect)
        elif effect.effect_type == EffectType.GLOW:
            self._collect_glow_commands(effect)
    
    def _execute_batch_draw(self) -> None:
        """执行批量绘制"""
        # 批量绘制填充圆形
        if self._circle_filled_batch:
            for x, y, radius, color in self._circle_filled_batch:
                arcade.draw_circle_filled(x, y, radius, color)
            log_draw_call(len(self._circle_filled_batch))
        
        # 批量绘制圆形轮廓
        if self._circle_outline_batch:
            for x, y, radius, color, thickness in self._circle_outline_batch:
                arcade.draw_circle_outline(x, y, radius, color, max(1, int(thickness)))
            log_draw_call(len(self._circle_outline_batch))
        
        # 批量绘制线条
        if self._line_batch:
            for x1, y1, x2, y2, color, thickness in self._line_batch:
                arcade.draw_line(x1, y1, x2, y2, color, max(1, int(thickness)))
            log_draw_call(len(self._line_batch))
    
    def _collect_flash_commands(self, effect: FlashEffect) -> None:
        """收集闪光效果命令 - 简化版"""
        alpha = int(255 * (1.0 - effect.progress) * effect.intensity)
        if alpha <= 0:
            return
        
        # 简化为单层发光，减少绘制调用
        r = effect.radius * 1.3
        a = max(0, min(255, alpha - 50))
        color = (*effect.color, a)
        self._circle_filled_batch.append((effect.x, effect.y, r, color))
    
    def _collect_ripple_commands(self, effect: RippleEffect) -> None:
        """收集波纹效果命令"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        color = (*effect.color, alpha)
        thickness = max(1, effect.thickness * (1.0 - effect.progress))
        self._circle_outline_batch.append((effect.x, effect.y, effect.radius, color, thickness))
    
    def _collect_explosion_commands(self, effect: ExplosionEffect) -> None:
        """收集爆炸效果命令 - 简化版"""
        alpha = int(255 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为单层圆环，减少绘制调用
        r = effect.max_radius * effect.progress
        a = int(alpha * (1.0 - effect.progress))
        color = (*effect.color, a)
        self._circle_outline_batch.append((effect.x, effect.y, r, color, 3))
        
        # 中心闪光（仅在早期）
        if effect.progress < 0.3:
            flash_alpha = int(255 * (1.0 - effect.progress / 0.3))
            flash_color = (255, 255, 200, flash_alpha)
            self._circle_filled_batch.append((effect.x, effect.y, effect.radius * 0.5, flash_color))
    
    def _collect_frost_commands(self, effect: FrostEffect) -> None:
        """收集冰霜效果命令 - 简化版"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为圆形轮廓，减少线条绘制
        color = (200, 230, 255, alpha)
        self._circle_outline_batch.append((effect.x, effect.y, effect.radius, color, 2))
        
        # 中心圆
        center_color = (220, 240, 255, alpha)
        self._circle_filled_batch.append((effect.x, effect.y, effect.radius * 0.2, center_color))
    
    def _collect_shockwave_commands(self, effect: ShockwaveEffect) -> None:
        """收集冲击波效果命令 - 简化版"""
        alpha = int(180 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为单层波
        wave_progress = effect.progress
        if wave_progress < 1.0:
            r = effect.max_radius * wave_progress
            a = int(alpha * (1.0 - wave_progress))
            color = (*effect.color, a)
            self._circle_outline_batch.append((effect.x, effect.y, r, color, 4))
    
    def _collect_hit_spark_commands(self, effect: HitSparkEffect) -> None:
        """收集击中火花效果命令 - 简化版"""
        alpha = int(255 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        length = effect.length * (1.0 - effect.progress * 0.5)
        color = (*effect.color, alpha)
        
        # 减少火花数量，只绘制主要方向
        for i in range(effect.spark_count // 2):  # 减少一半
            angle = math.radians(i * (720 / effect.spark_count) + effect.progress * 180)
            
            x1 = effect.x
            y1 = effect.y
            x2 = effect.x + math.cos(angle) * length
            y2 = effect.y + math.sin(angle) * length
            
            self._line_batch.append((x1, y1, x2, y2, color, 2))
    
    def _collect_planting_ring_commands(self, effect: PlantingRingEffect) -> None:
        """收集种植魔法圈效果命令 - 简化版"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为单层圆环
        color = (*effect.color, alpha)
        self._circle_outline_batch.append((effect.x, effect.y, effect.radius, color, 3))
    
    def _collect_portal_commands(self, effect: PortalEffect) -> None:
        """收集传送门效果命令 - 简化版"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为单层圆环
        color = (*effect.color, alpha)
        self._circle_outline_batch.append((effect.x, effect.y, effect.radius, color, 2))
        
        # 中心发光
        center_alpha = int(150 * (1.0 - effect.progress))
        center_color = (*effect.color, center_alpha)
        self._circle_filled_batch.append((effect.x, effect.y, effect.radius * 0.3, center_color))
    
    def _collect_glow_commands(self, effect: GlowEffect) -> None:
        """收集发光效果命令 - 简化版"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 简化为单层光晕
        color = (*effect.color, alpha)
        self._circle_filled_batch.append((effect.x, effect.y, effect.radius, color))
    
    # === 工厂方法（继承自原系统）===
    
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
                        spark_count: int = 6,
                        length: float = 20.0,
                        color: Tuple[int, int, int] = (255, 255, 100),
                        duration: float = 0.3) -> HitSparkEffect:
        """创建击中火花效果"""
        effect = HitSparkEffect(
            x=x, y=y,
            effect_type=EffectType.HIT_SPARK,
            life=duration, max_life=duration,
            spark_count=spark_count, length=length, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_planting_ring(self, x: float, y: float,
                            max_radius: float = 60.0,
                            color: Tuple[int, int, int] = (100, 200, 100),
                            duration: float = 0.5) -> PlantingRingEffect:
        """创建种植魔法圈效果"""
        effect = PlantingRingEffect(
            x=x, y=y,
            effect_type=EffectType.PLANTING_RING,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_planting_visual(self, x: float, y: float) -> PlantingRingEffect:
        """创建种植视觉效果（兼容方法）"""
        return self.create_planting_ring(x, y)
    
    def create_portal(self, x: float, y: float,
                     max_radius: float = 50.0,
                     color: Tuple[int, int, int] = (150, 100, 200),
                     duration: float = 1.0) -> PortalEffect:
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
