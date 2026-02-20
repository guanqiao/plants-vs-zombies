"""
射手植物系统

处理所有射手类植物的行为：
- 豌豆射手：普通投射物
- 寒冰射手：冰冻投射物，带减速效果
- 双发射手：一次发射两个投射物
- 三线射手：同时攻击三行

使用策略模式重构，消除复杂的if-elif链
"""

from typing import TYPE_CHECKING
from .base_plant_system import BasePlantSystem
from .attack_strategies import AttackStrategyRegistry
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class ShooterPlantSystem(BasePlantSystem):
    """
    射手植物系统
    
    处理射手类植物的攻击逻辑：
    - 检测同行僵尸
    - 发射投射物
    - 管理攻击冷却
    
    使用策略模式，通过AttackStrategyRegistry获取对应的攻击策略
    
    Attributes:
        SHOOTER_TYPES: 射手类植物类型集合
    """
    
    SHOOTER_TYPES = {
        PlantType.PEASHOOTER,
        PlantType.SNOW_PEA,
        PlantType.REPEATER,
        PlantType.THREEPEATER,
    }
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 40):
        """
        初始化射手植物系统
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(entity_factory, priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新射手植物状态
        
        检查攻击冷却，如果有僵尸在攻击范围内则发射投射物
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        # 获取所有射手类植物
        plants = self._get_plants_of_type(
            list(self.SHOOTER_TYPES), component_manager
        )
        
        for plant_id in plants:
            self._update_plant(plant_id, dt, component_manager)
    
    def _update_plant(self, plant_id: int, dt: float,
                     component_manager: ComponentManager) -> None:
        """
        更新单个射手植物
        
        Args:
            plant_id: 植物实体ID
            dt: 时间增量
            component_manager: 组件管理器
        """
        plant = component_manager.get_component(plant_id, PlantComponent)
        transform = component_manager.get_component(plant_id, TransformComponent)
        grid_pos = component_manager.get_component(plant_id, GridPositionComponent)
        
        if not all([plant, transform, grid_pos]):
            return
        
        # 更新攻击冷却
        plant.update_attack_cooldown(dt)
        
        # 检查是否可以攻击
        if not plant.can_attack:
            return
        
        # 检查是否有僵尸在攻击范围内
        if self._should_shoot(plant.plant_type, grid_pos.row, component_manager):
            # 使用策略模式执行攻击
            self._execute_attack(plant_id, plant, transform, grid_pos, component_manager)
            plant.start_attack()
    
    def _should_shoot(self, plant_type: PlantType, row: int,
                     component_manager: ComponentManager) -> bool:
        """
        检查是否应该射击
        
        三线射手检查三行，其他射手检查单行
        
        Args:
            plant_type: 植物类型
            row: 植物所在行
            component_manager: 组件管理器
            
        Returns:
            是否应该射击
        """
        if plant_type == PlantType.THREEPEATER:
            return self._has_zombie_in_three_rows(row, component_manager)
        else:
            return self._has_zombie_in_row(row, component_manager)
    
    def _execute_attack(self, plant_id: int, plant: PlantComponent,
                       transform: TransformComponent,
                       grid_pos: GridPositionComponent,
                       component_manager: ComponentManager) -> None:
        """
        执行攻击
        
        使用策略模式，根据植物类型获取对应的攻击策略
        
        Args:
            plant_id: 植物实体ID
            plant: 植物组件
            transform: 变换组件
            grid_pos: 网格位置组件
            component_manager: 组件管理器
        """
        strategy = AttackStrategyRegistry.get_strategy(plant.plant_type)
        strategy.execute(
            plant_id, plant, transform, grid_pos,
            self.entity_factory, component_manager
        )
