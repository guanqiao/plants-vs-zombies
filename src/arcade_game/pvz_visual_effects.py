"""
PVZ风格视觉特效系统
包含原版植物大战僵尸风格的各种特效
"""

import math
import random
from typing import List, Tuple, Dict
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade

from .visual_effects_optimized import OptimizedVisualEffectsSystem
from .visual_effects import EffectType


class PvzEffectType(Enum):
    """PVZ特有效果类型"""
    SUN_SPARKLE = auto()        # 阳光闪烁
    ICE_TRAIL = auto()          # 冰霜轨迹
    FREEZE_CRACK = auto()       # 冰冻破裂
    CHERRY_BLAST = auto()       # 樱桃爆炸
    POTATO_MINE_BLAST = auto()  # 土豆雷爆炸
    PLANTING_SMOKE = auto()     # 种植烟雾
    DAMAGE_POP = auto()         # 伤害弹出


@dataclass
class PvzVisualEffect:
    """PVZ视觉特效基类"""
    x: float
    y: float
    effect_type: PvzEffectType
    life: float
    max_life: float
    
    @property
    def progress(self) -> float:
        """获取生命周期进度 (0.0-1.0)"""
        if self.max_life <= 0:
            return 1.0
        return (self.max_life - self.life) / self.max_life
    
    @property
    def is_alive(self) -> bool:
        """判断特效是否存活"""
        return self.life > 0
    
    def update(self, dt: float):
        """更新特效"""
        self.life = max(0, self.life - dt)


@dataclass
class SunSparkleEffect(PvzVisualEffect):
    """阳光闪烁效果"""
    scale: float = 1.0
    color: Tuple[int, int, int] = (255, 255, 0)
    sparkle_count: int = 8


@dataclass
class IceTrailEffect(PvzVisualEffect):
    """冰霜轨迹效果"""
    radius: float = 30.0
    color: Tuple[int, int, int] = (135, 206, 250)


@dataclass
class FreezeCrackEffect(PvzVisualEffect):
    """冰冻破裂效果"""
    radius: float = 20.0
    crack_count: int = 6


@dataclass
class CherryBlastEffect(PvzVisualEffect):
    """樱桃爆炸效果"""
    max_radius: float = 100.0
    color: Tuple[int, int, int] = (255, 50, 50)


@dataclass
class PotatoMineBlastEffect(PvzVisualEffect):
    """土豆雷爆炸效果"""
    max_radius: float = 80.0
    color: Tuple[int, int, int] = (160, 82, 45)


@dataclass
class PlantingSmokeEffect(PvzVisualEffect):
    """种植烟雾效果"""
    particle_count: int = 12
    particles: List[Tuple[float, float, float, float, float]] = field(default_factory=list)  # x, y, vx, vy, life
    
    def __post_init__(self):
        """初始化烟雾粒子"""
        for _ in range(self.particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 60)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            particle_life = random.uniform(0.5, 1.0)
            self.particles.append((offset_x, offset_y, vx, vy, particle_life))


@dataclass
class DamagePopEffect(PvzVisualEffect):
    """伤害弹出效果"""
    damage: int = 0
    color: Tuple[int, int, int] = (255, 255, 255)
    float_speed: float = 50.0
    initial_y_offset: float = 0.0
    
    def __post_init__(self):
        """初始化初始Y偏移"""
        self.initial_y_offset = 0.0


class PvzVisualEffectsSystem(OptimizedVisualEffectsSystem):
    """
    PVZ风格视觉特效系统
    扩展优化版视觉特效系统，添加PVZ风格特效
    """
    
    def __init__(self):
        super().__init__()
        self.pvz_effects: List[PvzVisualEffect] = []
        
        # 阳光闪烁效果批次
        self._sun_sparkle_batch: List[Tuple[float, float, float, Tuple[int, ...]]] = []
        # 烟雾粒子批次
        self._smoke_particle_batch: List[Tuple[float, float, float, Tuple[int, ...]]] = []
        # 裂缝批次
        self._crack_batch: List[Tuple[float, float, float, float, Tuple[int, ...]]] = []
    
    def update(self, dt: float) -> None:
        """更新所有特效"""
        # 更新原有特效
        super().update(dt)
        
        # 更新PVZ特效
        for effect in self.pvz_effects:
            effect.update(dt)
            
            # 更新烟雾粒子
            if isinstance(effect, PlantingSmokeEffect):
                for i, (ox, oy, vx, vy, plife) in enumerate(effect.particles):
                    new_plife = max(0, plife - dt)
                    effect.particles[i] = (ox, oy, vx, vy, new_plife)
        
        # 移除已结束的PVZ特效
        self.pvz_effects = [e for e in self.pvz_effects if e.is_alive and 
                           (not isinstance(e, PlantingSmokeEffect) or 
                            any(p[4] > 0 for p in e.particles))]
    
    def render(self) -> None:
        """渲染所有特效"""
        # 清空PVZ批次
        self._sun_sparkle_batch.clear()
        self._smoke_particle_batch.clear()
        self._crack_batch.clear()
        
        # 清空父类批次缓冲区
        self._circle_filled_batch.clear()
        self._circle_outline_batch.clear()
        self._line_batch.clear()
        
        # 收集PVZ特效命令
        for effect in self.pvz_effects:
            self._collect_pvz_effect_commands(effect)
        
        # 执行原有渲染
        super()._execute_batch_draw()
        
        # 执行PVZ特效渲染
        self._execute_pvz_batch_draw()
    
    def _collect_pvz_effect_commands(self, effect: PvzVisualEffect) -> None:
        """收集PVZ特效的绘制命令"""
        if effect.effect_type == PvzEffectType.SUN_SPARKLE:
            self._collect_sun_sparkle_commands(effect)
        elif effect.effect_type == PvzEffectType.ICE_TRAIL:
            self._collect_ice_trail_commands(effect)
        elif effect.effect_type == PvzEffectType.FREEZE_CRACK:
            self._collect_freeze_crack_commands(effect)
        elif effect.effect_type == PvzEffectType.CHERRY_BLAST:
            self._collect_cherry_blast_commands(effect)
        elif effect.effect_type == PvzEffectType.POTATO_MINE_BLAST:
            self._collect_potato_mine_blast_commands(effect)
        elif effect.effect_type == PvzEffectType.PLANTING_SMOKE:
            self._collect_planting_smoke_commands(effect)
        elif effect.effect_type == PvzEffectType.DAMAGE_POP:
            self._collect_damage_pop_commands(effect)
    
    def _collect_sun_sparkle_commands(self, effect: SunSparkleEffect) -> None:
        """收集阳光闪烁效果命令"""
        alpha = int(255 * (1.0 - effect.progress) * 0.8)
        if alpha <= 0:
            return
        
        # 闪烁点
        for i in range(effect.sparkle_count):
            angle = (effect.progress * 360 + i * (360 / effect.sparkle_count)) % 360
            radius = 15 * effect.scale * (1.0 - effect.progress)
            offset_x = math.cos(math.radians(angle)) * radius * 0.5
            offset_y = math.sin(math.radians(angle)) * radius * 0.5
            
            sparkle_alpha = int(alpha * (0.5 + 0.5 * math.sin(effect.progress * 20)))
            sparkle_color = (*effect.color, sparkle_alpha)
            
            self._sun_sparkle_batch.append((effect.x + offset_x, effect.y + offset_y, 
                                          2 * effect.scale, sparkle_color))
    
    def _collect_ice_trail_commands(self, effect: IceTrailEffect) -> None:
        """收集冰霜轨迹效果命令"""
        alpha = int(200 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 冰霜光环
        color = (*effect.color, alpha)
        self._circle_outline_batch.append((effect.x, effect.y, 
                                         effect.radius * (1.0 - effect.progress), 
                                         color, 2))
        
        # 中心亮点
        center_alpha = int(alpha * 0.7)
        center_color = (200, 240, 255, center_alpha)
        self._circle_filled_batch.append((effect.x, effect.y, 
                                        effect.radius * 0.3 * (1.0 - effect.progress), 
                                        center_color))
    
    def _collect_freeze_crack_commands(self, effect: FreezeCrackEffect) -> None:
        """收集冰冻破裂效果命令"""
        alpha = int(255 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 从中心向外辐射的裂缝
        for i in range(effect.crack_count):
            angle = (i * (360 / effect.crack_count) + effect.progress * 180) % 360
            rad = math.radians(angle)
            
            # 裂缝起点（靠近中心）
            start_x = effect.x + math.cos(rad) * effect.radius * 0.3 * effect.progress
            start_y = effect.y + math.sin(rad) * effect.radius * 0.3 * effect.progress
            
            # 裂缝终点（向外延伸）
            end_x = effect.x + math.cos(rad) * effect.radius * min(1.0, effect.progress * 1.5)
            end_y = effect.y + math.sin(rad) * effect.radius * min(1.0, effect.progress * 1.5)
            
            crack_alpha = int(alpha * (1.0 - effect.progress * 0.5))
            crack_color = (200, 230, 255, crack_alpha)
            
            self._line_batch.append((start_x, start_y, end_x, end_y, crack_color, 2))
    
    def _collect_cherry_blast_commands(self, effect: CherryBlastEffect) -> None:
        """收集樱桃爆炸效果命令"""
        progress = effect.progress
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0:
            return
        
        # 爆炸波
        blast_radius = effect.max_radius * progress
        blast_alpha = int(alpha * (1.0 - progress * 0.3))
        blast_color = (*effect.color, blast_alpha)
        self._circle_outline_batch.append((effect.x, effect.y, blast_radius, blast_color, 4))
        
        # 中心火球
        fire_radius = effect.max_radius * 0.3 * (1.0 - progress)
        fire_alpha = int(255 * (1.0 - progress * 0.7))
        fire_color = (255, 100, 0, fire_alpha)
        self._circle_filled_batch.append((effect.x, effect.y, fire_radius, fire_color))
        
        # 爆炸碎片
        if progress < 0.6:
            for i in range(8):
                angle = (i * 45 + progress * 100) % 360
                rad = math.radians(angle)
                frag_distance = blast_radius * 0.7
                frag_x = effect.x + math.cos(rad) * frag_distance
                frag_y = effect.y + math.sin(rad) * frag_distance
                
                frag_alpha = int(200 * (1.0 - progress / 0.6))
                frag_color = (255, 150, 50, frag_alpha)
                self._circle_filled_batch.append((frag_x, frag_y, 3, frag_color))
    
    def _collect_potato_mine_blast_commands(self, effect: PotatoMineBlastEffect) -> None:
        """收集土豆雷爆炸效果命令"""
        progress = effect.progress
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0:
            return
        
        # 爆炸波
        blast_radius = effect.max_radius * progress
        blast_alpha = int(alpha * (1.0 - progress * 0.3))
        blast_color = (*effect.color, blast_alpha)
        self._circle_outline_batch.append((effect.x, effect.y, blast_radius, blast_color, 3))
        
        # 中心冲击
        shock_radius = effect.max_radius * 0.2 * (1.0 - progress)
        shock_alpha = int(200 * (1.0 - progress * 0.8))
        shock_color = (200, 150, 100, shock_alpha)
        self._circle_filled_batch.append((effect.x, effect.y, shock_radius, shock_color))
    
    def _collect_planting_smoke_commands(self, effect: PlantingSmokeEffect) -> None:
        """收集种植烟雾效果命令"""
        for ox, oy, vx, vy, plife in effect.particles:
            if plife <= 0:
                continue
            
            particle_progress = 1.0 - (plife / 1.0)  # 1.0 at start, 0.0 at end
            particle_alpha = int(200 * (plife / 1.0) * 0.7)
            particle_size = 3 * (1.0 - particle_progress * 0.5)
            particle_x = effect.x + ox + vx * (1.0 - plife) * 0.5
            particle_y = effect.y + oy + vy * (1.0 - plife) * 0.5
            
            smoke_color = (200, 200, 200, particle_alpha)
            self._smoke_particle_batch.append((particle_x, particle_y, particle_size, smoke_color))
    
    def _collect_damage_pop_commands(self, effect: DamagePopEffect) -> None:
        """收集伤害弹出效果命令"""
        if effect.progress > 0.8:  # 只在前80%的时间显示
            return
            
        alpha = int(255 * (1.0 - effect.progress))
        if alpha <= 0:
            return
        
        # 计算当前位置（向上飘）
        current_y = effect.y + effect.initial_y_offset + effect.float_speed * effect.progress
        
        # 绘制伤害数字
        # 这里我们只是标记位置，实际文本渲染会在外部处理
        # 但对于特效系统，我们可以创建一个视觉标记
        marker_alpha = int(alpha * 0.6)
        marker_color = (*effect.color, marker_alpha)
        self._circle_filled_batch.append((effect.x, current_y, 8, marker_color))
    
    def _execute_pvz_batch_draw(self) -> None:
        """执行PVZ特效批量绘制"""
        # 绘制阳光闪烁
        for x, y, size, color in self._sun_sparkle_batch:
            arcade.draw_circle_filled(x, y, size, color)
        
        # 绘制烟雾粒子
        for x, y, size, color in self._smoke_particle_batch:
            arcade.draw_circle_filled(x, y, size, color)
        
        # 绘制裂缝
        for x1, y1, x2, y2, color in self._crack_batch:
            arcade.draw_line(x1, y1, x2, y2, color, 2)
    
    # === PVZ特效工厂方法 ===
    
    def create_sun_sparkle(self, x: float, y: float,
                          scale: float = 1.0,
                          color: Tuple[int, int, int] = (255, 255, 0),
                          duration: float = 0.8) -> SunSparkleEffect:
        """创建阳光闪烁效果"""
        effect = SunSparkleEffect(
            x=x, y=y,
            effect_type=PvzEffectType.SUN_SPARKLE,
            life=duration, max_life=duration,
            scale=scale, color=color
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_ice_trail(self, x: float, y: float,
                        radius: float = 30.0,
                        color: Tuple[int, int, int] = (135, 206, 250),
                        duration: float = 0.6) -> IceTrailEffect:
        """创建冰霜轨迹效果"""
        effect = IceTrailEffect(
            x=x, y=y,
            effect_type=PvzEffectType.ICE_TRAIL,
            life=duration, max_life=duration,
            radius=radius, color=color
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_freeze_crack(self, x: float, y: float,
                           radius: float = 20.0,
                           crack_count: int = 6,
                           duration: float = 0.5) -> FreezeCrackEffect:
        """创建冰冻破裂效果"""
        effect = FreezeCrackEffect(
            x=x, y=y,
            effect_type=PvzEffectType.FREEZE_CRACK,
            life=duration, max_life=duration,
            radius=radius, crack_count=crack_count
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_cherry_blast(self, x: float, y: float,
                           max_radius: float = 100.0,
                           color: Tuple[int, int, int] = (255, 50, 50),
                           duration: float = 0.6) -> CherryBlastEffect:
        """创建樱桃爆炸效果"""
        effect = CherryBlastEffect(
            x=x, y=y,
            effect_type=PvzEffectType.CHERRY_BLAST,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_potato_mine_blast(self, x: float, y: float,
                                max_radius: float = 80.0,
                                color: Tuple[int, int, int] = (160, 82, 45),
                                duration: float = 0.5) -> PotatoMineBlastEffect:
        """创建土豆雷爆炸效果"""
        effect = PotatoMineBlastEffect(
            x=x, y=y,
            effect_type=PvzEffectType.POTATO_MINE_BLAST,
            life=duration, max_life=duration,
            max_radius=max_radius, color=color
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_planting_smoke(self, x: float, y: float,
                             particle_count: int = 12,
                             duration: float = 1.0) -> PlantingSmokeEffect:
        """创建种植烟雾效果"""
        effect = PlantingSmokeEffect(
            x=x, y=y,
            effect_type=PvzEffectType.PLANTING_SMOKE,
            life=duration, max_life=duration,
            particle_count=particle_count
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_damage_pop(self, x: float, y: float, damage: int,
                         color: Tuple[int, int, int] = (255, 255, 255),
                         duration: float = 1.0) -> DamagePopEffect:
        """创建伤害弹出效果"""
        effect = DamagePopEffect(
            x=x, y=y,
            effect_type=PvzEffectType.DAMAGE_POP,
            life=duration, max_life=duration,
            damage=damage, color=color
        )
        self.pvz_effects.append(effect)
        return effect
    
    def create_cherry_bomb_visual(self, x: float, y: float) -> List[PvzVisualEffect]:
        """创建完整的樱桃炸弹视觉效果组合"""
        effects = []
        effects.append(self.create_cherry_blast(x, y))
        effects.append(self.create_flash(x, y, radius=80, color=(255, 100, 0), duration=0.4))
        effects.append(self.create_shockwave(x, y, max_radius=120, color=(255, 200, 100), duration=0.5))
        return effects
    
    def create_potato_mine_visual(self, x: float, y: float) -> List[PvzVisualEffect]:
        """创建完整的土豆雷视觉效果组合"""
        effects = []
        effects.append(self.create_potato_mine_blast(x, y))
        effects.append(self.create_flash(x, y, radius=60, color=(200, 150, 100), duration=0.3))
        return effects
    
    def clear(self) -> None:
        """清除所有特效"""
        self.pvz_effects.clear()
        self.effects.clear()