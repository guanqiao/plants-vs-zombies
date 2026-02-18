"""
植物行为系统 - 处理植物的攻击和特殊行为
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, PlantComponent, GridPositionComponent,
    ProjectileType, PlantTypeComponent, PlantType
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
    
    # 射手类植物类型
    SHOOTER_PLANTS = {
        PlantType.PEASHOOTER,
        PlantType.SNOW_PEA,
        PlantType.REPEATER,
        PlantType.THREEPEATER,
    }
    
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
                self._handle_attack(entity_id, transform, plant, grid_pos, component_manager)
    
    def _handle_attack(self, entity_id: int, transform, plant, grid_pos, 
                       component_manager: ComponentManager) -> None:
        """处理植物攻击"""
        plant_type_comp = component_manager.get_component(entity_id, PlantTypeComponent)
        if not plant_type_comp:
            return
        
        plant_type = plant_type_comp.plant_type
        
        # 根据植物类型处理不同攻击方式
        if plant_type in self.SHOOTER_PLANTS:
            # 检查同行是否有僵尸
            if self._has_zombie_in_row(grid_pos.row, component_manager):
                # 发射投射物
                self._shoot_projectile(transform, grid_pos, plant_type)
                plant.start_cooldown()
        
        # 特殊植物处理
        elif plant_type == PlantType.SUNFLOWER:
            # 向日葵不产生投射物，而是产生阳光
            # 这个逻辑在SunSystem中处理
            pass
    
    def _has_zombie_in_row(self, row: int, component_manager: ComponentManager) -> bool:
        """
        检查指定行是否有僵尸
        
        Args:
            row: 行索引
            component_manager: 组件管理器
            
        Returns:
            是否有僵尸在该行
        """
        from ..components import ZombieComponent
        
        # 获取所有僵尸
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            if zombie_grid and zombie_grid.row == row:
                return True
        
        return False
    
    def _shoot_projectile(self, transform, grid_pos, plant_type) -> None:
        """发射投射物"""
        # 确定投射物类型
        if plant_type == PlantType.SNOW_PEA:
            projectile_type = ProjectileType.FROZEN_PEA
        else:
            projectile_type = ProjectileType.PEA
        
        # 创建投射物
        self.entity_factory.create_projectile(
            projectile_type,
            transform.x + 30,  # 从植物右侧发射
            transform.y,
            grid_pos.row
        )
    
    def _shoot_three_projectiles(self, transform, grid_pos) -> None:
        """
        三线射手发射三行投射物
        
        Args:
            transform: 植物变换组件
            grid_pos: 网格位置组件
        """
        # 发射到当前行和上下两行
        for row_offset in [-1, 0, 1]:
            target_row = grid_pos.row + row_offset
            if 0 <= target_row < 5:  # 确保在有效范围内
                self.entity_factory.create_projectile(
                    ProjectileType.PEA,
                    transform.x + 30,
                    transform.y + row_offset * 100,  # 调整Y坐标到对应行
                    target_row
                )
