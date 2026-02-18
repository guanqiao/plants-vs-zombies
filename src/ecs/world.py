"""
世界模块 - ECS架构的核心管理器

世界管理器协调实体、组件和系统
提供统一的接口来操作ECS世界
"""

from typing import List, Type, TypeVar
from .entity import Entity, EntityManager
from .component import Component, ComponentManager
from .system import System, SystemManager


T = TypeVar('T', bound=Component)


class World:
    """
    ECS世界管理器
    
    作为ECS架构的入口点，提供统一的API来：
    - 创建和销毁实体
    - 添加和移除组件
    - 注册和执行系统
    - 更新游戏世界
    """
    
    def __init__(self):
        self._entity_manager = EntityManager()
        self._component_manager = ComponentManager()
        self._system_manager = SystemManager()
        self._system_manager.set_component_manager(self._component_manager)
    
    # 实体操作
    def create_entity(self) -> Entity:
        """创建新实体"""
        return self._entity_manager.create_entity()
    
    def destroy_entity(self, entity: Entity) -> None:
        """销毁实体"""
        self._entity_manager.destroy_entity(entity.id)
    
    def get_entity(self, entity_id: int) -> Entity:
        """获取指定ID的实体"""
        return self._entity_manager.get_entity(entity_id)
    
    # 组件操作
    def add_component(self, entity: Entity, component: Component) -> None:
        """为实体添加组件"""
        self._component_manager.add_component(entity.id, component)
    
    def remove_component(self, entity: Entity, component_type: Type[T]) -> None:
        """从实体移除组件"""
        self._component_manager.remove_component(entity.id, component_type)
    
    def get_component(self, entity: Entity, component_type: Type[T]) -> T:
        """获取实体的指定类型组件"""
        return self._component_manager.get_component(entity.id, component_type)
    
    def has_component(self, entity: Entity, component_type: Type[Component]) -> bool:
        """检查实体是否有指定类型组件"""
        return self._component_manager.has_component(entity.id, component_type)
    
    def query_components(self, component_type: Type[T]) -> dict:
        """查询所有指定类型的组件"""
        return self._component_manager.get_all_components(component_type)
    
    def query_entities(self, *component_types: Type[Component]) -> List[int]:
        """查询拥有所有指定组件类型的实体ID"""
        return self._component_manager.query(*component_types)
    
    # 系统操作
    def add_system(self, system: System) -> None:
        """添加系统"""
        self._system_manager.add_system(system)
    
    def remove_system(self, system: System) -> None:
        """移除系统"""
        self._system_manager.remove_system(system)
    
    # 世界更新
    def update(self, dt: float) -> None:
        """
        更新世界
        
        Args:
            dt: 时间增量（秒）
        """
        # 更新所有系统
        self._system_manager.update(dt)
        
        # 处理待销毁的实体
        self._entity_manager.process_pending_removals(self._component_manager)
    
    def clear(self) -> None:
        """清空整个世界"""
        self._system_manager.clear()
        self._entity_manager.clear()