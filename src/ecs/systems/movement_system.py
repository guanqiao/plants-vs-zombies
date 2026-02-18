"""
移动系统 - 更新所有带VelocityComponent的实体位置
"""

from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, VelocityComponent


class MovementSystem(System):
    """
    移动系统
    
    根据速度更新所有实体的位置
    处理速度倍率（减速/加速效果）
    """
    
    def __init__(self, priority: int = 10):
        super().__init__(priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新所有实体的位置"""
        # 查询所有同时拥有Transform和Velocity组件的实体
        entities = component_manager.query(TransformComponent, VelocityComponent)
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            velocity = component_manager.get_component(entity_id, VelocityComponent)
            
            if transform and velocity:
                # 计算实际速度
                actual_speed = velocity.get_actual_speed()
                
                # 更新位置
                transform.x += velocity.vx * actual_speed * dt
                transform.y += velocity.vy * actual_speed * dt