"""
投手植物系统

处理投手类植物的行为：
- 西瓜投手：抛物线攻击，溅射伤害
- 冰西瓜：冰冻效果+溅射伤害
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


class LobberPlantSystem(BasePlantSystem):
    """
    投手植物系统
    
    处理投手类植物的攻击逻辑：
    - 西瓜投手：抛物线投射物，溅射伤害
    - 冰西瓜：冰冻效果+溅射
    
    Attributes:
        LOBBER_TYPES: 投手类植物类型集合
        ATTACK_RANGE: 攻击范围（像素）
        FIRE_RATE: 射击间隔（秒）
    """
    
    LOBBER_TYPES = {PlantType.MELON_PULT, PlantType.WINTER_MELON}
    ATTACK_RANGE = 800.0
    FIRE_RATE = 3.0
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 43):
        """
        初始化投手植物系统
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(entity_factory, priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新投手植物状态
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        plants = self._get_plants_of_type(
            list(self.LOBBER_TYPES), component_manager
        )
        
        for plant_id in plants:
            self._update_plant(plant_id, dt, component_manager)
    
    def _update_plant(self, plant_id: int, dt: float,
                     component_manager: ComponentManager) -> None:
        """
        更新单个投手植物
        
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
        
        # 查找目标僵尸
        target = self._find_target(grid_pos.row, transform.x, component_manager)
        
        if target:
            self._shoot(plant_id, plant, transform, grid_pos, target, component_manager)
            plant.start_attack()
    
    def _find_target(self, row: int, x: float,
                    component_manager: ComponentManager) -> int:
        """
        查找目标僵尸
        
        投手类植物攻击最近的僵尸
        
        Args:
            row: 植物所在行
            x: 植物X坐标
            component_manager: 组件管理器
            
        Returns:
            目标僵尸实体ID，如果没有则返回None
        """
        return self._get_closest_zombie_in_row(row, x, component_manager)
    
    def _shoot(self, plant_id: int, plant: PlantComponent,
              transform: TransformComponent,
              grid_pos: GridPositionComponent,
              target_id: int,
              component_manager: ComponentManager) -> None:
        """
        发射投射物
        
        Args:
            plant_id: 植物实体ID
            plant: 植物组件
            transform: 变换组件
            grid_pos: 网格位置组件
            target_id: 目标僵尸ID
            component_manager: 组件管理器
        """
        plant_type = plant.plant_type
        
        if plant_type == PlantType.WINTER_MELON:
            self._shoot_winter_melon(transform, grid_pos, target_id)
        else:  # MELON_PULT
            self._shoot_melon(transform, grid_pos, target_id)
    
    def _shoot_melon(self, transform: TransformComponent,
                    grid_pos: GridPositionComponent,
                    target_id: int) -> None:
        """
        西瓜投手发射
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
            target_id: 目标僵尸ID
        """
        self.entity_factory.create_projectile(
            ProjectileType.MELON,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
    
    def _shoot_winter_melon(self, transform: TransformComponent,
                           grid_pos: GridPositionComponent,
                           target_id: int) -> None:
        """
        冰西瓜发射
        
        发射冰冻西瓜，带减速效果
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
            target_id: 目标僵尸ID
        """
        self.entity_factory.create_projectile(
            ProjectileType.WINTER_MELON,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
