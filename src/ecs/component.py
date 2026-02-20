"""
组件模块 - ECS架构的核心数据单元

组件是纯数据容器，不包含任何逻辑
"""

from dataclasses import dataclass, field
from typing import Dict, List, Type, TypeVar, Generic, Any, Set, Tuple
from enum import Enum, auto


class Component:
    """组件基类"""
    pass


T = TypeVar('T', bound=Component)


class ComponentManager:
    """
    组件管理器
    
    负责存储和管理所有组件实例
    使用类型索引实现O(1)的组件查询
    支持查询结果缓存，提升性能
    """
    
    def __init__(self):
        # _components[component_type][entity_id] = component_instance
        self._components: Dict[Type[Component], Dict[int, Component]] = {}
        # _entity_components[entity_id] = {component_type, ...}
        self._entity_components: Dict[int, set] = {}
        
        # 查询缓存
        # _query_cache[(component_type1, component_type2, ...)] = {entity_id, ...}
        self._query_cache: Dict[Tuple[Type[Component], ...], Set[int]] = {}
        # 缓存版本号，用于使缓存失效
        self._cache_version = 0
    
    def add_component(self, entity_id: int, component: Component) -> None:
        """为实体添加组件"""
        component_type = type(component)
        
        if component_type not in self._components:
            self._components[component_type] = {}
        
        self._components[component_type][entity_id] = component
        
        if entity_id not in self._entity_components:
            self._entity_components[entity_id] = set()
        self._entity_components[entity_id].add(component_type)
        
        # 使缓存失效（组件变化可能影响查询结果）
        self._invalidate_cache()
    
    def remove_component(self, entity_id: int, component_type: Type[T]) -> None:
        """从实体移除组件"""
        if component_type in self._components:
            self._components[component_type].pop(entity_id, None)
        
        if entity_id in self._entity_components:
            self._entity_components[entity_id].discard(component_type)
        
        # 使缓存失效
        self._invalidate_cache()
    
    def get_component(self, entity_id: int, component_type: Type[T]) -> T:
        """获取实体的指定类型组件"""
        if component_type in self._components:
            return self._components[component_type].get(entity_id)
        return None
    
    def has_component(self, entity_id: int, component_type: Type[Component]) -> bool:
        """检查实体是否有指定类型组件"""
        if entity_id in self._entity_components:
            return component_type in self._entity_components[entity_id]
        return False
    
    def get_all_components(self, component_type: Type[T]) -> Dict[int, T]:
        """获取所有指定类型的组件"""
        return self._components.get(component_type, {})
    
    def remove_all_components(self, entity_id: int) -> None:
        """移除实体的所有组件"""
        if entity_id in self._entity_components:
            for component_type in self._entity_components[entity_id]:
                if component_type in self._components:
                    self._components[component_type].pop(entity_id, None)
            del self._entity_components[entity_id]
            # 使缓存失效
            self._invalidate_cache()
    
    def query(self, *component_types: Type[Component]) -> List[int]:
        """
        查询拥有所有指定组件类型的实体
        
        使用缓存机制提升性能，相同的查询会返回缓存结果
        
        Args:
            *component_types: 组件类型列表
            
        Returns:
            符合条件的实体ID列表
        """
        if not component_types:
            return []
        
        # 检查缓存
        cache_key = component_types
        if cache_key in self._query_cache:
            return list(self._query_cache[cache_key])
        
        # 执行查询
        result = self._perform_query(*component_types)
        
        # 缓存结果
        self._query_cache[cache_key] = result
        
        return list(result)
    
    def _perform_query(self, *component_types: Type[Component]) -> Set[int]:
        """
        执行实际的查询操作
        
        Args:
            *component_types: 组件类型列表
            
        Returns:
            符合条件的实体ID集合
        """
        # 从第一个组件类型开始
        first_type = component_types[0]
        if first_type not in self._components:
            return set()
        
        entities = set(self._components[first_type].keys())
        
        # 与其他组件类型取交集
        for component_type in component_types[1:]:
            if component_type not in self._components:
                return set()
            entities &= set(self._components[component_type].keys())
        
        return entities
    
    def _invalidate_cache(self) -> None:
        """使所有查询缓存失效"""
        self._query_cache.clear()
        self._cache_version += 1

    def clear(self) -> None:
        """清空所有组件数据"""
        self._components.clear()
        self._entity_components.clear()
        self._query_cache.clear()
        self._cache_version += 1