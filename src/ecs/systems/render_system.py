"""
渲染系统 - 使用Arcade渲染所有带SpriteComponent的实体
"""

import arcade
from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, SpriteComponent


class RenderSystem(System):
    """
    渲染系统
    
    负责渲染所有拥有TransformComponent和SpriteComponent的实体
    使用Arcade的shape_list进行批量渲染优化
    """
    
    def __init__(self, priority: int = 100):
        super().__init__(priority)
        self.shape_list = None
        self.needs_rebuild = True
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        渲染所有实体
        
        注意：在Arcade中，渲染通常在on_draw中调用，
        这里我们提供render方法供GameWindow调用
        """
        pass
    
    def render(self, component_manager: ComponentManager) -> None:
        """执行渲染"""
        # 获取所有需要渲染的实体
        entities = component_manager.query(TransformComponent, SpriteComponent)
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            sprite = component_manager.get_component(entity_id, SpriteComponent)
            
            if transform and sprite:
                self._draw_entity(transform, sprite)
    
    def _draw_entity(self, transform: TransformComponent, sprite: SpriteComponent) -> None:
        """绘制单个实体"""
        # 计算矩形边界
        left = sprite.get_left(transform.x)
        right = sprite.get_right(transform.x)
        bottom = sprite.get_bottom(transform.y)
        top = sprite.get_top(transform.y)
        
        # 绘制填充矩形
        arcade.draw_lrtb_rectangle_filled(
            left, right, top, bottom,
            sprite.color
        )
        
        # 绘制边框
        arcade.draw_lrtb_rectangle_outline(
            left, right, top, bottom,
            (0, 0, 0),
            2
        )