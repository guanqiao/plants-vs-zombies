"""
冷却系统 - 更新所有冷却组件
"""
from typing import TYPE_CHECKING

from src.ecs.system import System
from src.ecs.components.cooldown import CooldownComponent

if TYPE_CHECKING:
    from src.ecs.component import ComponentManager


class CooldownSystem(System):
    """
    冷却系统 - 管理游戏中所有冷却组件的更新
    
    每帧更新所有激活的冷却组件，减少剩余冷却时间
    """
    
    def __init__(self, priority: int = 50):
        """
        初始化冷却系统
        
        Args:
            priority: 系统优先级，默认50
        """
        super().__init__(priority)
    
    def update(self, dt: float, component_manager: 'ComponentManager'):
        """
        更新所有冷却组件
        
        Args:
            dt: 时间增量（秒）
            component_manager: 组件管理器
        """
        # 获取所有带冷却组件的实体
        entities = component_manager.query(CooldownComponent)
        
        for entity in entities:
            cooldown = component_manager.get_component(entity, CooldownComponent)
            if cooldown:
                cooldown.update(dt)
