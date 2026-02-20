"""
辅助植物系统

处理辅助类植物的行为：
- 磁力菇：移除僵尸的金属防具
"""

from typing import TYPE_CHECKING
from .base_plant_system import BasePlantSystem
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent, ZombieComponent
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class SupportPlantSystem(BasePlantSystem):
    """
    辅助植物系统
    
    处理辅助类植物的特殊效果：
    - 磁力菇：移除范围内僵尸的金属防具
    
    Attributes:
        SUPPORT_TYPES: 辅助类植物类型集合
        MAGNET_RANGE: 磁力菇作用范围（像素）
        MAGNET_COOLDOWN: 磁力菇冷却时间（秒）
    """
    
    SUPPORT_TYPES = {PlantType.MAGNET_SHROOM}
    MAGNET_RANGE = 200.0
    MAGNET_COOLDOWN = 10.0
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 44):
        """
        初始化辅助植物系统
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(entity_factory, priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新辅助植物状态
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        plants = self._get_plants_of_type(
            list(self.SUPPORT_TYPES), component_manager
        )
        
        for plant_id in plants:
            self._update_plant(plant_id, dt, component_manager)
    
    def _update_plant(self, plant_id: int, dt: float,
                     component_manager: ComponentManager) -> None:
        """
        更新单个辅助植物
        
        Args:
            plant_id: 植物实体ID
            dt: 时间增量
            component_manager: 组件管理器
        """
        plant = component_manager.get_component(plant_id, PlantComponent)
        transform = component_manager.get_component(plant_id, TransformComponent)
        
        if not plant or not transform:
            return
        
        # 更新冷却
        plant.update_attack_cooldown(dt)
        
        # 检查是否可以激活
        if not plant.can_attack:
            return
        
        # 处理磁力菇效果
        if plant.plant_type == PlantType.MAGNET_SHROOM:
            if self._apply_magnet_effect(plant_id, transform, component_manager):
                plant.start_attack()
    
    def _apply_magnet_effect(self, plant_id: int,
                            transform: TransformComponent,
                            component_manager: ComponentManager) -> bool:
        """
        应用磁力菇效果
        
        移除范围内僵尸的金属防具
        
        Args:
            plant_id: 植物实体ID
            transform: 变换组件
            component_manager: 组件管理器
            
        Returns:
            是否成功应用效果
        """
        # 查找范围内的僵尸
        zombies = self._get_zombies_in_range(
            transform.x, transform.y, self.MAGNET_RANGE, component_manager
        )
        
        affected = False
        
        for zombie_id in zombies:
            # 检查僵尸是否有金属防具
            if self._has_metal_armor(zombie_id, component_manager):
                # 移除防具
                self._remove_metal_armor(zombie_id, component_manager)
                affected = True
        
        return affected
    
    def _get_zombies_in_range(self, x: float, y: float, radius: float,
                             component_manager: ComponentManager) -> list:
        """
        获取范围内的所有僵尸
        
        Args:
            x: 中心X坐标
            y: 中心Y坐标
            radius: 范围半径
            component_manager: 组件管理器
            
        Returns:
            僵尸实体ID列表
        """
        zombies = []
        zombie_entities = component_manager.query(ZombieComponent, TransformComponent)
        
        for zombie_id in zombie_entities:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            
            if zombie_transform:
                distance = ((zombie_transform.x - x) ** 2 + 
                           (zombie_transform.y - y) ** 2) ** 0.5)
                
                if distance <= radius:
                    zombies.append(zombie_id)
        
        return zombies
    
    def _has_metal_armor(self, zombie_id: int,
                        component_manager: ComponentManager) -> bool:
        """
        检查僵尸是否有金属防具
        
        Args:
            zombie_id: 僵尸实体ID
            component_manager: 组件管理器
            
        Returns:
            是否有金属防具
        """
        zombie = component_manager.get_component(zombie_id, ZombieComponent)
        
        if not zombie:
            return False
        
        # 检查僵尸类型是否有金属防具
        from ...components import ZombieType
        
        metal_armor_types = {
            ZombieType.BUCKETHEAD,
            ZombieType.FOOTBALL,
            ZombieType.DANCER,
        }
        
        zombie_type = component_manager.get_component(zombie_id, 
            type('ZombieTypeComponent', (), {}))
        
        # 简化实现：检查僵尸类型
        # 实际应该检查具体的防具组件
        return False  # 暂不支持
    
    def _remove_metal_armor(self, zombie_id: int,
                           component_manager: ComponentManager) -> None:
        """
        移除僵尸的金属防具
        
        Args:
            zombie_id: 僵尸实体ID
            component_manager: 组件管理器
        """
        # 实际实现应该修改僵尸的防御属性
        # 这里简化处理
        pass
