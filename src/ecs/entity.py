"""
实体模块 - ECS架构中的唯一标识

实体只是一个ID，本身不包含任何数据或逻辑
数据和逻辑由组件和系统提供
"""

from typing import Set, Dict, List


class Entity:
    """
    实体类
    
    实体是游戏对象的唯一标识符
    通过组合不同的组件来定义实体特性
    """
    
    _next_id = 0
    
    def __init__(self):
        self.id = Entity._next_id
        Entity._next_id += 1
        self._active = True
    
    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False
    
    def __hash__(self):
        return hash(self.id)
    
    def __repr__(self):
        return f"Entity({self.id})"
    
    @property
    def active(self) -> bool:
        """实体是否处于活动状态"""
        return self._active
    
    def destroy(self):
        """销毁实体"""
        self._active = False


class EntityManager:
    """
    实体管理器
    
    负责创建、销毁和管理所有实体
    """
    
    def __init__(self):
        self._entities: Dict[int, Entity] = {}
        self._entities_to_remove: Set[int] = set()
    
    def create_entity(self) -> Entity:
        """创建新实体"""
        entity = Entity()
        self._entities[entity.id] = entity
        return entity
    
    def get_entity(self, entity_id: int) -> Entity:
        """获取指定ID的实体"""
        return self._entities.get(entity_id)
    
    def destroy_entity(self, entity_id: int) -> None:
        """标记实体为待销毁"""
        self._entities_to_remove.add(entity_id)
        if entity_id in self._entities:
            self._entities[entity_id].destroy()
    
    def process_pending_removals(self, component_manager) -> None:
        """处理待销毁的实体"""
        for entity_id in self._entities_to_remove:
            if entity_id in self._entities:
                # 移除实体的所有组件
                component_manager.remove_all_components(entity_id)
                del self._entities[entity_id]
        self._entities_to_remove.clear()
    
    def get_all_entities(self) -> List[Entity]:
        """获取所有活动实体"""
        return [entity for entity in self._entities.values() if entity.active]
    
    def clear(self) -> None:
        """清空所有实体"""
        self._entities.clear()
        self._entities_to_remove.clear()
        Entity._next_id = 0