"""
投射物渲染器 - 增强的投射物视觉效果

包括：
- 尾迹效果
- 旋转动画
- 击中反馈
- 特殊投射物效果（冰冻、火焰等）
"""

import math
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field
import arcade


@dataclass
class TrailPoint:
    """尾迹点"""
    x: float
    y: float
    alpha: float
    size: float


@dataclass
class ProjectileVisualState:
    """投射物视觉状态"""
    rotation: float = 0.0
    rotation_speed: float = 360.0
    trail: List[TrailPoint] = field(default_factory=list)
    glow_intensity: float = 1.0
    hit_flash: float = 0.0
    
    def update(self, dt: float, x: float, y: float, size: float) -> None:
        """更新状态"""
        # 更新旋转
        self.rotation += self.rotation_speed * dt
        
        # 添加尾迹点
        self.trail.append(TrailPoint(x, y, 1.0, size))
        
        # 更新尾迹
        new_trail = []
        for point in self.trail:
            new_alpha = point.alpha - dt * 4
            new_size = point.size * (0.9 - dt * 0.5)
            if new_alpha > 0 and new_size > 0:
                new_trail.append(TrailPoint(point.x, point.y, new_alpha, new_size))
        self.trail = new_trail[-15:]  # 保留最近15个点
        
        # 更新击中闪光
        self.hit_flash *= 0.85


class ProjectileRenderer:
    """
    投射物渲染器
    
    提供增强的投射物视觉效果
    """
    
    # 颜色配置
    PEA_COLOR = (100, 220, 100)
    PEA_GLOW = (150, 255, 150)
    FROZEN_PEA_COLOR = (150, 200, 255)
    FROZEN_PEA_GLOW = (200, 230, 255)
    FIRE_COLOR = (255, 150, 50)
    FIRE_GLOW = (255, 200, 100)
    
    def __init__(self):
        self.projectile_states: Dict[int, ProjectileVisualState] = {}
        self._time = 0.0
    
    def update(self, dt: float) -> None:
        """更新所有投射物状态"""
        self._time += dt
        
        # 清理已消失的投射物状态
        # 这个会在渲染时自动处理
    
    def get_or_create_state(self, projectile_id: int) -> ProjectileVisualState:
        """获取或创建投射物状态"""
        if projectile_id not in self.projectile_states:
            self.projectile_states[projectile_id] = ProjectileVisualState()
        return self.projectile_states[projectile_id]
    
    def remove_state(self, projectile_id: int) -> None:
        """移除投射物状态"""
        if projectile_id in self.projectile_states:
            del self.projectile_states[projectile_id]
    
    def trigger_hit_flash(self, projectile_id: int) -> None:
        """触发击中闪光"""
        if projectile_id in self.projectile_states:
            self.projectile_states[projectile_id].hit_flash = 1.0
    
    def render_projectile(self, projectile_id: int, x: float, y: float,
                         width: float, height: float,
                         projectile_type: str = 'pea',
                         is_frozen: bool = False) -> None:
        """
        渲染投射物
        
        Args:
            projectile_id: 投射物ID
            x, y: 位置
            width, height: 尺寸
            projectile_type: 投射物类型
            is_frozen: 是否冰冻
        """
        state = self.get_or_create_state(projectile_id)
        state.update(0.016, x, y, min(width, height) / 2)  # 假设60fps
        
        # 确定颜色
        if is_frozen:
            main_color = self.FROZEN_PEA_COLOR
            glow_color = self.FROZEN_PEA_GLOW
        elif projectile_type == 'fire':
            main_color = self.FIRE_COLOR
            glow_color = self.FIRE_GLOW
        else:
            main_color = self.PEA_COLOR
            glow_color = self.PEA_GLOW
        
        radius = min(width, height) / 2
        
        # 绘制尾迹
        self._draw_trail(state.trail, glow_color)
        
        # 绘制外发光
        glow_size = radius * (1.5 + 0.2 * math.sin(self._time * 8))
        arcade.draw_circle_filled(x, y, glow_size, (*glow_color, 80))
        
        # 绘制主体（带旋转效果）
        self._draw_rotating_projectile(x, y, radius, main_color, state.rotation, is_frozen)
        
        # 绘制高光
        highlight_x = x - radius * 0.3
        highlight_y = y + radius * 0.3
        arcade.draw_circle_filled(highlight_x, highlight_y, radius * 0.25,
                                  (255, 255, 255, 180))
        
        # 绘制击中闪光
        if state.hit_flash > 0:
            flash_alpha = int(200 * state.hit_flash)
            flash_size = radius * (1.5 + state.hit_flash)
            arcade.draw_circle_filled(x, y, flash_size, (255, 255, 255, flash_alpha))
    
    def _draw_trail(self, trail: List[TrailPoint], color: Tuple[int, int, int]) -> None:
        """绘制尾迹"""
        for point in trail:
            alpha = int(point.alpha * 100)
            if alpha > 0:
                arcade.draw_circle_filled(
                    point.x, point.y, point.size,
                    (*color, alpha)
                )
    
    def _draw_rotating_projectile(self, x: float, y: float, radius: float,
                                  color: Tuple[int, int, int], rotation: float,
                                  is_frozen: bool) -> None:
        """绘制旋转的投射物"""
        # 主体圆形
        arcade.draw_circle_filled(x, y, radius, color)
        
        # 内部纹理效果（旋转的线条）
        inner_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        
        if is_frozen:
            # 冰冻效果：绘制冰晶图案
            for i in range(6):
                angle = math.radians(rotation + i * 60)
                x1 = x + math.cos(angle) * radius * 0.3
                y1 = y + math.sin(angle) * radius * 0.3
                x2 = x + math.cos(angle) * radius * 0.8
                y2 = y + math.sin(angle) * radius * 0.8
                arcade.draw_line(x1, y1, x2, y2, inner_color, 2)
        else:
            # 普通效果：绘制旋转的弧线
            for i in range(3):
                start_angle = math.radians(rotation + i * 120)
                end_angle = math.radians(rotation + i * 120 + 60)
                arcade.draw_arc_outline(
                    x, y, radius * 0.7, radius * 0.7,
                    inner_color,
                    math.degrees(start_angle), math.degrees(end_angle),
                    2
                )
    
    def render_pea(self, x: float, y: float, size: float = 10.0,
                   projectile_id: int = None) -> None:
        """渲染普通豌豆"""
        if projectile_id is None:
            projectile_id = id((x, y))
        self.render_projectile(projectile_id, x, y, size * 2, size * 2, 'pea', False)
    
    def render_frozen_pea(self, x: float, y: float, size: float = 10.0,
                         projectile_id: int = None) -> None:
        """渲染冰冻豌豆"""
        if projectile_id is None:
            projectile_id = id((x, y))
        self.render_projectile(projectile_id, x, y, size * 2, size * 2, 'pea', True)
    
    def render_melon(self, x: float, y: float, size: float = 15.0,
                    projectile_id: int = None) -> None:
        """渲染西瓜"""
        if projectile_id is None:
            projectile_id = id((x, y))
        
        state = self.get_or_create_state(projectile_id)
        state.update(0.016, x, y, size)
        
        # 西瓜颜色
        melon_color = (50, 150, 50)
        melon_inner = (100, 200, 100)
        
        # 绘制尾迹
        self._draw_trail(state.trail, (100, 200, 100))
        
        # 绘制主体
        arcade.draw_circle_filled(x, y, size, melon_color)
        arcade.draw_circle_filled(x, y, size * 0.7, melon_inner)
        
        # 绘制条纹
        for i in range(4):
            angle = math.radians(state.rotation + i * 90)
            x1 = x + math.cos(angle) * size * 0.3
            y1 = y + math.sin(angle) * size * 0.3
            x2 = x + math.cos(angle) * size * 0.9
            y2 = y + math.sin(angle) * size * 0.9
            arcade.draw_line(x1, y1, x2, y2, (30, 100, 30), 2)
    
    def render_cabbage(self, x: float, y: float, size: float = 12.0,
                      projectile_id: int = None) -> None:
        """渲染卷心菜"""
        if projectile_id is None:
            projectile_id = id((x, y))
        
        state = self.get_or_create_state(projectile_id)
        state.update(0.016, x, y, size)
        
        # 卷心菜颜色
        cabbage_color = (100, 180, 80)
        cabbage_inner = (150, 200, 130)
        
        # 绘制尾迹
        self._draw_trail(state.trail, cabbage_inner)
        
        # 绘制主体（椭圆形）
        arcade.draw_ellipse_filled(x, y, size * 1.2, size, cabbage_color)
        arcade.draw_ellipse_filled(x, y, size * 0.8, size * 0.6, cabbage_inner)
        
        # 绘制叶子纹理
        for i in range(3):
            angle = math.radians(state.rotation + i * 120)
            lx = x + math.cos(angle) * size * 0.5
            ly = y + math.sin(angle) * size * 0.4
            arcade.draw_circle_filled(lx, ly, size * 0.2, cabbage_inner)
    
    def clear(self) -> None:
        """清除所有状态"""
        self.projectile_states.clear()
