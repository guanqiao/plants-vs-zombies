"""
生命值系统 - 管理实体生命状态
"""

from ..system import System
from ..component import ComponentManager
from ..components import HealthComponent


class HealthSystem(System):
    """
    生命值系统
    
    管理所有实体的生命值状态
    处理死亡实体的清理
    """
    
    def __init__(self, priority: int = 30):
        super().__init__(priority)
        self.on_death_callbacks = []
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新生命值状态"""
        # 获取所有带生命值组件的实体
        health_components = component_manager.get_all_components(HealthComponent)
        
        for entity_id, health in health_components.items():
            if health.is_dead:
                self._handle_death(entity_id, component_manager)
    
    def _handle_death(self, entity_id: int, component_manager: ComponentManager) -> None:
        """处理实体死亡"""
        # 触发死亡回调
        for callback in self.on_death_callbacks:
            callback(entity_id)
    
    def register_death_callback(self, callback) -> None:
        """注册死亡回调函数"""
        self.on_death_callbacks.append(callback)
    
    def unregister_death_callback(self, callback) -> None:
        """注销死亡回调函数"""
        if callback in self.on_death_callbacks:
            self.on_death_callbacks.remove(callback)
    
    def deal_damage(self, entity_id: int, damage: int, 
                    component_manager: ComponentManager) -> bool:
        """
        对实体造成伤害
        
        Returns:
            实体是否死亡
        """
        health = component_manager.get_component(entity_id, HealthComponent)
        if health and not health.is_dead:
            health.take_damage(damage)
            return health.is_dead
        return False