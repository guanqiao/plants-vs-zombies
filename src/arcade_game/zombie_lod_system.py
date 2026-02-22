"""
僵尸LOD（细节层次）系统 - 性能优化

包括：
- 根据距离调整动画质量
- 远距离僵尸简化渲染
- 屏幕外僵尸跳过渲染
- 动态帧率控制
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class LODLevel(Enum):
    """LOD等级"""
    HIGH = auto()      # 高质量 - 近距离
    MEDIUM = auto()    # 中等质量 - 中距离
    LOW = auto()       # 低质量 - 远距离
    CULLED = auto()    # 剔除 - 屏幕外或过远


@dataclass
class LODConfig:
    """LOD配置"""
    # 距离阈值（像素）
    high_distance: float = 200.0    # 高质量距离
    medium_distance: float = 400.0  # 中等质量距离
    low_distance: float = 600.0     # 低质量距离
    
    # 动画帧率控制
    high_fps: int = 60      # 高质量动画帧率
    medium_fps: int = 30    # 中等质量动画帧率
    low_fps: int = 15       # 低质量动画帧率
    
    # 特效开关
    enable_shadow_high: bool = True
    enable_shadow_medium: bool = True
    enable_shadow_low: bool = False
    
    enable_dust_high: bool = True
    enable_dust_medium: bool = False
    enable_dust_low: bool = False
    
    enable_expression_high: bool = True
    enable_expression_medium: bool = True
    enable_expression_low: bool = False
    
    # 简化渲染
    simplify_body_high: bool = False
    simplify_body_medium: bool = True
    simplify_body_low: bool = True


@dataclass
class ZombieLODState:
    """僵尸LOD状态"""
    current_level: LODLevel = LODLevel.HIGH
    distance_to_camera: float = 0.0
    is_on_screen: bool = True
    
    # 动画控制
    animation_timer: float = 0.0
    animation_interval: float = 1.0 / 60.0  # 默认60fps
    skip_animation: bool = False
    
    # 渲染计数（用于跳帧）
    frame_counter: int = 0
    render_every_n_frames: int = 1
    
    def update(self, dt: float, lod_config: LODConfig) -> None:
        """更新LOD状态"""
        # 根据距离确定LOD等级
        if self.distance_to_camera > lod_config.low_distance:
            self.current_level = LODLevel.CULLED
        elif self.distance_to_camera > lod_config.medium_distance:
            self.current_level = LODLevel.LOW
        elif self.distance_to_camera > lod_config.high_distance:
            self.current_level = LODLevel.MEDIUM
        else:
            self.current_level = LODLevel.HIGH
        
        # 根据LOD等级设置动画帧率
        if self.current_level == LODLevel.HIGH:
            self.animation_interval = 1.0 / lod_config.high_fps
            self.render_every_n_frames = 1
        elif self.current_level == LODLevel.MEDIUM:
            self.animation_interval = 1.0 / lod_config.medium_fps
            self.render_every_n_frames = 2
        elif self.current_level == LODLevel.LOW:
            self.animation_interval = 1.0 / lod_config.low_fps
            self.render_every_n_frames = 4
        else:  # CULLED
            self.skip_animation = True
            return
        
        # 更新动画计时器
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0.0
            self.skip_animation = False
        else:
            self.skip_animation = True
        
        # 更新帧计数器
        self.frame_counter = (self.frame_counter + 1) % self.render_every_n_frames
    
    def should_render(self) -> bool:
        """是否应该渲染"""
        if self.current_level == LODLevel.CULLED:
            return False
        if not self.is_on_screen:
            return False
        return self.frame_counter == 0
    
    def should_render_shadow(self, lod_config: LODConfig) -> bool:
        """是否应该渲染阴影"""
        if self.current_level == LODLevel.HIGH:
            return lod_config.enable_shadow_high
        elif self.current_level == LODLevel.MEDIUM:
            return lod_config.enable_shadow_medium
        elif self.current_level == LODLevel.LOW:
            return lod_config.enable_shadow_low
        return False
    
    def should_render_dust(self, lod_config: LODConfig) -> bool:
        """是否应该渲染尘土"""
        if self.current_level == LODLevel.HIGH:
            return lod_config.enable_dust_high
        elif self.current_level == LODLevel.MEDIUM:
            return lod_config.enable_dust_medium
        elif self.current_level == LODLevel.LOW:
            return lod_config.enable_dust_low
        return False
    
    def should_render_expression(self, lod_config: LODConfig) -> bool:
        """是否应该渲染表情"""
        if self.current_level == LODLevel.HIGH:
            return lod_config.enable_expression_high
        elif self.current_level == LODLevel.MEDIUM:
            return lod_config.enable_expression_medium
        elif self.current_level == LODLevel.LOW:
            return lod_config.enable_expression_low
        return False
    
    def should_simplify_body(self, lod_config: LODConfig) -> bool:
        """是否应该简化身体渲染"""
        if self.current_level == LODLevel.HIGH:
            return lod_config.simplify_body_high
        elif self.current_level == LODLevel.MEDIUM:
            return lod_config.simplify_body_medium
        elif self.current_level == LODLevel.LOW:
            return lod_config.simplify_body_low
        return True


class ZombieLODSystem:
    """
    僵尸LOD系统
    
    根据僵尸与摄像机的距离和屏幕位置，动态调整渲染质量
    """
    
    def __init__(self, screen_width: float = 900, screen_height: float = 600):
        self._states: Dict[int, ZombieLODState] = {}
        self._config = LODConfig()
        
        # 屏幕参数
        self._screen_width = screen_width
        self._screen_height = screen_height
        self._camera_x = screen_width / 2
        self._camera_y = screen_height / 2
        
        # 性能统计
        self._rendered_count = 0
        self._culled_count = 0
        self._total_count = 0
    
    def update(self, dt: float, zombie_id: int, zombie_x: float, zombie_y: float) -> None:
        """
        更新僵尸LOD状态
        
        Args:
            dt: 时间增量
            zombie_id: 僵尸实体ID
            zombie_x: 僵尸X坐标
            zombie_y: 僵尸Y坐标
        """
        state = self._get_or_create_state(zombie_id)
        
        # 计算与摄像机的距离
        dx = zombie_x - self._camera_x
        dy = zombie_y - self._camera_y
        state.distance_to_camera = math.sqrt(dx * dx + dy * dy)
        
        # 检查是否在屏幕内（添加一些边距）
        margin = 100.0
        state.is_on_screen = (
            -margin <= zombie_x <= self._screen_width + margin and
            -margin <= zombie_y <= self._screen_height + margin
        )
        
        # 更新LOD状态
        state.update(dt, self._config)
    
    def should_render(self, zombie_id: int) -> bool:
        """判断僵尸是否应该渲染"""
        if zombie_id not in self._states:
            return True  # 默认渲染
        return self._states[zombie_id].should_render()
    
    def should_update_animation(self, zombie_id: int) -> bool:
        """判断是否应该更新动画"""
        if zombie_id not in self._states:
            return True
        state = self._states[zombie_id]
        return not state.skip_animation
    
    def get_lod_level(self, zombie_id: int) -> LODLevel:
        """获取僵尸的LOD等级"""
        if zombie_id not in self._states:
            return LODLevel.HIGH
        return self._states[zombie_id].current_level
    
    def should_render_shadow(self, zombie_id: int) -> bool:
        """判断是否应该渲染阴影"""
        if zombie_id not in self._states:
            return True
        return self._states[zombie_id].should_render_shadow(self._config)
    
    def should_render_dust(self, zombie_id: int) -> bool:
        """判断是否应该渲染尘土"""
        if zombie_id not in self._states:
            return True
        return self._states[zombie_id].should_render_dust(self._config)
    
    def should_render_expression(self, zombie_id: int) -> bool:
        """判断是否应该渲染表情"""
        if zombie_id not in self._states:
            return True
        return self._states[zombie_id].should_render_expression(self._config)
    
    def should_simplify_body(self, zombie_id: int) -> bool:
        """判断是否应该简化身体渲染"""
        if zombie_id not in self._states:
            return False
        return self._states[zombie_id].should_simplify_body(self._config)
    
    def set_camera_position(self, x: float, y: float) -> None:
        """设置摄像机位置"""
        self._camera_x = x
        self._camera_y = y
    
    def set_screen_size(self, width: float, height: float) -> None:
        """设置屏幕大小"""
        self._screen_width = width
        self._screen_height = height
    
    def update_config(self, **kwargs) -> None:
        """更新LOD配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get_config(self) -> LODConfig:
        """获取当前配置"""
        return self._config
    
    def remove_zombie(self, zombie_id: int) -> None:
        """移除僵尸LOD状态"""
        self._states.pop(zombie_id, None)
    
    def clear(self) -> None:
        """清除所有状态"""
        self._states.clear()
        self._reset_stats()
    
    def _get_or_create_state(self, zombie_id: int) -> ZombieLODState:
        """获取或创建LOD状态"""
        if zombie_id not in self._states:
            self._states[zombie_id] = ZombieLODState()
        return self._states[zombie_id]
    
    def _reset_stats(self) -> None:
        """重置统计"""
        self._rendered_count = 0
        self._culled_count = 0
        self._total_count = 0
    
    def get_stats(self) -> Dict[str, int]:
        """获取性能统计"""
        stats = {
            'total': len(self._states),
            'high': 0,
            'medium': 0,
            'low': 0,
            'culled': 0,
        }
        for state in self._states.values():
            if state.current_level == LODLevel.HIGH:
                stats['high'] += 1
            elif state.current_level == LODLevel.MEDIUM:
                stats['medium'] += 1
            elif state.current_level == LODLevel.LOW:
                stats['low'] += 1
            elif state.current_level == LODLevel.CULLED:
                stats['culled'] += 1
        return stats


# 全局LOD系统实例
_lod_system: Optional[ZombieLODSystem] = None


def get_zombie_lod_system(screen_width: float = 900, 
                         screen_height: float = 600) -> ZombieLODSystem:
    """获取僵尸LOD系统实例"""
    global _lod_system
    if _lod_system is None:
        _lod_system = ZombieLODSystem(screen_width, screen_height)
    return _lod_system
