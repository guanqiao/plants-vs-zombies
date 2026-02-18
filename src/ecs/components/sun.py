"""
阳光相关组件
"""

from dataclasses import dataclass


@dataclass
class SunProducerComponent:
    """
    阳光生产组件
    
    存储产生阳光的属性
    
    Attributes:
        production_amount: 每次产生的阳光数量
        production_interval: 产生间隔（秒）
        timer: 当前计时器
        is_auto: 是否自动产生（如向日葵）
        is_collectable: 是否可以被收集
        fall_speed: 下落速度（像素/秒）
        lifetime: 阳光停留时间（秒），0表示永久
    """
    production_amount: int = 25
    production_interval: float = 5.0
    timer: float = 0.0
    is_auto: bool = True
    is_collectable: bool = True
    fall_speed: float = 50.0
    lifetime: float = 0.0  # 0表示永久停留
    
    def update(self, dt: float) -> bool:
        """
        更新计时器
        
        Returns:
            是否应该产生阳光
        """
        if not self.is_auto:
            return False
        
        self.timer += dt
        if self.timer >= self.production_interval:
            self.timer = 0
            return True
        return False
    
    def produce(self) -> int:
        """
        产生阳光
        
        Returns:
            产生的阳光数量
        """
        return self.production_amount
    
    def update_lifetime(self, dt: float) -> bool:
        """
        更新生命周期
        
        Returns:
            是否仍然存活（False表示应该被移除）
        """
        if self.lifetime <= 0:
            return True  # 永久停留
        
        self.lifetime -= dt
        return self.lifetime > 0