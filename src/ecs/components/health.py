"""
生命值组件 - 实体的生命值管理
"""

from dataclasses import dataclass, field


@dataclass
class HealthComponent:
    """
    生命值组件
    
    存储和管理实体的生命值
    
    Attributes:
        current: 当前生命值
        max_health: 最大生命值
        is_dead: 是否已死亡
    """
    current: int
    max_health: int
    is_dead: bool = False
    
    def __post_init__(self):
        if self.current <= 0:
            self.is_dead = True
    
    def take_damage(self, damage: int) -> None:
        """受到伤害"""
        self.current -= damage
        if self.current <= 0:
            self.current = 0
            self.is_dead = True
    
    def heal(self, amount: int) -> None:
        """恢复生命"""
        self.current = min(self.current + amount, self.max_health)
        if self.current > 0:
            self.is_dead = False
    
    def get_health_percent(self) -> float:
        """获取生命值百分比"""
        if self.max_health <= 0:
            return 0.0
        return self.current / self.max_health