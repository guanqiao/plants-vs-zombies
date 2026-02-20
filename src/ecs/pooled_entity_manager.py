"""
使用对象池的实体管理器 - 优化实体创建和销毁性能
"""
from typing import Set, List
from .entity_pool import EntityPool
from .component import ComponentManager


class PooledEntityManager:
    """
    使用对象池的实体管理器
    
    相比普通EntityManager，使用对象池重用实体ID，减少内存分配
    """
    
    def __init__(self, pool_size: int = 100, component_manager: ComponentManager = None):
        """
        初始化实体管理器
        
        Args:
            pool_size: 对象池初始大小
            component_manager: 组件管理器（可选）
        """
        self._pool = EntityPool(initial_size=pool_size)
        self._component_manager = component_manager
        # 待销毁的实体列表
        self._entities_to_remove: Set[int] = set()
    
    def create_entity(self) -> int:
        """
        创建新实体
        
        Returns:
            新实体的ID
        """
        return self._pool.acquire()
    
    def destroy_entity(self, entity_id: int) -> None:
        """
        标记实体为待销毁
        
        Args:
            entity_id: 要销毁的实体ID
        """
        if self._pool.is_active(entity_id):
            self._entities_to_remove.add(entity_id)
    
    def process_pending_removals(self) -> None:
        """处理所有待销毁的实体"""
        for entity_id in self._entities_to_remove:
            # 移除所有组件
            if self._component_manager:
                self._component_manager.remove_all_components(entity_id)
            # 释放实体ID回池中
            self._pool.release(entity_id)
        
        self._entities_to_remove.clear()
    
    def is_valid_entity(self, entity_id: int) -> bool:
        """
        检查实体ID是否有效
        
        Args:
            entity_id: 实体ID
            
        Returns:
            True if 有效且活跃
        """
        return self._pool.is_active(entity_id)
    
    def get_all_entities(self) -> Set[int]:
        """
        获取所有活跃的实体
        
        Returns:
            活跃实体ID集合
        """
        return self._pool.get_active_ids()
    
    def get_active_count(self) -> int:
        """
        获取活跃实体数量
        
        Returns:
            活跃实体数
        """
        return self._pool.get_active_count()
    
    def clear(self) -> None:
        """清空所有实体"""
        # 移除所有组件
        if self._component_manager:
            for entity_id in self._pool.get_active_ids():
                self._component_manager.remove_all_components(entity_id)
        
        self._entities_to_remove.clear()
        self._pool.clear()
    
    def set_component_manager(self, component_manager: ComponentManager) -> None:
        """
        设置组件管理器
        
        Args:
            component_manager: 组件管理器实例
        """
        self._component_manager = component_manager
