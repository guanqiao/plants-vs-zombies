"""
屏幕震动效果
"""

import random
from typing import Tuple


class ScreenShake:
    """
    屏幕震动效果
    
    模拟爆炸、重击等场景的屏幕震动
    """
    
    def __init__(self):
        self.shake_intensity = 0.0
        self.shake_duration = 0.0
        self.shake_timer = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.decay_rate = 5.0  # 衰减速度
    
    def shake(self, intensity: float, duration: float) -> None:
        """
        触发屏幕震动
        
        Args:
            intensity: 震动强度（像素）
            duration: 持续时间（秒）
        """
        self.shake_intensity = max(self.shake_intensity, intensity)
        self.shake_duration = max(self.shake_duration, duration)
        self.shake_timer = self.shake_duration
    
    def update(self, dt: float) -> None:
        """
        更新震动状态
        
        Args:
            dt: 时间增量
        """
        if self.shake_timer > 0:
            self.shake_timer -= dt
            
            # 计算当前强度（随时间衰减）
            progress = self.shake_timer / self.shake_duration
            current_intensity = self.shake_intensity * progress
            
            # 随机偏移
            self.offset_x = random.uniform(-current_intensity, current_intensity)
            self.offset_y = random.uniform(-current_intensity, current_intensity)
            
            # 震动结束
            if self.shake_timer <= 0:
                self.offset_x = 0.0
                self.offset_y = 0.0
                self.shake_intensity = 0.0
                self.shake_duration = 0.0
    
    def get_offset(self) -> Tuple[float, float]:
        """
        获取当前震动偏移
        
        Returns:
            (offset_x, offset_y)
        """
        return (self.offset_x, self.offset_y)
    
    def is_shaking(self) -> bool:
        """检查是否正在震动"""
        return self.shake_timer > 0
    
    def stop(self) -> None:
        """立即停止震动"""
        self.shake_timer = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.shake_intensity = 0.0
