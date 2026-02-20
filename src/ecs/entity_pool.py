"""
实体对象池 - 优化实体ID分配和重用
"""
from typing import Set, List


class EntityPool:
    """
    实体对象池
    
    管理实体ID的分配和重用，避免频繁的内存分配和释放
    """
    
    def __init__(self, initial_size: int = 100):
        """
        初始化实体池
        
        Args:
            initial_size: 初始池大小
        """
        self._initial_size = initial_size
        # 可用的实体ID列表
        self._available_ids: List[int] = list(range(initial_size))
        # 活跃的实体ID集合
        self._active_ids: Set[int] = set()
        # 下一个新ID的计数器
        self._next_id = initial_size
    
    def acquire(self) -> int:
        """
        从池中获取一个实体ID
        
        Returns:
            实体ID
        """
        if self._available_ids:
            # 重用现有的ID
            entity_id = self._available_ids.pop()
        else:
            # 池已空，创建新ID
            entity_id = self._next_id
            self._next_id += 1
        
        # 标记为活跃
        self._active_ids.add(entity_id)
        
        return entity_id
    
    def release(self, entity_id: int) -> None:
        """
        释放实体ID回池中
        
        Args:
            entity_id: 要释放的实体ID
        """
        if entity_id in self._active_ids:
            self._active_ids.remove(entity_id)
            # 将ID放回可用列表
            self._available_ids.append(entity_id)
    
    def is_active(self, entity_id: int) -> bool:
        """
        检查实体ID是否处于活跃状态
        
        Args:
            entity_id: 实体ID
            
        Returns:
            True if 活跃
        """
        return entity_id in self._active_ids
    
    def get_active_count(self) -> int:
        """
        获取当前活跃实体数量
        
        Returns:
            活跃实体数
        """
        return len(self._active_ids)
    
    def get_available_count(self) -> int:
        """
        获取可用实体ID数量
        
        Returns:
            可用ID数
        """
        return len(self._available_ids)
    
    def get_total_count(self) -> int:
        """
        获取总共创建的实体ID数量
        
        Returns:
            总ID数（活跃 + 可用）
        """
        return len(self._active_ids) + len(self._available_ids)
    
    def clear(self) -> None:
        """清空池，重置所有状态"""
        self._available_ids = list(range(self._initial_size))
        self._active_ids.clear()
        self._next_id = self._initial_size
    
    def get_active_ids(self) -> Set[int]:
        """
        获取所有活跃的实体ID
        
        Returns:
            活跃ID集合
        """
        return self._active_ids.copy()
