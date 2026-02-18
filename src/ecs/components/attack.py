"""
攻击组件 - 实体的攻击能力
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AttackComponent:
    """
    攻击组件
    
    存储实体的攻击能力
    
    Attributes:
        damage: 基础伤害
        range: 攻击范围（像素）
        cooldown: 攻击冷却时间（秒）
        timer: 当前冷却计时器
        can_attack: 是否可以攻击
        target_entity: 当前目标实体ID
    """
    damage: int = 20
    range: float = 100.0
    cooldown: float = 1.0
    timer: float = 0.0
    can_attack: bool = True
    target_entity: Optional[int] = None
    
    def update(self, dt: float) -> None:
        """更新攻击状态"""
        if self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                self.can_attack = True
    
    def attack(self) -> None:
        """执行攻击"""
        if self.can_attack:
            self.can_attack = False
            self.timer = self.cooldown
    
    def is_ready(self) -> bool:
        """检查是否可以攻击"""
        return self.can_attack and self.timer <= 0
    
    def set_target(self, entity_id: Optional[int]) -> None:
        """设置攻击目标"""
        self.target_entity = entity_id
    
    def clear_target(self) -> None:
        """清除攻击目标"""
        self.target_entity = None