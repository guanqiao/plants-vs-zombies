"""
碰撞系统 - 检测和处理实体间的碰撞
"""

from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, CollisionComponent


class CollisionSystem(System):
    """
    碰撞系统
    
    检测实体间的碰撞并触发相应事件
    支持碰撞层过滤
    """
    
    # 碰撞层定义
    LAYER_PLANT = 1
    LAYER_ZOMBIE = 2
    LAYER_PROJECTILE = 4
    LAYER_SUN = 8
    
    def __init__(self, priority: int = 20):
        super().__init__(priority)
        self.collision_callbacks = []
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """检测并处理碰撞"""
        # 获取所有带碰撞组件的实体
        entities = component_manager.query(TransformComponent, CollisionComponent)
        
        # 简单的O(n²)碰撞检测
        # 对于大量实体，建议使用空间分割优化
        entity_list = list(entities)
        
        for i in range(len(entity_list)):
            for j in range(i + 1, len(entity_list)):
                entity1 = entity_list[i]
                entity2 = entity_list[j]
                
                if self._check_collision(entity1, entity2, component_manager):
                    self._handle_collision(entity1, entity2)
    
    def _check_collision(self, entity1: int, entity2: int, 
                         component_manager: ComponentManager) -> bool:
        """检查两个实体是否碰撞"""
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
        """处理碰撞事件"""
        # 触发所有注册的回调
        for callback in self.collision_callbacks:
            callback(entity1, entity2)
    
    def register_collision_callback(self, callback) -> None:
        """注册碰撞回调函数"""
        self.collision_callbacks.append(callback)
    
    def unregister_collision_callback(self, callback) -> None:
        """注销碰撞回调函数"""
        if callback in self.collision_callbacks:
            self.collision_callbacks.remove(callback)