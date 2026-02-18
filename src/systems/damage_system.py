import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class DamageSystem:
    """伤害系统"""
    
    def __init__(self):
        pass
    
    def apply_damage(self, target, damage: int):
        """应用伤害"""
        target.take_damage(damage)
    
    def apply_area_damage(self, targets: list, center_x: float, center_y: float, 
                          radius: float, damage: int):
        """应用范围伤害"""
        for target in targets:
            dist = ((target.x - center_x) ** 2 + (target.y - center_y) ** 2) ** 0.5
            if dist <= radius:
                target.take_damage(damage)
