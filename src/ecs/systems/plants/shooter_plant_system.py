"""
射手植物系统

处理所有射手类植物的行为：
- 豌豆射手：普通投射物
- 寒冰射手：冰冻投射物，带减速效果
- 双发射手：一次发射两个投射物
- 三线射手：同时攻击三行
"""

from typing import TYPE_CHECKING
from .base_plant_system import BasePlantSystem
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent, ProjectileType
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
            self._shoot(plant_id, plant, transform, grid_pos, component_manager)
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
    
    def _shoot(self, plant_id: int, plant: PlantComponent,
              transform: TransformComponent,
              grid_pos: GridPositionComponent,
              component_manager: ComponentManager) -> None:
        """
        发射投射物
        
        根据植物类型发射不同的投射物
        
        Args:
            plant_id: 植物实体ID
            plant: 植物组件
            transform: 变换组件
            grid_pos: 网格位置组件
            component_manager: 组件管理器
        """
        plant_type = plant.plant_type
        
        if plant_type == PlantType.THREEPEATER:
            self._shoot_three_projectiles(transform, grid_pos)
        elif plant_type == PlantType.REPEATER:
            self._shoot_repeater(transform, grid_pos)
        elif plant_type == PlantType.SNOW_PEA:
            self._shoot_snow_pea(transform, grid_pos)
        else:  # PEASHOOTER
            self._shoot_peashooter(transform, grid_pos)
    
    def _shoot_peashooter(self, transform: TransformComponent,
                         grid_pos: GridPositionComponent) -> None:
        """
        豌豆射手发射
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
        """
        self.entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
    
    def _shoot_snow_pea(self, transform: TransformComponent,
                       grid_pos: GridPositionComponent) -> None:
        """
        寒冰射手发射
        
        发射冰冻豌豆，带减速效果
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
        """
        self.entity_factory.create_projectile(
            ProjectileType.FROZEN_PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
    
    def _shoot_repeater(self, transform: TransformComponent,
                       grid_pos: GridPositionComponent) -> None:
        """
        双发射手发射
        
        一次发射两个投射物
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
        """
        # 第一个豌豆
        self.entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
        # 第二个豌豆（稍微延迟）
        self.entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 40,
            transform.y,
            grid_pos.row
        )
    
    def _shoot_three_projectiles(self, transform: TransformComponent,
                                grid_pos: GridPositionComponent) -> None:
        """
        三线射手发射
        
        同时向三行发射投射物
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
        """
        center_row = grid_pos.row
        
        # 发射到当前行
        self.entity_factory.create_projectile(
            ProjectileType.PEA,
            transform.x + 30,
            transform.y,
            center_row
        )
        
        # 发射到上一行
        if center_row > 0:
            y_offset = -100  # 行间距
            self.entity_factory.create_projectile(
                ProjectileType.PEA,
                transform.x + 30,
                transform.y + y_offset,
                center_row - 1
            )
        
        # 发射到下一行
        if center_row < 4:
            y_offset = 100
            self.entity_factory.create_projectile(
                ProjectileType.PEA,
                transform.x + 30,
                transform.y + y_offset,
                center_row + 1
            )
