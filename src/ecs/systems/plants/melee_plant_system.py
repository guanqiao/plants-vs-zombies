"""
近战植物系统

处理近战类植物的行为：
- 大嘴花：吞噬僵尸，需要时间咀嚼
- 地刺：对踩到的僵尸造成持续伤害
"""

from typing import Dict, Set, Optional, TYPE_CHECKING
from .base_plant_system import BasePlantSystem
from ...component import ComponentManager
from ...components import (
    PlantComponent, PlantType, TransformComponent,
    GridPositionComponent, ZombieComponent, HealthComponent
)

if TYPE_CHECKING:
    from ....arcade_game.entity_factory import EntityFactory


class MeleePlantSystem(BasePlantSystem):
    """
    近战植物系统
    
    处理近战类植物的攻击逻辑：
    - 大嘴花：吞噬僵尸，咀嚼状态管理
    - 地刺：接触伤害
    
    Attributes:
        MELEE_TYPES: 近战类植物类型集合
        CHOMPER_EAT_TIME: 大嘴花吞噬时间（秒）
        CHOMPER_CHEW_TIME: 大嘴花咀嚼时间（秒）
        SPIKEWEED_DAMAGE: 地刺伤害
        SPIKEWEED_DAMAGE_INTERVAL: 地刺伤害间隔（秒）
    """
    
    MELEE_TYPES = {PlantType.CHOMPER, PlantType.SPIKEWEED}
    CHOMPER_EAT_TIME = 0.5  # 吞噬动画时间
    CHOMPER_CHEW_TIME = 42.0  # 咀嚼时间
    SPIKEWEED_DAMAGE = 20
    SPIKEWEED_DAMAGE_INTERVAL = 0.5
    
    def __init__(self, entity_factory: 'EntityFactory', priority: int = 42):
        """
        初始化近战植物系统
        
        Args:
            entity_factory: 实体工厂实例
            priority: 系统优先级
        """
        super().__init__(entity_factory, priority)
        # 大嘴花状态：实体ID -> 状态（'idle', 'eating', 'chewing'）
        self._chomper_states: Dict[int, str] = {}
        # 大嘴花计时器：实体ID -> 计时器
        self._chomper_timers: Dict[int, float] = {}
        # 地刺上次伤害时间：实体ID -> 时间
        self._spikeweed_last_damage: Dict[int, float] = {}
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新近战植物状态
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        plants = self._get_plants_of_type(
            list(self.MELEE_TYPES), component_manager
        )
        
        for plant_id in plants:
            plant = component_manager.get_component(plant_id, PlantComponent)
            
            if not plant:
                continue
            
            if plant.plant_type == PlantType.CHOMPER:
                self._update_chomper(plant_id, dt, component_manager)
            elif plant.plant_type == PlantType.SPIKEWEED:
                self._update_spikeweed(plant_id, dt, component_manager)
    
    def _update_chomper(self, plant_id: int, dt: float,
                       component_manager: ComponentManager) -> None:
        """
        更新大嘴花状态
        
        管理大嘴花的吞噬和咀嚼状态
        
        Args:
            plant_id: 植物实体ID
            dt: 时间增量
            component_manager: 组件管理器
        """
        # 初始化状态
        if plant_id not in self._chomper_states:
            self._chomper_states[plant_id] = 'idle'
            self._chomper_timers[plant_id] = 0.0
        
        state = self._chomper_states[plant_id]
        
        if state == 'idle':
            # 空闲状态：尝试吞噬僵尸
            self._try_eat_zombie(plant_id, component_manager)
        elif state == 'eating':
            # 吞噬中：等待吞噬动画完成
            self._chomper_timers[plant_id] += dt
            if self._chomper_timers[plant_id] >= self.CHOMPER_EAT_TIME:
                self._chomper_states[plant_id] = 'chewing'
                self._chomper_timers[plant_id] = 0.0
        elif state == 'chewing':
            # 咀嚼中：等待咀嚼完成
            self._chomper_timers[plant_id] += dt
            if self._chomper_timers[plant_id] >= self.CHOMPER_CHEW_TIME:
                self._chomper_states[plant_id] = 'idle'
                self._chomper_timers[plant_id] = 0.0
    
    def _try_eat_zombie(self, plant_id: int,
                       component_manager: ComponentManager) -> None:
        """
        尝试让大嘴花吞噬僵尸
        
        Args:
            plant_id: 植物实体ID
            component_manager: 组件管理器
        """
        transform = component_manager.get_component(plant_id, TransformComponent)
        grid_pos = component_manager.get_component(plant_id, GridPositionComponent)
        
        if not transform or not grid_pos:
            return
        
        # 查找可以吞噬的僵尸
        zombie_id = self._find_eatable_zombie(
            grid_pos.row, transform.x, component_manager
        )
        
        if zombie_id:
            # 吞噬僵尸
            self._eat_zombie(zombie_id, component_manager)
            # 进入吞噬状态
            self._chomper_states[plant_id] = 'eating'
            self._chomper_timers[plant_id] = 0.0
    
    def _find_eatable_zombie(self, row: int, x: float,
                            component_manager: ComponentManager) -> Optional[int]:
        """
        查找可以被吞噬的僵尸
        
        大嘴花可以吞噬前方一格的僵尸
        
        Args:
            row: 植物所在行
            x: 植物X坐标
            component_manager: 组件管理器
            
        Returns:
            可吞噬的僵尸实体ID，如果没有则返回None
        """
        zombies = self._get_zombies_in_row(row, component_manager)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_health = component_manager.get_component(zombie_id, HealthComponent)
            
            if not zombie_transform or not zombie_health:
                continue
            
            # 检查僵尸是否在大嘴花前方一格范围内
            distance = zombie_transform.x - x
            if 0 < distance < 80:  # 前方一格范围
                return zombie_id
        
        return None
    
    def _eat_zombie(self, zombie_id: int,
                   component_manager: ComponentManager) -> None:
        """
        吞噬僵尸（立即击杀）
        
        Args:
            zombie_id: 僵尸实体ID
            component_manager: 组件管理器
        """
        zombie_health = component_manager.get_component(zombie_id, HealthComponent)
        
        if zombie_health:
            # 造成巨额伤害（即死）
            zombie_health.take_damage(9999)
    
    def _update_spikeweed(self, plant_id: int, dt: float,
                         component_manager: ComponentManager) -> None:
        """
        更新地刺状态
        
        对踩到的僵尸造成持续伤害
        
        Args:
            plant_id: 植物实体ID
            dt: 时间增量
            component_manager: 组件管理器
        """
        transform = component_manager.get_component(plant_id, TransformComponent)
        grid_pos = component_manager.get_component(plant_id, GridPositionComponent)
        
        if not transform or not grid_pos:
            return
        
        # 初始化上次伤害时间
        if plant_id not in self._spikeweed_last_damage:
            self._spikeweed_last_damage[plant_id] = 0.0
        
        # 检查是否应该造成伤害
        self._spikeweed_last_damage[plant_id] += dt
        
        if self._spikeweed_last_damage[plant_id] >= self.SPIKEWEED_DAMAGE_INTERVAL:
            # 检查是否有僵尸在地刺上
            if self._check_zombie_on_spikeweed(
                grid_pos.row, transform.x, component_manager
            ):
                self._damage_zombies_on_spikeweed(
                    grid_pos.row, transform.x, component_manager
                )
                self._spikeweed_last_damage[plant_id] = 0.0
    
    def _check_zombie_on_spikeweed(self, row: int, x: float,
                                  component_manager: ComponentManager) -> bool:
        """
        检查是否有僵尸在地刺上
        
        Args:
            row: 地刺所在行
            x: 地刺X坐标
            component_manager: 组件管理器
            
        Returns:
            是否有僵尸在地刺上
        """
        zombies = self._get_zombies_in_row(row, component_manager)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            
            if zombie_transform:
                # 检查僵尸是否在地刺格子上
                distance = abs(zombie_transform.x - x)
                if distance < 40:
                    return True
        
        return False
    
    def _damage_zombies_on_spikeweed(self, row: int, x: float,
                                    component_manager: ComponentManager) -> None:
        """
        对地刺上的所有僵尸造成伤害
        
        Args:
            row: 地刺所在行
            x: 地刺X坐标
            component_manager: 组件管理器
        """
        zombies = self._get_zombies_in_row(row, component_manager)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_health = component_manager.get_component(zombie_id, HealthComponent)
            
            if not zombie_transform or not zombie_health:
                continue
            
            # 检查僵尸是否在地刺上
            distance = abs(zombie_transform.x - x)
            if distance < 40:
                zombie_health.take_damage(self.SPIKEWEED_DAMAGE)
