"""
冷却组件 - 用于植物卡片冷却系统
"""
from dataclasses import dataclass, field


@dataclass
class CooldownComponent:
    """
    冷却组件 - 管理植物卡片的冷却时间
    
    Attributes:
        cooldown_time: 冷却总时间（秒）
        current_cooldown: 当前剩余冷却时间（秒）
        plant_type: 植物类型标识
    """
    cooldown_time: float = 0.0
    current_cooldown: float = 0.0
    plant_type: str = ""
    
    def start_cooldown(self):
        """开始冷却"""
        self.current_cooldown = self.cooldown_time
    
    def update(self, dt: float):
        """
        更新冷却时间
        
        Args:
            dt: 时间增量（秒）
        """
        if self.current_cooldown > 0:
            self.current_cooldown = max(0.0, self.current_cooldown - dt)
    
    def is_ready(self) -> bool:
        """
        检查冷却是否完成
        
        Returns:
            True if 冷却完成，可以种植
        """
        return self.current_cooldown <= 0
    
    def get_progress(self) -> float:
        """
        获取冷却进度
        
        Returns:
            0.0 ~ 1.0，1.0表示冷却完成
        """
        if self.cooldown_time <= 0:
            return 1.0
        if self.current_cooldown <= 0:
            return 1.0
        return 1.0 - (self.current_cooldown / self.cooldown_time)
