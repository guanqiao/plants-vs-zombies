"""
植物系统基类

提供所有植物系统共享的功能和工具方法
"""

from typing import List, Optional, TYPE_CHECKING
from ...system import System
from ...component import ComponentManager
from ...components import (
    TransformComponent, PlantComponent, ZombieComponent,
    GridPositionComponent
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class BasePlantSystem(System):
    """
    植物系统基类
    
    提供植物系统共享的功能：
    - 行内僵尸查询
    - 范围内僵尸查询
    - 植物类型过滤
    
    Attributes:
        entity_factory: 实体工厂，用于创建投射物等
    """
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 40):
        """
        初始化植物系统基类
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(priority)
        self.entity_factory = entity_factory
    
    def _has_zombie_in_row(self, row: int, 
                           component_manager: ComponentManager) -> bool:
        """
        检查指定行是否有僵尸
        
        Args:
            row: 行号（0-4）
            component_manager: 组件管理器
            
        Returns:
            该行是否有僵尸
        """
        zombies = component_manager.query(ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            grid_pos = component_manager.get_component(zombie_id, GridPositionComponent)
            if grid_pos and grid_pos.row == row:
                return True
        
        return False
    
    def _has_zombie_in_three_rows(self, center_row: int,
                                   component_manager: ComponentManager) -> bool:
        """
        检查中心行及其上下行是否有僵尸
        
        用于三线射手的攻击检测
        
        Args:
            center_row: 中心行号
            component_manager: 组件管理器
            
        Returns:
            三行中任意一行是否有僵尸
        """
        rows_to_check = [center_row]
        
        if center_row > 0:
            rows_to_check.append(center_row - 1)
        if center_row < 4:
            rows_to_check.append(center_row + 1)
        
        for row in rows_to_check:
            if self._has_zombie_in_row(row, component_manager):
                return True
        
        return False
    
    def _get_zombies_in_row(self, row: int,
                           component_manager: ComponentManager) -> List[int]:
        """
        获取指定行的所有僵尸
        
        Args:
            row: 行号
            component_manager: 组件管理器
            
        Returns:
            僵尸实体ID列表
        """
        zombies = []
        zombie_entities = component_manager.query(ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombie_entities:
            grid_pos = component_manager.get_component(zombie_id, GridPositionComponent)
            if grid_pos and grid_pos.row == row:
                zombies.append(zombie_id)
        
        return zombies
    
    def _get_closest_zombie_in_row(self, row: int, x: float,
                                    component_manager: ComponentManager) -> Optional[int]:
        """
        获取指定行中距离X坐标最近的僵尸
        
        Args:
            row: 行号
            x: X坐标（用于计算距离）
            component_manager: 组件管理器
            
        Returns:
            最近的僵尸实体ID，如果没有则返回None
        """
        zombies = self._get_zombies_in_row(row, component_manager)
        
        if not zombies:
            return None
        
        closest_zombie = None
        min_distance = float('inf')
        
        for zombie_id in zombies:
            transform = component_manager.get_component(zombie_id, TransformComponent)
            if transform:
                distance = abs(transform.x - x)
                if distance < min_distance:
                    min_distance = distance
                    closest_zombie = zombie_id
        
        return closest_zombie
    
    def _get_plants_of_type(self, plant_types: List,
                           component_manager: ComponentManager) -> List[int]:
        """
        获取指定类型的所有植物
        
        Args:
            plant_types: 植物类型列表
            component_manager: 组件管理器
            
        Returns:
            植物实体ID列表
        """
        plants = []
        plant_entities = component_manager.query(PlantComponent, TransformComponent)
        
        for plant_id in plant_entities:
            plant = component_manager.get_component(plant_id, PlantComponent)
            if plant and plant.plant_type in plant_types:
                plants.append(plant_id)
        
        return plants
