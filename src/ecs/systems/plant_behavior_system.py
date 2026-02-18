"""
植物行为系统 - 处理植物的攻击和特殊行为
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, PlantComponent, GridPositionComponent,
    ProjectileType
)


class PlantBehaviorSystem(System):
    """
    植物行为系统
    
    处理植物的攻击逻辑和特殊行为
    - 豌豆射手：发射豌豆
    - 向日葵：产生阳光
    - 樱桃炸弹：爆炸
    等
    """
    
    def __init__(self, entity_factory, priority: int = 40):
        super().__init__(priority)
        self.entity_factory = entity_factory
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新植物行为"""
        # 获取所有植物实体
        entities = component_manager.query(
            TransformComponent, PlantComponent, GridPositionComponent
        )
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            plant = component_manager.get_component(entity_id, PlantComponent)
            grid_pos = component_manager.get_component(entity_id, GridPositionComponent)
            
            if not all([transform, plant, grid_pos]):
                continue
            
            # 更新攻击计时器
            plant.update_timer(dt)
            
            # 处理攻击逻辑
            if plant.can_attack():
                self._handle_attack(entity_id, transform, plant, grid_pos, dt)
    
    def _handle_attack(self, entity_id: int, transform, plant, grid_pos, dt: float) -> None:
        """处理植物攻击"""
        from ..components import PlantTypeComponent
        
        plant_type_comp = component_manager.get_component(entity_id, PlantTypeComponent)
        if not plant_type_comp:
            return
        
        plant_type = plant_type_comp.plant_type
        
        # 根据植物类型处理不同攻击方式
        if plant_type.value in [1, 3, 6, 8]:  # 射手类植物
            # 发射投射物
            self._shoot_projectile(transform, grid_pos, plant_type)
            plant.start_cooldown()
    
    def _shoot_projectile(self, transform, grid_pos, plant_type) -> None:
        """发射投射物"""
        from ..components import PlantType
        
        # 确定投射物类型
        if plant_type == PlantType.SNOW_PEA:
            projectile_type = ProjectileType.FROZEN_PEA
        else:
            projectile_type = ProjectileType.PEA
        
        # 创建投射物
        self.entity_factory.create_projectile(
            projectile_type,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )