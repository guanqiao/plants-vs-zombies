"""
僵尸视觉效果系统 - 处理僵尸的视觉反馈

包括：
- 受击闪烁效果
- 死亡动画
- 移动动画
- 特殊僵尸效果
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import arcade


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
    
    def trigger_hit(self) -> None:
        """触发受击效果"""
        self.hit_flash = 1.0
        self.shake_offset_x = 5.0
    
    def start_death(self) -> None:
        """开始死亡动画"""
        self.is_dying = True
        self.death_progress = 0.0
    
    def update(self, dt: float) -> None:
        """更新状态"""
        # 更新受击闪烁
        if self.hit_flash > 0:
            self.hit_flash *= 0.85
            if self.hit_flash < 0.01:
                self.hit_flash = 0.0
        
        # 更新震动
        self.shake_offset_x *= 0.8
        self.shake_offset_y *= 0.8
        if abs(self.shake_offset_x) < 0.1:
            self.shake_offset_x = 0.0
        if abs(self.shake_offset_y) < 0.1:
            self.shake_offset_y = 0.0
        
        # 更新死亡动画
        if self.is_dying:
            self.death_progress += dt * 1.5
            if self.death_progress >= 1.0:
                self.death_progress = 1.0
            
            # 死亡效果：缩小、淡出
            self.scale = 1.0 - self.death_progress * 0.5
            self.alpha = int(255 * (1.0 - self.death_progress))


@dataclass
class DeathAnimation:
    """死亡动画"""
    x: float
    y: float
    zombie_type: str
    progress: float = 0.0
    duration: float = 0.8
    particles: List[dict] = field(default_factory=list)
    is_complete: bool = False
    
    def __post_init__(self):
        """初始化粒子"""
        import random
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
            })
    
    def update(self, dt: float) -> None:
        """更新动画"""
        self.progress += dt / self.duration
        
        if self.progress >= 1.0:
            self.is_complete = True
            return
        
        # 更新粒子
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] -= 100 * dt  # 重力
            p['alpha'] = int(255 * (1.0 - self.progress))
            p['rotation'] += p['rotation_speed'] * dt
            p['size'] *= 0.98
    
    def render(self) -> None:
        """渲染动画"""
        if self.is_complete:
            return
        
        # 绘制粒子
        for p in self.particles:
            if p['alpha'] > 0:
                color = (100, 100, 100, p['alpha'])
                arcade.draw_circle_filled(p['x'], p['y'], p['size'], color)
        
        # 绘制淡出的僵尸轮廓
        alpha = int(200 * (1.0 - self.progress))
        if alpha > 0:
            # 绘制简化轮廓
            arcade.draw_ellipse_filled(
                self.x, self.y,
                30 * (1.0 - self.progress * 0.5),
                50 * (1.0 - self.progress * 0.5),
                (80, 80, 80, alpha)
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
    
    def trigger_hit(self, zombie_id: int) -> None:
        """触发僵尸受击效果"""
        state = self.get_or_create_state(zombie_id)
        state.trigger_hit()
    
    def start_death_animation(self, zombie_id: int, x: float, y: float,
                             zombie_type: str = 'normal') -> None:
        """开始死亡动画"""
        # 创建死亡动画
        anim = DeathAnimation(x=x, y=y, zombie_type=zombie_type)
        self.death_animations.append(anim)
        
        # 标记状态
        if zombie_id in self.zombie_states:
            self.zombie_states[zombie_id].start_death()
    
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
    
    def apply_hit_flash_to_color(self, zombie_id: int, 
                                  base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """将受击闪烁应用到颜色"""
        flash = self.get_hit_flash_intensity(zombie_id)
        if flash > 0:
            # 向白色混合
            return tuple(int(c + (255 - c) * flash) for c in base_color)
        return base_color
    
    def clear(self) -> None:
        """清除所有状态"""
        self.zombie_states.clear()
        self.death_animations.clear()
    
    def get_active_death_count(self) -> int:
        """获取活动死亡动画数量"""
        return len(self.death_animations)
