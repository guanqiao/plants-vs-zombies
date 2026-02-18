"""
阳光系统 - 处理阳光的生成和收集
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, SunProducerComponent, VelocityComponent
)


class SunSystem(System):
    """
    阳光系统
    
    管理阳光的自动生成和收集
    - 向日葵自动产生阳光
    - 天空掉落阳光
    - 玩家收集阳光
    """
    
    def __init__(self, priority: int = 45):
        super().__init__(priority)
        self.auto_sun_timer = 0.0
        self.auto_sun_interval = 10.0  # 每10秒自动产生阳光
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新阳光系统"""
        # 自动产生天空阳光
        self.auto_sun_timer += dt
        if self.auto_sun_timer >= self.auto_sun_interval:
            self.auto_sun_timer = 0
            # 实际产生阳光由游戏逻辑处理
        
        # 更新所有阳光生产组件
        sun_producers = component_manager.get_all_components(SunProducerComponent)
        
        for entity_id, sun_producer in sun_producers.items():
            if sun_producer.is_auto:
                if sun_producer.update(dt):
                    # 产生阳光
                    self._produce_sun(entity_id, sun_producer, component_manager)
            
            # 更新下落中的阳光位置
            if not sun_producer.is_auto:
                velocity = component_manager.get_component(entity_id, VelocityComponent)
                if velocity:
                    transform = component_manager.get_component(entity_id, TransformComponent)
                    if transform and transform.y <= 50:
                        # 阳光落地，停止下落
                        velocity.vy = 0
                        velocity.base_speed = 0
    
    def _produce_sun(self, entity_id: int, sun_producer: SunProducerComponent,
                     component_manager: ComponentManager) -> None:
        """产生阳光"""
        transform = component_manager.get_component(entity_id, TransformComponent)
        if not transform:
            return
        
        # 实际产生阳光由EntityFactory处理
        # 这里只是标记需要产生阳光
        pass
    
    def collect_sun(self, entity_id: int, component_manager: ComponentManager) -> int:
        """
        收集阳光
        
        Returns:
            收集到的阳光数量
        """
        sun_producer = component_manager.get_component(entity_id, SunProducerComponent)
        if sun_producer and sun_producer.is_collectable:
            amount = sun_producer.production_amount
            # 标记实体待销毁
            return amount
        return 0