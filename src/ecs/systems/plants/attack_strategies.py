"""
攻击策略模式

使用策略模式重构植物攻击逻辑，消除复杂的if-elif链
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, TYPE_CHECKING
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent, ProjectileType
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class AttackStrategy(ABC):
    """
    攻击策略抽象基类
    
    定义植物攻击的通用接口
    """
    
    @abstractmethod
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """
        执行攻击
        
        Args:
            plant_id: 植物实体ID
            plant: 植物组件
            transform: 变换组件
            grid_pos: 网格位置组件
            entity_factory: 实体工厂
            component_manager: 组件管理器
            
        Returns:
            是否成功执行攻击
        """
        pass


class ShooterStrategy(AttackStrategy):
    """射手策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """发射普通投射物"""
        entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        return True


class SnowPeaStrategy(AttackStrategy):
    """寒冰射手策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """发射冰冻投射物"""
        entity_factory.create_projectile(
            ProjectileType.FROZEN_PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        return True


class RepeaterStrategy(AttackStrategy):
    """双发射手策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """发射两个投射物"""
        # 第一个豌豆
        entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        # 第二个豌豆（稍微延迟）
        entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 40,
            transform.y,
            grid_pos.row
        )
        return True


class ThreepeaterStrategy(AttackStrategy):
    """三线射手策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """同时向三行发射"""
        center_row = grid_pos.row
        
        # 发射到当前行
        entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            center_row
        )
        
        # 发射到上一行
        if center_row > 0:
            y_offset = -100
            entity_factory.create_projectile(
                ProjectileType.PEA,
                transform.x + 30,
                transform.y + y_offset,
                center_row - 1
            )
        
        # 发射到下一行
        if center_row < 4:
            y_offset = 100
            entity_factory.create_projectile(
                ProjectileType.PEA,
                transform.x + 30,
                transform.y + y_offset,
                center_row + 1
            )
        
        return True


class MelonPultStrategy(AttackStrategy):
    """西瓜投手策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """发射西瓜"""
        entity_factory.create_projectile(
            ProjectileType.MELON,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        return True


class WinterMelonStrategy(AttackStrategy):
    """冰西瓜策略"""
    
    def execute(self, plant_id: int, plant: PlantComponent,
                transform: TransformComponent,
                grid_pos: GridPositionComponent,
                entity_factory: 'EntityFactory',
                component_manager: ComponentManager) -> bool:
        """发射冰冻西瓜"""
        entity_factory.create_projectile(
            ProjectileType.WINTER_MELON,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        return True


class AttackStrategyRegistry:
    """
    攻击策略注册表
    
    管理植物类型到攻击策略的映射
    """
    
    _strategies: Dict[PlantType, AttackStrategy] = {}
    
    @classmethod
    def register(cls, plant_type: PlantType, strategy: AttackStrategy) -> None:
        """
        注册攻击策略
        
        Args:
            plant_type: 植物类型
            strategy: 攻击策略实例
        """
        cls._strategies[plant_type] = strategy
    
    @classmethod
    def get_strategy(cls, plant_type: PlantType) -> AttackStrategy:
        """
        获取攻击策略
        
        Args:
            plant_type: 植物类型
            
        Returns:
            攻击策略实例，如果没有则返回默认策略
        """
        return cls._strategies.get(plant_type, ShooterStrategy())
    
    @classmethod
    def has_strategy(cls, plant_type: PlantType) -> bool:
        """
        检查是否有策略
        
        Args:
            plant_type: 植物类型
            
        Returns:
            是否有对应的攻击策略
        """
        return plant_type in cls._strategies


# 注册所有攻击策略
AttackStrategyRegistry.register(PlantType.PEASHOOTER, ShooterStrategy())
AttackStrategyRegistry.register(PlantType.SNOW_PEA, SnowPeaStrategy())
AttackStrategyRegistry.register(PlantType.REPEATER, RepeaterStrategy())
AttackStrategyRegistry.register(PlantType.THREEPEATER, ThreepeaterStrategy())
AttackStrategyRegistry.register(PlantType.MELON_PULT, MelonPultStrategy())
AttackStrategyRegistry.register(PlantType.WINTER_MELON, WinterMelonStrategy())
