
"""
增强版视觉特效系统 - 新增多种特效

包括：
- 场景过渡效果（淡入淡出）
- 植物种植破土效果
- 僵尸从地下钻出效果
- 僵尸特写效果
- 更多粒子特效
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class EnhancedEffectType(Enum):
    """增强版特效类型"""
    SCENE_TRANSITION = auto()      # 场景过渡
    GROUND_BREAK = auto()          # 破土效果
    ZOMBIE_EMERGE = auto()         # 僵尸钻出效果
    ZOMBIE_CLOSEUP = auto()        # 僵尸特写
    DIRT_SPLATTER = auto()         # 泥土飞溅
    LEAF_FALL = auto()             # 落叶效果
    RAIN_DROP = auto()             # 雨滴效果
    SNOW_FLAKE = auto()            # 雪花效果
    MAGIC_RING = auto()            # 魔法圈


@dataclass
class EnhancedVisualEffect:
    """增强版视觉特效基类"""
    x: float
    y: float
    effect_type: EnhancedEffectType
    life: float
    max_life: float
    is_alive: bool = True
    
    def update(self, dt: float) -&gt; None:
        """更新特效"""
        self.life -= dt
        if self.life &lt;= 0:
            self.is_alive = False
    
    @property
    def progress(self) -&gt; float:
        """获取进度 (0-1)"""
        return 1.0 - (self.life / self.max_life)


@dataclass
class SceneTransitionEffect(EnhancedVisualEffect):
    """场景过渡效果"""
    transition_type: str = "fade_out"  # fade_out, fade_in, cross_fade
    color: Tuple[int, int, int] = (0, 0, 0)
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.SCENE_TRANSITION


@dataclass
class GroundBreakEffect(EnhancedVisualEffect):
    """植物种植破土效果"""
    dirt_count: int = 15
    particles: List = field(default_factory=list)
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.GROUND_BREAK
        self._init_particles()
    
    def _init_particles(self):
        """初始化泥土粒子"""
        for _ in range(self.dirt_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 100,
                'size': random.uniform(3, 8),
                'life': random.uniform(0.3, 0.7),
                'max_life': random.uniform(0.3, 0.7),
            })
    
    def update(self, dt: float) -&gt; None:
        super().update(dt)
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 200 * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] &gt; 0]


@dataclass
class ZombieEmergeEffect(EnhancedVisualEffect):
    """僵尸从地下钻出效果"""
    dirt_count: int = 20
    particles: List = field(default_factory=list)
    shake_intensity: float = 5.0
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.ZOMBIE_EMERGE
        self._init_particles()
    
    def _init_particles(self):
        """初始化泥土粒子"""
        for _ in range(self.dirt_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(80, 200)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 150,
                'size': random.uniform(4, 10),
                'life': random.uniform(0.4, 0.8),
                'max_life': random.uniform(0.4, 0.8),
            })
    
    def update(self, dt: float) -&gt; None:
        super().update(dt)
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 250 * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] &gt; 0]


@dataclass
class ZombieCloseupEffect(EnhancedVisualEffect):
    """僵尸特写效果"""
    zombie_type: str = "normal"
    scale: float = 1.0
    target_scale: float = 2.0
    alpha: float = 0.0
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.ZOMBIE_CLOSEUP
    
    def update(self, dt: float) -&gt; None:
        super().update(dt)
        progress = self.progress
        if progress &lt; 0.3:
            self.scale = 1.0 + (self.target_scale - 1.0) * (progress / 0.3)
            self.alpha = progress / 0.3
        elif progress &gt; 0.7:
            self.scale = self.target_scale - (self.target_scale - 1.0) * ((progress - 0.7) / 0.3)
            self.alpha = 1.0 - ((progress - 0.7) / 0.3)
        else:
            self.scale = self.target_scale
            self.alpha = 1.0


@dataclass
class LeafFallEffect(EnhancedVisualEffect):
    """落叶效果"""
    leaf_count: int = 10
    leaves: List = field(default_factory=list)
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.LEAF_FALL
        self._init_leaves()
    
    def _init_leaves(self):
        """初始化落叶"""
        for _ in range(self.leaf_count):
            self.leaves.append({
                'x': random.uniform(self.x - 100, self.x + 100),
                'y': self.y + random.uniform(-50, 50),
                'vy': random.uniform(30, 80),
                'vx': random.uniform(-20, 20),
                'size': random.uniform(5, 12),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-90, 90),
                'life': random.uniform(1.0, 2.0),
                'max_life': random.uniform(1.0, 2.0),
                'color': random.choice([
                    (34, 139, 34),
                    (50, 205, 50),
                    (107, 142, 35),
                    (85, 107, 47),
                ]),
            })
    
    def update(self, dt: float) -&gt; None:
        super().update(dt)
        for leaf in self.leaves:
            leaf['x'] += leaf['vx'] * dt
            leaf['y'] += leaf['vy'] * dt
            leaf['rotation'] += leaf['rotation_speed'] * dt
            leaf['life'] -= dt
        self.leaves = [l for l in self.leaves if l['life'] &gt; 0]


@dataclass
class MagicRingEffect(EnhancedVisualEffect):
    """魔法圈效果"""
    ring_count: int = 3
    max_radius: float = 80.0
    color: Tuple[int, int, int] = (100, 200, 100)
    rotation: float = 0.0
    rotation_speed: float = 90.0
    
    def __post_init__(self):
        self.effect_type = EnhancedEffectType.MAGIC_RING
    
    def update(self, dt: float) -&gt; None:
        super().update(dt)
        self.rotation += self.rotation_speed * dt


class EnhancedVisualEffectsSystem:
    """
    增强版视觉特效系统
    
    管理和渲染所有增强版视觉特效
    """
    
    def __init__(self):
        self.effects: List[EnhancedVisualEffect] = []
    
    def update(self, dt: float) -&gt; None:
        """更新所有特效"""
        for effect in self.effects:
            effect.update(dt)
        
        # 移除已结束的特效
        self.effects = [e for e in self.effects if e.is_alive]
    
    def render(self) -&gt; None:
        """渲染所有特效"""
        for effect in self.effects:
            self._render_effect(effect)
    
    def _render_effect(self, effect: EnhancedVisualEffect) -&gt; None:
        """渲染单个特效"""
        if effect.effect_type == EnhancedEffectType.SCENE_TRANSITION:
            self._render_scene_transition(effect)
        elif effect.effect_type == EnhancedEffectType.GROUND_BREAK:
            self._render_ground_break(effect)
        elif effect.effect_type == EnhancedEffectType.ZOMBIE_EMERGE:
            self._render_zombie_emerge(effect)
        elif effect.effect_type == EnhancedEffectType.ZOMBIE_CLOSEUP:
            self._render_zombie_closeup(effect)
        elif effect.effect_type == EnhancedEffectType.LEAF_FALL:
            self._render_leaf_fall(effect)
        elif effect.effect_type == EnhancedEffectType.MAGIC_RING:
            self._render_magic_ring(effect)
    
    def _render_scene_transition(self, effect: SceneTransitionEffect) -&gt; None:
        """渲染场景过渡效果"""
        alpha = int(255 * effect.progress)
        if effect.transition_type == "fade_in":
            alpha = 255 - alpha
        
        arcade.draw_rect_filled(arcade.XYWH(effect.x, effect.y, 2000, 2000), (*effect.color, alpha)
        )
    
    def _render_ground_break(self, effect: GroundBreakEffect) -&gt; None:
        """渲染破土效果"""
        # 渲染泥土粒子
        for p in effect.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            arcade.draw_circle_filled(
                p['x'], p['y'],
                p['size'],
                (101, 67, 33, alpha)
            )
        
        # 渲染地面裂纹
        if effect.progress &lt; 0.5:
            crack_alpha = int(200 * (1 - effect.progress * 2))
            for i in range(5):
                angle = math.radians(i * 72)
                length = 20 * effect.progress * 2
                x1 = effect.x
                y1 = effect.y
                x2 = effect.x + math.cos(angle) * length
                y2 = effect.y + math.sin(angle) * length
                arcade.draw_line(x1, y1, x2, y2, (80, 50, 30, crack_alpha), 2)
    
    def _render_zombie_emerge(self, effect: ZombieEmergeEffect) -&gt; None:
        """渲染僵尸钻出效果"""
        # 渲染泥土粒子
        for p in effect.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            arcade.draw_circle_filled(
                p['x'], p['y'],
                p['size'],
                (101, 67, 33, alpha)
            )
        
        # 渲染地面震动效果（视觉指示）
        if effect.progress &lt; 0.3:
            shake_alpha = int(150 * (1 - effect.progress / 0.3))
            arcade.draw_circle_outline(
                effect.x, effect.y,
                30 + effect.progress * 50,
                (150, 100, 50, shake_alpha),
                3
            )
    
    def _render_zombie_closeup(self, effect: ZombieCloseupEffect) -&gt; None:
        """渲染僵尸特写效果（占位实现）"""
        alpha = int(200 * effect.alpha)
        # 这里可以渲染放大的僵尸精灵
        # 暂时渲染一个占位框
        size = 100 * effect.scale
        arcade.draw_rect_outline(arcade.XYWH(effect.x, effect.y, size, size * 1.5), (255, 255, 255, alpha),
            3
        )
    
    def _render_leaf_fall(self, effect: LeafFallEffect) -&gt; None:
        """渲染落叶效果"""
        for leaf in effect.leaves:
            alpha = int(255 * (leaf['life'] / leaf['max_life']))
            
            # 绘制叶子（简化为菱形）
            size = leaf['size']
            angle_rad = math.radians(leaf['rotation'])
            
            # 旋转叶子
            points = []
            for i in range(4):
                a = angle_rad + math.radians(i * 90)
                s = size if i % 2 == 0 else size * 0.5
                points.append((
                    leaf['x'] + math.cos(a) * s,
                    leaf['y'] + math.sin(a) * s
                ))
            
            arcade.draw_polygon_filled(points, (*leaf['color'], alpha))
    
    def _render_magic_ring(self, effect: MagicRingEffect) -&gt; None:
        """渲染魔法圈效果"""
        alpha = int(200 * (1 - effect.progress))
        
        for i in range(effect.ring_count):
            ring_progress = max(0, effect.progress - i * 0.2)
            if ring_progress &lt; 1.0:
                radius = effect.max_radius * ring_progress
                ring_alpha = int(alpha * (1 - ring_progress))
                
                # 绘制魔法圈
                arcade.draw_circle_outline(
                    effect.x, effect.y,
                    radius,
                    (*effect.color, ring_alpha),
                    4 - i
                )
                
                # 绘制符文装饰
                if i == 0:
                    rune_count = 8
                    for j in range(rune_count):
                        rune_angle = math.radians(effect.rotation + j * (360 / rune_count))
                        rune_x = effect.x + math.cos(rune_angle) * radius
                        rune_y = effect.y + math.sin(rune_angle) * radius
                        arcade.draw_circle_filled(rune_x, rune_y, 4, (*effect.color, ring_alpha))
    
    # === 创建特效的工厂方法 ===
    
    def create_scene_transition(self, x: float, y: float,
                               transition_type: str = "fade_out",
                               color: Tuple[int, int, int] = (0, 0, 0),
                               duration: float = 1.0) -&gt; SceneTransitionEffect:
        """创建场景过渡效果"""
        effect = SceneTransitionEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.SCENE_TRANSITION,
            life=duration, max_life=duration,
            transition_type=transition_type,
            color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_ground_break(self, x: float, y: float,
                            dirt_count: int = 15,
                            duration: float = 0.8) -&gt; GroundBreakEffect:
        """创建植物种植破土效果"""
        effect = GroundBreakEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.GROUND_BREAK,
            life=duration, max_life=duration,
            dirt_count=dirt_count
        )
        self.effects.append(effect)
        return effect
    
    def create_zombie_emerge(self, x: float, y: float,
                            dirt_count: int = 20,
                            duration: float = 1.0) -&gt; ZombieEmergeEffect:
        """创建僵尸从地下钻出效果"""
        effect = ZombieEmergeEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.ZOMBIE_EMERGE,
            life=duration, max_life=duration,
            dirt_count=dirt_count
        )
        self.effects.append(effect)
        return effect
    
    def create_zombie_closeup(self, x: float, y: float,
                             zombie_type: str = "normal",
                             duration: float = 1.5) -&gt; ZombieCloseupEffect:
        """创建僵尸特写效果"""
        effect = ZombieCloseupEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.ZOMBIE_CLOSEUP,
            life=duration, max_life=duration,
            zombie_type=zombie_type
        )
        self.effects.append(effect)
        return effect
    
    def create_leaf_fall(self, x: float, y: float,
                        leaf_count: int = 10,
                        duration: float = 2.0) -&gt; LeafFallEffect:
        """创建落叶效果"""
        effect = LeafFallEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.LEAF_FALL,
            life=duration, max_life=duration,
            leaf_count=leaf_count
        )
        self.effects.append(effect)
        return effect
    
    def create_magic_ring(self, x: float, y: float,
                         max_radius: float = 80.0,
                         color: Tuple[int, int, int] = (100, 200, 100),
                         duration: float = 0.8) -&gt; MagicRingEffect:
        """创建魔法圈效果"""
        effect = MagicRingEffect(
            x=x, y=y,
            effect_type=EnhancedEffectType.MAGIC_RING,
            life=duration, max_life=duration,
            max_radius=max_radius,
            color=color
        )
        self.effects.append(effect)
        return effect
    
    def create_planting_with_ground_break(self, x: float, y: float) -&gt; None:
        """创建带破土效果的种植视觉效果组合"""
        self.create_ground_break(x, y, dirt_count=15, duration=0.8)
        self.create_magic_ring(x, y, max_radius=60, color=(100, 200, 100), duration=0.6)
        self.create_leaf_fall(x, y, leaf_count=8, duration=1.5)
    
    def clear(self) -&gt; None:
        """清除所有特效"""
        self.effects.clear()
    
    def get_active_count(self) -&gt; int:
        """获取活动特效数量"""
        return len(self.effects)
