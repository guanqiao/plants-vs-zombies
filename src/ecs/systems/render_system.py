"""
渲染系统 - 使用Arcade渲染所有带SpriteComponent的实体
"""

import arcade
from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, SpriteComponent
from ..components.animation_component import AnimationComponent


class RenderSystem(System):
    """
    渲染系统
    
    负责渲染所有拥有TransformComponent和SpriteComponent的实体
    支持精灵图和动画渲染
    """
    
    def __init__(self, priority: int = 100):
        super().__init__(priority)
        self._sprite_list = arcade.SpriteList()
        self._needs_rebuild = True
        self._last_entity_count = 0  # 用于检测实体数量变化
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新动画状态
        
        Args:
            dt: 时间增量
            component_manager: 组件管理器
        """
        # 更新所有动画组件
        entities = component_manager.query(TransformComponent, SpriteComponent, AnimationComponent)
        for entity_id in entities:
            anim_comp = component_manager.get_component(entity_id, AnimationComponent)
            if anim_comp:
                anim_comp.update(dt)
    
    def render(self, component_manager: ComponentManager) -> None:
        """
        执行渲染
        
        Args:
            component_manager: 组件管理器
        """
        # 获取所有需要渲染的实体并按z_index排序
        entities = self._get_sorted_entities(component_manager)
        
        # 调试输出（当实体数量变化时）
        current_count = len(entities)
        if current_count != self._last_entity_count:
            print(f"[RenderSystem] 实体数量: {current_count}")
            self._last_entity_count = current_count
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            sprite = component_manager.get_component(entity_id, SpriteComponent)
            anim_comp = component_manager.get_component(entity_id, AnimationComponent)
            
            if transform and sprite:
                self._draw_entity(transform, sprite, anim_comp)
    
    def _get_sorted_entities(self, component_manager: ComponentManager) -> list:
        """
        获取按z_index排序的实体列表
        
        Args:
            component_manager: 组件管理器
            
        Returns:
            排序后的实体ID列表
        """
        entities = list(component_manager.query(TransformComponent, SpriteComponent))
        
        # 按z_index排序
        def get_z_index(entity_id):
            anim_comp = component_manager.get_component(entity_id, AnimationComponent)
            if anim_comp:
                return anim_comp.z_index
            return 0
        
        return sorted(entities, key=get_z_index)
    
    def _draw_entity(self, transform: TransformComponent, 
                     sprite: SpriteComponent,
                     anim_comp: AnimationComponent = None) -> None:
        """
        绘制单个实体
        
        Args:
            transform: 变换组件
            sprite: 精灵组件
            anim_comp: 动画组件（可选）
        """
        # 如果有动画组件且当前有纹理，使用纹理渲染
        if anim_comp:
            texture = anim_comp.get_current_texture()
            if texture:
                try:
                    self._draw_textured_entity(transform, sprite, anim_comp, texture)
                    return
                except Exception as e:
                    print(f"[RenderSystem] 纹理渲染失败: {e}")
        
        # 如果有精灵图路径，尝试加载并渲染
        if sprite.sprite_path:
            # TODO: 从路径加载纹理
            pass
        
        # 否则使用纯色矩形渲染（回退方案）
        self._draw_colored_entity(transform, sprite)
    
    def _draw_textured_entity(self, transform: TransformComponent,
                              sprite: SpriteComponent,
                              anim_comp: AnimationComponent,
                              texture) -> None:
        """
        使用纹理绘制实体
        
        Args:
            transform: 变换组件
            sprite: 精灵组件
            anim_comp: 动画组件
            texture: 纹理对象
        """
        # 计算绘制参数
        x = transform.x
        y = transform.y
        scale = anim_comp.scale if anim_comp else 1.0
        width = sprite.width * scale
        height = sprite.height * scale
        
        # 绘制纹理
        try:
            arcade.draw_texture_rect(
                texture,
                arcade.XYWH(x, y, width, height),
                alpha=sprite.alpha
            )
        except Exception as e:
            print(f"[RenderSystem] draw_texture_rect 失败: {e}")
            # 回退到纯色渲染
            self._draw_colored_entity(transform, sprite)
    
    def _draw_colored_entity(self, transform: TransformComponent,
                             sprite: SpriteComponent) -> None:
        """
        使用纯色绘制实体（回退方案）
        
        Args:
            transform: 变换组件
            sprite: 精灵组件
        """
        # 计算矩形边界
        left = sprite.get_left(transform.x)
        right = sprite.get_right(transform.x)
        bottom = sprite.get_bottom(transform.y)
        top = sprite.get_top(transform.y)
        
        # 确保颜色可见（使用完全不透明）
        color_with_alpha = (*sprite.color, min(255, sprite.alpha))
        
        # 绘制填充矩形
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            color_with_alpha
        )
        
        # 绘制更明显的边框
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            (255, 255, 255, min(255, sprite.alpha)),  # 白色边框更明显
            3
        )
        
        # 绘制中心点标记，帮助调试定位
        arcade.draw_circle_filled(
            transform.x, transform.y,
            5,
            (255, 0, 0, min(255, sprite.alpha))  # 红色中心点
        )
