"""
植物卡片管理器 - 管理植物卡片的冷却状态
"""
from typing import Dict, Optional


class PlantCardManager:
    """
    植物卡片管理器 - 管理所有植物卡片的冷却状态
    
    每个植物类型有独立的冷却时间，种植后进入冷却状态
    """
    
    def __init__(self):
        """初始化卡片管理器"""
        # 存储每种植物的冷却配置
        self.card_cooldowns: Dict[str, float] = {}
        # 存储每种植物的当前冷却状态
        self.current_cooldowns: Dict[str, float] = {}
    
    def register_card(self, plant_type: str, cooldown_time: float):
        """
        注册植物卡片
        
        Args:
            plant_type: 植物类型标识
            cooldown_time: 冷却时间（秒）
        """
        self.card_cooldowns[plant_type] = cooldown_time
        self.current_cooldowns[plant_type] = 0.0
    
    def can_plant(self, plant_type: str) -> bool:
        """
        检查是否可以种植
        
        Args:
            plant_type: 植物类型标识
            
        Returns:
            True if 冷却完成且可以种植
        """
        if plant_type not in self.card_cooldowns:
            return False
        
        current = self.current_cooldowns.get(plant_type, 0.0)
        return current <= 0
    
    def start_cooldown(self, plant_type: str):
        """
        开始冷却
        
        Args:
            plant_type: 植物类型标识
        """
        if plant_type in self.card_cooldowns:
            self.current_cooldowns[plant_type] = self.card_cooldowns[plant_type]
    
    def update(self, dt: float):
        """
        更新所有冷却状态
        
        Args:
            dt: 时间增量（秒）
        """
        for plant_type in self.current_cooldowns:
            if self.current_cooldowns[plant_type] > 0:
                self.current_cooldowns[plant_type] = max(
                    0.0, 
                    self.current_cooldowns[plant_type] - dt
                )
    
    def get_cooldown_progress(self, plant_type: str) -> float:
        """
        获取冷却进度
        
        Args:
            plant_type: 植物类型标识
            
        Returns:
            0.0 ~ 1.0，1.0表示冷却完成
        """
        if plant_type not in self.card_cooldowns:
            return 0.0
        
        cooldown_time = self.card_cooldowns[plant_type]
        current = self.current_cooldowns.get(plant_type, 0.0)
        
        if cooldown_time <= 0:
            return 1.0
        if current <= 0:
            return 1.0
        
        return 1.0 - (current / cooldown_time)
    
    def get_remaining_cooldown(self, plant_type: str) -> float:
        """
        获取剩余冷却时间
        
        Args:
            plant_type: 植物类型标识
            
        Returns:
            剩余冷却时间（秒）
        """
        return self.current_cooldowns.get(plant_type, 0.0)
    
    def reset_all(self):
        """重置所有冷却"""
        for plant_type in self.current_cooldowns:
            self.current_cooldowns[plant_type] = 0.0
