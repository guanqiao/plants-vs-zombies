"""
种植动画系统 - 处理植物种植时的动画效果

包括：
- 植物放大动画
- 土粒飞溅
- 光环效果
- 种植成功反馈
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import arcade


@dataclass
class PlantingAnimation:
    """种植动画状态"""
    x: float
    y: float
    plant_color: Tuple[int, int, int]
    progress: float = 0.0
    duration: float = 0.5
    scale: float = 0.0
    glow_intensity: float = 1.0
    ring_radius: float = 0.0
    is_complete: bool = False
    
    def update(self, dt: float) -> None:
        """更新动画"""
        self.progress += dt / self.duration
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.is_complete = True
        
        # 缩放曲线：快速放大然后稳定
        if self.progress < 0.3:
            self.scale = self.progress / 0.3 * 1.2  # 快速放大到1.2倍
        elif self.progress < 0.5:
            self.scale = 1.2 - (self.progress - 0.3) / 0.2 * 0.2  # 缩小到1.0
        else:
            self.scale = 1.0
        
        # 光环扩散
        self.ring_radius = 50 + self.progress * 80
        
        # 发光衰减
        self.glow_intensity = 1.0 - self.progress * 0.7
    
    def render(self) -> None:
        """渲染动画"""
        if self.is_complete:
            return
        
        alpha = int(255 * (1.0 - self.progress * 0.5))
        
        # 绘制光环
        ring_alpha = int(150 * (1.0 - self.progress))
        if ring_alpha > 0:
            arcade.draw_circle_outline(
                self.x, self.y,
                self.ring_radius,
                (*self.plant_color, ring_alpha),
                3
            )
        
        # 绘制发光
        if self.glow_intensity > 0:
            glow_size = 30 * self.glow_intensity
            glow_alpha = int(100 * self.glow_intensity)
            arcade.draw_circle_filled(
                self.x, self.y, glow_size,
                (*self.plant_color, glow_alpha)
            )
        
        # 绘制植物轮廓预览
        preview_size = 25 * self.scale
        arcade.draw_circle_filled(
            self.x, self.y, preview_size,
            (*self.plant_color, alpha)
        )
        
        # 绘制高光
        highlight_size = preview_size * 0.3
        arcade.draw_circle_filled(
            self.x - preview_size * 0.3, self.y + preview_size * 0.3,
            highlight_size,
            (255, 255, 255, int(alpha * 0.7))
        )


class PlantingAnimationSystem:
    """
    种植动画系统
    
    管理所有种植动画效果
    """
    
    def __init__(self):
        self.animations: List[PlantingAnimation] = []
    
    def update(self, dt: float) -> None:
        """更新所有动画"""
        for anim in self.animations:
            anim.update(dt)
        
        # 移除完成的动画
        self.animations = [a for a in self.animations if not a.is_complete]
    
    def render(self) -> None:
        """渲染所有动画"""
        for anim in self.animations:
            anim.render()
    
    def start_planting_animation(self, x: float, y: float,
                                 plant_color: Tuple[int, int, int] = (100, 200, 100),
                                 duration: float = 0.5) -> PlantingAnimation:
        """
        开始种植动画
        
        Args:
            x, y: 种植位置
            plant_color: 植物颜色
            duration: 动画持续时间
            
        Returns:
            创建的动画对象
        """
        anim = PlantingAnimation(
            x=x, y=y,
            plant_color=plant_color,
            duration=duration
        )
        self.animations.append(anim)
        return anim
    
    def clear(self) -> None:
        """清除所有动画"""
        self.animations.clear()
    
    def get_active_count(self) -> int:
        """获取活动动画数量"""
        return len(self.animations)
