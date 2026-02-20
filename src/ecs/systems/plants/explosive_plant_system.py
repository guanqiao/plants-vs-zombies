"""
爆炸植物系统

处理爆炸类植物的行为：
- 樱桃炸弹：立即爆炸，范围伤害
- 土豆雷：延迟触发，武装后爆炸
"""

from typing import Dict, Set, TYPE_CHECKING
from .base_plant_system import BasePlantSystem
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent, ZombieComponent, HealthComponent
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class ExplosivePlantSystem(BasePlantSystem):
    """
    爆炸植物系统
    
    处理爆炸类植物的逻辑：
    - 樱桃炸弹立即爆炸
    - 土豆雷武装计时和触发
    
    Attributes:
        EXPLOSIVE_TYPES: 爆炸类植物类型集合
        EXPLOSION_RADIUS: 爆炸半径（像素）
        EXPLOSION_DAMAGE: 爆炸伤害
        POTATO_MINE_ARM_TIME: 土豆雷武装时间（秒）
    """
    
    EXPLOSIVE_TYPES = {PlantType.CHERRY_BOMB, PlantType.POTATO_MINE}
    EXPLOSION_RADIUS = 100.0
    EXPLOSION_DAMAGE = 1800
    POTATO_MINE_ARM_TIME = 15.0
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 41):
        """
        初始化爆炸植物系统
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(entity_factory, priority)
        # 土豆雷状态：实体ID -> 武装计时器
        self._potato_mine_states: Dict[int, float] = {}
        # 已武装的土豆雷
        self._armed_potato_mines: Set[int] = set()
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新爆炸植物状态
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        plants = self._get_plants_of_type(
            list(self.EXPLOSIVE_TYPES), component_manager
        )
        
        for plant_id in plants:
            plant = component_manager.get_component(plant_id, PlantComponent)
            
            if not plant:
                continue
            
            if plant.plant_type == PlantType.CHERRY_BOMB:
                self._handle_cherry_bomb(plant_id, component_manager)
            elif plant.plant_type == PlantType.POTATO_MINE:
                self._handle_potato_mine(plant_id, dt, component_manager)
    
    def _handle_cherry_bomb(self, plant_id: int,
                           component_manager: ComponentManager) -> None:
        """
        处理樱桃炸弹
        
        立即爆炸并销毁
        
        Args:
            plant_id: 植物实体ID
            component_manager: 组件管理器
        """
        transform = component_manager.get_component(plant_id, TransformComponent)
        
        if transform:
            self._explode(plant_id, transform.x, transform.y, 
                         self.EXPLOSION_RADIUS, self.EXPLOSION_DAMAGE,
                         component_manager)
    
    def _handle_potato_mine(self, plant_id: int, dt: float,
                           component_manager: ComponentManager) -> None:
        """
        处理土豆雷
        
        武装计时，武装后检测僵尸并爆炸
        
        Args:
            plant_id: 植物实体ID
            dt: 时间增量
            component_manager: 组件管理器
        """
        # 初始化状态
        if plant_id not in self._potato_mine_states:
            self._potato_mine_states[plant_id] = 0.0
        
        # 更新武装计时
        if plant_id not in self._armed_potato_mines:
            self._potato_mine_states[plant_id] += dt
            
            # 检查是否武装完成
            if self._potato_mine_states[plant_id] >= self.POTATO_MINE_ARM_TIME:
                self._armed_potato_mines.add(plant_id)
        
        # 已武装的土豆雷检测僵尸
        if plant_id in self._armed_potato_mines:
            transform = component_manager.get_component(plant_id, TransformComponent)
            grid_pos = component_manager.get_component(plant_id, GridPositionComponent)
            
            if transform and grid_pos:
                if self._check_zombie_trigger(transform, grid_pos, component_manager):
                    self._explode_potato_mine(plant_id, transform, component_manager)
    
    def _check_zombie_trigger(self, transform: TransformComponent,
                             grid_pos: GridPositionComponent,
                             component_manager: ComponentManager) -> bool:
        """
        检查是否有僵尸触发土豆雷
        
        Args:
            transform: 变换组件
            grid_pos: 网格位置组件
            component_manager: 组件管理器
            
        Returns:
            是否触发爆炸
        """
        zombies = component_manager.query(ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            
            if (zombie_grid and zombie_transform and 
                zombie_grid.row == grid_pos.row):
                # 检查僵尸是否在土豆雷格子上
                distance = abs(zombie_transform.x - transform.x)
                if distance < 40:  # 触发距离
                    return True
        
        return False
    
    def _explode_potato_mine(self, plant_id: int,
                            transform: TransformComponent,
                            component_manager: ComponentManager) -> None:
        """
        土豆雷爆炸
        
        Args:
            plant_id: 植物实体ID
            transform: 变换组件
            component_manager: 组件管理器
        """
        self._explode(plant_id, transform.x, transform.y,
                     self.EXPLOSION_RADIUS, self.EXPLOSION_DAMAGE,
                     component_manager)
        
        # 清理状态
        self._potato_mine_states.pop(plant_id, None)
        self._armed_potato_mines.discard(plant_id)
    
    def _explode(self, plant_id: int, x: float, y: float,
                radius: float, damage: int,
                component_manager: ComponentManager) -> None:
        """
        执行爆炸
        
        对范围内所有僵尸造成伤害
        
        Args:
            plant_id: 爆炸的植物实体ID
            x: 爆炸中心X坐标
            y: 爆炸中心Y坐标
            radius: 爆炸半径
            damage: 爆炸伤害
            component_manager: 组件管理器
        """
        zombies = component_manager.query(ZombieComponent, TransformComponent)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_health = component_manager.get_component(zombie_id, HealthComponent)
            
            if not zombie_transform or not zombie_health:
                continue
            
            # 计算距离
            distance = ((zombie_transform.x - x) ** 2 + 
                       (zombie_transform.y - y) ** 2) ** 0.5
            
            # 在爆炸范围内则造成伤害
            if distance <= radius:
                zombie_health.take_damage(damage)
        
        # 标记植物实体为死亡（实际销毁由外部系统处理）
        plant_health = component_manager.get_component(plant_id, HealthComponent)
        if plant_health:
            plant_health.take_damage(plant_health.current)
