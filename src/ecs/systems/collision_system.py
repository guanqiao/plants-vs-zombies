"""
碰撞系统 - 检测和处理实体间的碰撞

使用空间哈希网格优化碰撞检测性能，将O(n²)降低到O(n)
"""

from typing import Callable, List, Optional, Set
from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, CollisionComponent
from ...core.spatial_hash import SpatialHash, AABB


# 碰撞回调函数类型
CollisionCallback = Callable[[int, int], None]


class CollisionSystem(System):
    """
    碰撞系统
    
    使用空间哈希网格优化碰撞检测性能。
    将世界划分为固定大小的网格单元，只检测同一单元或邻近单元内的实体碰撞。
    
    Attributes:
        LAYER_PLANT: 植物碰撞层
        LAYER_ZOMBIE: 僵尸碰撞层
        LAYER_PROJECTILE: 投射物碰撞层
        LAYER_SUN: 阳光碰撞层
    """
    
    # 碰撞层定义
    LAYER_PLANT = 1
    LAYER_ZOMBIE = 2
    LAYER_PROJECTILE = 4
    LAYER_SUN = 8
    
    # 空间哈希网格单元大小（像素）
    CELL_SIZE = 100.0
    
    def __init__(self, priority: int = 20):
        """
        初始化碰撞系统
        
        Args:
            priority: 系统优先级，数字越小越早执行
        """
        super().__init__(priority)
        self._collision_callbacks: List[CollisionCallback] = []
        self._spatial_hash: SpatialHash = SpatialHash(cell_size=self.CELL_SIZE)
        self._checked_pairs: Set[tuple] = set()  # 避免重复检测
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        检测并处理碰撞
        
        使用空间哈希优化，只检测可能碰撞的实体对
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        # 清空上帧的检测记录
        self._checked_pairs.clear()
        
        # 更新空间哈希
        self._update_spatial_hash(component_manager)
        
        # 获取所有带碰撞组件的实体
        entities = component_manager.query(TransformComponent, CollisionComponent)
        
        # 使用空间哈希进行碰撞检测
        for entity_id in entities:
            self._check_entity_collisions(entity_id, component_manager)
    
    def _update_spatial_hash(self, component_manager: ComponentManager) -> None:
        """
        更新空间哈希网格
        
        清空并重新构建空间哈希，反映当前实体位置
        
        Args:
            component_manager: 组件管理器
        """
        self._spatial_hash.clear()
        
        entities = component_manager.query(TransformComponent, CollisionComponent)
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            collision = component_manager.get_component(entity_id, CollisionComponent)
            
            if transform and collision:
                # 创建AABB
                aabb = AABB(
                    x=transform.x - collision.width / 2,
                    y=transform.y - collision.height / 2,
                    width=collision.width,
                    height=collision.height
                )
                self._spatial_hash.insert(entity_id, aabb)
    
    def _check_entity_collisions(self, entity_id: int, 
                                  component_manager: ComponentManager) -> None:
        """
        检查指定实体与其他实体的碰撞
        
        使用空间哈希查询邻近实体，只检测可能碰撞的实体对
        
        Args:
            entity_id: 实体ID
            component_manager: 组件管理器
        """
        transform = component_manager.get_component(entity_id, TransformComponent)
        collision = component_manager.get_component(entity_id, CollisionComponent)
        
        if not transform or not collision:
            return
        
        # 使用空间哈希查询邻近实体
        # 查询范围基于碰撞盒大小
        query_radius = max(collision.width, collision.height) * 2
        nearby_entities = self._spatial_hash.get_nearby_entities(entity_id, query_radius)
        
        for other_id in nearby_entities:
            # 避免重复检测（确保每对只检测一次）
            pair = tuple(sorted([entity_id, other_id]))
            if pair in self._checked_pairs:
                continue
            
            self._checked_pairs.add(pair)
            
            # 执行详细碰撞检测
            if self._check_collision(entity_id, other_id, component_manager):
                self._handle_collision(entity_id, other_id)
    
    def _check_collision(self, entity1: int, entity2: int, 
                         component_manager: ComponentManager) -> bool:
        """
        检查两个实体是否碰撞
        
        执行详细的碰撞检测，包括碰撞层过滤和碰撞盒相交检测
        
        Args:
            entity1: 第一个实体ID
            entity2: 第二个实体ID
            component_manager: 组件管理器
            
        Returns:
            是否发生碰撞
        """
        transform1 = component_manager.get_component(entity1, TransformComponent)
        collision1 = component_manager.get_component(entity1, CollisionComponent)
        transform2 = component_manager.get_component(entity2, TransformComponent)
        collision2 = component_manager.get_component(entity2, CollisionComponent)
        
        if not all([transform1, collision1, transform2, collision2]):
            return False
        
        # 检查碰撞层
        if not collision1.can_collide_with(collision2.layer):
            return False
        
        # 检查碰撞盒相交
        return collision1.intersects(
            transform1.x, transform1.y,
            collision2,
            transform2.x, transform2.y
        )
    
    def _handle_collision(self, entity1: int, entity2: int) -> None:
        """
        处理碰撞事件
        
        触发所有注册的碰撞回调函数
        
        Args:
            entity1: 第一个碰撞实体ID
            entity2: 第二个碰撞实体ID
        """
        for callback in self._collision_callbacks:
            callback(entity1, entity2)
    
    def register_collision_callback(self, callback: CollisionCallback) -> None:
        """
        注册碰撞回调函数
        
        Args:
            callback: 回调函数，接收两个碰撞实体ID
        """
        self._collision_callbacks.append(callback)
    
    def unregister_collision_callback(self, callback: CollisionCallback) -> None:
        """
        注销碰撞回调函数
        
        Args:
            callback: 要注销的回调函数
        """
        if callback in self._collision_callbacks:
            self._collision_callbacks.remove(callback)
    
    def get_stats(self) -> dict:
        """
        获取碰撞系统统计信息
        
        Returns:
            统计信息字典，包含空间哈希状态和检测对数
        """
        return {
            'spatial_hash': self._spatial_hash.get_stats(),
            'checked_pairs': len(self._checked_pairs),
            'callbacks': len(self._collision_callbacks)
        }
