"""
植物系统模块

包含所有植物行为相关的系统，按植物类型分类：
- ShooterPlantSystem: 射手类植物（豌豆射手、寒冰射手等）
- ExplosivePlantSystem: 爆炸类植物（樱桃炸弹、土豆雷）
- MeleePlantSystem: 近战类植物（大嘴花、地刺）
- LobberPlantSystem: 投手类植物（西瓜投手、冰西瓜）
- SupportPlantSystem: 辅助类植物（磁力菇）

攻击策略模式：
- AttackStrategy: 攻击策略基类
- AttackStrategyRegistry: 攻击策略注册表
"""

from .base_plant_system import BasePlantSystem
from .shooter_plant_system import ShooterPlantSystem
from .explosive_plant_system import ExplosivePlantSystem
from .melee_plant_system import MeleePlantSystem
from .lobber_plant_system import LobberPlantSystem
from .support_plant_system import SupportPlantSystem
from .attack_strategies import (
    AttackStrategy,
    AttackStrategyRegistry,
    ShooterStrategy,
    SnowPeaStrategy,
    RepeaterStrategy,
    ThreepeaterStrategy,
)

__all__ = [
    'BasePlantSystem',
    'ShooterPlantSystem',
    'ExplosivePlantSystem',
    'MeleePlantSystem',
    'LobberPlantSystem',
    'SupportPlantSystem',
    'AttackStrategy',
    'AttackStrategyRegistry',
    'ShooterStrategy',
    'SnowPeaStrategy',
    'RepeaterStrategy',
    'ThreepeaterStrategy',
]
