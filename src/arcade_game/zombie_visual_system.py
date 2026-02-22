"""
僵尸视觉效果系统 - 处理僵尸的视觉反馈

包括：
- 受击闪烁效果
- 死亡动画
- 移动动画
- 特殊僵尸效果
- 部位脱落效果
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class DeathType(Enum):
    """死亡类型"""
    NORMAL = auto()      # 普通死亡（倒地）
    EXPLOSION = auto()   # 爆炸死亡（樱桃炸弹）
    FROZEN = auto()      # 冰冻死亡
    ELECTRIC = auto()    # 电击死亡
    BURNED = auto()      # 烧焦死亡


@dataclass
class ZombieVisualState:
    """僵尸视觉状态"""
    hit_flash: float = 0.0
    death_progress: float = 0.0
    is_dying: bool = False
    shake_offset_x: float = 0.0
    shake_offset_y: float = 0.0
    scale: float = 1.0
    alpha: int = 255
    color_tint: Tuple[int, int, int] = (255, 255, 255)
    
    # 增强的受击效果
    hit_pulse: float = 0.0  # 受击脉冲（放大效果）
    blood_particles: List[dict] = field(default_factory=list)
    
    # 部位脱落状态
    has_left_arm: bool = True
    has_right_arm: bool = True
    has_head: bool = True
    
    # 护甲状态
    armor_broken: bool = False
    armor_flying: bool = False
    armor_offset_x: float = 0.0
    armor_offset_y: float = 0.0
    armor_velocity_x: float = 0.0
    armor_velocity_y: float = 0.0
    armor_rotation: float = 0.0
    
    def trigger_hit(self, damage: int = 10) -> None:
        """触发受击效果"""
        self.hit_flash = 1.0
        self.hit_pulse = 1.0
        self.shake_offset_x = random.uniform(-4, 4)
        self.shake_offset_y = random.uniform(-3, 3)
        
        # 根据伤害生成血液粒子
        num_particles = min(5, max(1, damage // 10))
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi)  # 上半圆
            speed = random.uniform(30, 80)
            self.blood_particles.append({
                'x': 0, 'y': 0,  # 相对位置
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(2, 5),
                'alpha': 255,
                'life': 0.5,
            })
    
    def trigger_armor_break(self) -> None:
        """触发护甲破碎效果"""
        self.armor_broken = True
        self.armor_flying = True
        self.armor_velocity_x = random.uniform(50, 150)
        self.armor_velocity_y = random.uniform(100, 200)
        self.armor_rotation = random.uniform(-30, 30)
    
    def start_death(self, death_type: DeathType = DeathType.NORMAL) -> None:
        """开始死亡动画"""
        self.is_dying = True
        self.death_progress = 0.0
        self.death_type = death_type
    
    def update(self, dt: float) -> None:
        """更新状态"""
        # 更新受击闪烁
        if self.hit_flash > 0:
            self.hit_flash *= 0.88
            if self.hit_flash < 0.01:
                self.hit_flash = 0.0
        
        # 更新受击脉冲
        if self.hit_pulse > 0:
            self.hit_pulse -= dt * 3
            if self.hit_pulse < 0:
                self.hit_pulse = 0
        
        # 更新震动
        if abs(self.shake_offset_x) > 0.1 or abs(self.shake_offset_y) > 0.1:
            self.shake_offset_x *= 0.85
            self.shake_offset_y *= 0.85
        else:
            self.shake_offset_x = 0.0
            self.shake_offset_y = 0.0
        
        # 更新血液粒子
        for p in self.blood_particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] -= 200 * dt  # 重力
            p['life'] -= dt
            p['alpha'] = int(255 * (p['life'] / 0.5))
            if p['life'] <= 0:
                self.blood_particles.remove(p)
        
        # 更新护甲飞行动画
        if self.armor_flying:
            self.armor_offset_x += self.armor_velocity_x * dt
            self.armor_offset_y += self.armor_velocity_y * dt
            self.armor_velocity_y -= 300 * dt  # 重力
            self.armor_rotation += self.armor_velocity_x * 0.1 * dt
            
            # 地面碰撞
            if self.armor_offset_y < -30:
                self.armor_offset_y = -30
                self.armor_velocity_y *= -0.4
                self.armor_velocity_x *= 0.7
                if abs(self.armor_velocity_y) < 10:
                    self.armor_flying = False
        
        # 更新死亡动画
        if self.is_dying:
            self.death_progress += dt * 1.2
            if self.death_progress >= 1.0:
                self.death_progress = 1.0
            
            # 死亡效果：缩小、淡出
            self.scale = 1.0 - self.death_progress * 0.3
            self.alpha = int(255 * (1.0 - self.death_progress))


@dataclass
class DeathAnimation:
    """死亡动画"""
    x: float
    y: float
    zombie_type: str
    death_type: DeathType = DeathType.NORMAL
    progress: float = 0.0
    duration: float = 1.0
    particles: List[dict] = field(default_factory=list)
    is_complete: bool = False
    
    def __post_init__(self):
        """初始化粒子"""
        self._init_particles()
    
    def _init_particles(self):
        """根据死亡类型初始化粒子"""
        if self.death_type == DeathType.EXPLOSION:
            # 爆炸效果 - 更多碎片
            for _ in range(25):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(80, 200)
                self.particles.append({
                    'x': self.x, 'y': self.y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.uniform(4, 12),
                    'alpha': 255,
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-360, 360),
                    'color': random.choice([
                        (100, 100, 100),  # 灰色
                        (139, 69, 19),    # 棕色
                        (128, 128, 128),  # 灰色
                    ]),
                    'type': 'debris'
                })
        elif self.death_type == DeathType.FROZEN:
            # 冰冻效果 - 冰晶
            for _ in range(20):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(30, 100)
                self.particles.append({
                    'x': self.x, 'y': self.y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.uniform(3, 8),
                    'alpha': 255,
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-180, 180),
                    'color': (200, 230, 255),  # 冰蓝色
                    'type': 'ice'
                })
        elif self.death_type == DeathType.ELECTRIC:
            # 电击效果 - 电火花
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(50, 150)
                self.particles.append({
                    'x': self.x, 'y': self.y,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': random.uniform(2, 6),
                    'alpha': 255,
                    'color': (255, 255, 100),  # 黄色电光
                    'type': 'spark'
                })
        elif self.death_type == DeathType.BURNED:
            # 烧焦效果 - 灰烬
            for _ in range(15):
                self.particles.append({
                    'x': self.x + random.uniform(-20, 20),
                    'y': self.y + random.uniform(-30, 30),
                    'vx': random.uniform(-20, 20),
                    'vy': random.uniform(20, 60),  # 向上飘
                    'size': random.uniform(3, 8),
                    'alpha': 255,
                    'color': (50, 50, 50),  # 黑色灰烬
                    'type': 'ash'
                })
        else:
            # 普通死亡
            for _ in range(15):
                self.particles.append({
                    'x': self.x + random.uniform(-20, 20),
                    'y': self.y + random.uniform(-30, 30),
                    'vx': random.uniform(-50, 50),
                    'vy': random.uniform(-80, 20),
                    'size': random.uniform(3, 8),
                    'alpha': 255,
                    'rotation': random.uniform(0, 360),
                    'rotation_speed': random.uniform(-180, 180),
                    'color': (100, 100, 100),
                    'type': 'normal'
                })
    
    def update(self, dt: float) -> None:
        """更新动画"""
        self.progress += dt / self.duration
        
        if self.progress >= 1.0:
            self.is_complete = True
            return
        
        # 更新粒子
        for p in self.particles:
            if p['type'] == 'ash':
                # 灰烬向上飘
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['size'] *= 0.98
            elif p['type'] == 'spark':
                # 电火花快速消失
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['alpha'] = int(255 * (1.0 - self.progress * 2))
            else:
                # 普通粒子受重力
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt
                p['vy'] -= 150 * dt  # 重力
                p['alpha'] = int(255 * (1.0 - self.progress))
                if 'rotation' in p:
                    p['rotation'] += p.get('rotation_speed', 0) * dt
                p['size'] *= 0.99
    
    def render(self) -> None:
        """渲染动画"""
        if self.is_complete:
            return
        
        # 绘制粒子
        for p in self.particles:
            if p['alpha'] <= 0:
                continue
            
            color = (*p['color'][:3], p['alpha'])
            
            if p['type'] == 'spark':
                # 电火花绘制为十字
                size = p['size']
                arcade.draw_line(
                    p['x'] - size, p['y'], p['x'] + size, p['y'],
                    color, 2
                )
                arcade.draw_line(
                    p['x'], p['y'] - size, p['x'], p['y'] + size,
                    color, 2
                )
            elif p['type'] == 'ice':
                # 冰晶绘制为菱形
                size = p['size']
                arcade.draw_polygon_filled([
                    (p['x'], p['y'] + size),
                    (p['x'] + size * 0.7, p['y']),
                    (p['x'], p['y'] - size),
                    (p['x'] - size * 0.7, p['y']),
                ], color)
            else:
                # 其他粒子绘制为圆形
                arcade.draw_circle_filled(p['x'], p['y'], p['size'], color)
        
        # 绘制死亡后的僵尸轮廓（根据死亡类型）
        alpha = int(200 * (1.0 - self.progress))
        if alpha > 0:
            if self.death_type == DeathType.FROZEN:
                # 冰冻死亡 - 冰雕效果
                color = (200, 230, 255, alpha)
            elif self.death_type == DeathType.BURNED:
                # 烧焦 - 黑色轮廓
                color = (30, 30, 30, alpha)
            else:
                color = (80, 80, 80, alpha)
            
            # 绘制简化轮廓
            arcade.draw_ellipse_filled(
                self.x, self.y,
                30 * (1.0 - self.progress * 0.5),
                50 * (1.0 - self.progress * 0.5),
                color
            )


class ZombieVisualSystem:
    """
    僵尸视觉效果系统
    
    管理所有僵尸的视觉反馈效果
    """
    
    def __init__(self):
        self.zombie_states: Dict[int, ZombieVisualState] = {}
        self.death_animations: List[DeathAnimation] = []
        self._time = 0.0
    
    def update(self, dt: float) -> None:
        """更新所有状态"""
        self._time += dt
        
        # 更新僵尸状态
        for state in self.zombie_states.values():
            state.update(dt)
        
        # 更新死亡动画
        for anim in self.death_animations:
            anim.update(dt)
        
        # 移除完成的动画
        self.death_animations = [a for a in self.death_animations if not a.is_complete]
    
    def render(self) -> None:
        """渲染死亡动画"""
        for anim in self.death_animations:
            anim.render()
    
    def get_or_create_state(self, zombie_id: int) -> ZombieVisualState:
        """获取或创建僵尸状态"""
        if zombie_id not in self.zombie_states:
            self.zombie_states[zombie_id] = ZombieVisualState()
        return self.zombie_states[zombie_id]
    
    def remove_state(self, zombie_id: int) -> None:
        """移除僵尸状态"""
        if zombie_id in self.zombie_states:
            del self.zombie_states[zombie_id]
    
    def trigger_hit(self, zombie_id: int, damage: int = 10) -> None:
        """触发僵尸受击效果"""
        state = self.get_or_create_state(zombie_id)
        state.trigger_hit(damage)
    
    def trigger_armor_break(self, zombie_id: int) -> None:
        """触发护甲破碎效果"""
        state = self.get_or_create_state(zombie_id)
        state.trigger_armor_break()
    
    def detach_part(self, zombie_id: int, part: str) -> None:
        """
        使僵尸部位脱落
        
        Args:
            zombie_id: 僵尸实体ID
            part: 部位名称 ('head', 'left_arm', 'right_arm')
        """
        state = self.get_or_create_state(zombie_id)
        if part == 'head':
            state.has_head = False
        elif part == 'left_arm':
            state.has_left_arm = False
        elif part == 'right_arm':
            state.has_right_arm = False
    
    def start_death_animation(self, zombie_id: int, x: float, y: float,
                             zombie_type: str = 'normal',
                             death_type: DeathType = DeathType.NORMAL) -> None:
        """开始死亡动画"""
        # 创建死亡动画
        anim = DeathAnimation(x=x, y=y, zombie_type=zombie_type, death_type=death_type)
        self.death_animations.append(anim)
        
        # 标记状态
        if zombie_id in self.zombie_states:
            self.zombie_states[zombie_id].start_death(death_type)
    
    def get_render_offset(self, zombie_id: int) -> Tuple[float, float]:
        """获取渲染偏移"""
        if zombie_id in self.zombie_states:
            state = self.zombie_states[zombie_id]
            return (state.shake_offset_x, state.shake_offset_y)
        return (0.0, 0.0)
    
    def get_hit_flash_intensity(self, zombie_id: int) -> float:
        """获取受击闪烁强度"""
        if zombie_id in self.zombie_states:
            return self.zombie_states[zombie_id].hit_flash
        return 0.0
    
    def get_hit_pulse_scale(self, zombie_id: int) -> float:
        """获取受击脉冲缩放"""
        if zombie_id in self.zombie_states:
            pulse = self.zombie_states[zombie_id].hit_pulse
            # 脉冲效果：先放大后缩小
            if pulse > 0.5:
                return 1.0 + (pulse - 0.5) * 0.2
            else:
                return 1.0 - (0.5 - pulse) * 0.1
        return 1.0
    
    def apply_hit_flash_to_color(self, zombie_id: int, 
                                  base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """将受击闪烁应用到颜色"""
        flash = self.get_hit_flash_intensity(zombie_id)
        if flash > 0:
            # 向白色混合
            return tuple(int(c + (255 - c) * flash) for c in base_color)
        return base_color
    
    def render_blood_particles(self, zombie_id: int, x: float, y: float) -> None:
        """渲染血液粒子"""
        if zombie_id not in self.zombie_states:
            return
        
        state = self.zombie_states[zombie_id]
        for p in state.blood_particles:
            if p['alpha'] > 0:
                color = (180, 30, 30, p['alpha'])  # 血红色
                arcade.draw_circle_filled(
                    x + p['x'], y + p['y'],
                    p['size'], color
                )
    
    def render_flying_armor(self, zombie_id: int, x: float, y: float,
                           armor_type: str = 'cone') -> None:
        """渲染飞出的护甲"""
        if zombie_id not in self.zombie_states:
            return
        
        state = self.zombie_states[zombie_id]
        if not state.armor_flying and not state.armor_broken:
            return
        
        # 根据护甲类型选择颜色
        if armor_type == 'cone':
            color = (255, 140, 0)  # 橙色路障
        elif armor_type == 'bucket':
            color = (169, 169, 169)  # 灰色铁桶
        elif armor_type == 'football':
            color = (139, 69, 19)  # 棕色橄榄球
        else:
            color = (128, 128, 128)
        
        # 绘制飞出的护甲
        armor_x = x + state.armor_offset_x
        armor_y = y + state.armor_offset_y
        
        # 简化绘制为椭圆
        arcade.draw_ellipse_filled(
            armor_x, armor_y,
            25, 30,
            color
        )
    
    def clear(self) -> None:
        """清除所有状态"""
        self.zombie_states.clear()
        self.death_animations.clear()
    
    def get_active_death_count(self) -> int:
        """获取活动死亡动画数量"""
        return len(self.death_animations)
