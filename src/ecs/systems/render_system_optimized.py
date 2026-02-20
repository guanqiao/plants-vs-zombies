"""
渲染系统 - 优化版，使用SpriteList批量渲染

相比原版，优化点：
- 使用arcade.SpriteList进行批量渲染
- 添加脏标记机制，只在实体变化时重建SpriteList
- 缓存组件查询结果
- 减少每帧的Python循环开销
"""

import arcade
from typing import Dict, List, Optional, Tuple
from ..system import System
from ..component import ComponentManager
from ..components import TransformComponent, SpriteComponent
from ..components.animation_component import AnimationComponent
from ...core.logger import get_module_logger
from ...core.performance_monitor import log_draw_call


logger = get_module_logger(__name__)


class OptimizedRenderSystem(System):
    """
    优化的渲染系统
    
    使用SpriteList批量渲染，大幅提升性能
    """
    
    def __init__(self, priority: int = 100, three_d_effects=None):
        super().__init__(priority)
        self._three_d_effects = three_d_effects
        
        # 按z_index分层的SpriteList
        self._sprite_lists: Dict[int, arcade.SpriteList] = {}
        self._entity_sprites: Dict[int, arcade.Sprite] = {}
        
        # 脏标记
        self._needs_rebuild = True
        self._entity_version = 0
        
        # 缓存
        self._cached_entities: List[int] = []
        self._entity_components: Dict[int, Tuple] = {}
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新动画状态"""
        # 只更新有动画的实体
        for entity_id in self._cached_entities:
            anim_comp = component_manager.get_component(entity_id, AnimationComponent)
            if anim_comp:
                anim_comp.update(dt)
    
    def render(self, component_manager: ComponentManager) -> None:
        """执行批量渲染"""
        # 检查是否需要重建
        current_entities = set(component_manager.query(TransformComponent, SpriteComponent))
        
        if self._needs_rebuild or current_entities != set(self._cached_entities):
            self._rebuild_sprite_lists(component_manager)
            self._needs_rebuild = False
        
        # 更新所有精灵的位置和状态
        self._update_sprites(component_manager)
        
        # 批量渲染所有层
        for z_index in sorted(self._sprite_lists.keys()):
            sprite_list = self._sprite_lists[z_index]
            if len(sprite_list) > 0:
                sprite_list.draw()
                log_draw_call(1)  # 记录批量绘制调用
    
    def _rebuild_sprite_lists(self, component_manager: ComponentManager) -> None:
        """重建所有SpriteList"""
        # 清理旧的SpriteList
        for sprite_list in self._sprite_lists.values():
            sprite_list.clear()
        self._sprite_lists.clear()
        self._entity_sprites.clear()
        self._entity_components.clear()
        
        # 获取所有实体并排序
        entities = list(component_manager.query(TransformComponent, SpriteComponent))
        
        # 按z_index分组
        entities_by_z: Dict[int, List[int]] = {}
        for entity_id in entities:
            anim_comp = component_manager.get_component(entity_id, AnimationComponent)
            z_index = anim_comp.z_index if anim_comp else 0
            
            if z_index not in entities_by_z:
                entities_by_z[z_index] = []
            entities_by_z[z_index].append(entity_id)
        
        # 为每个z_index创建SpriteList
        for z_index, entity_list in entities_by_z.items():
            sprite_list = arcade.SpriteList()
            
            for entity_id in entity_list:
                transform = component_manager.get_component(entity_id, TransformComponent)
                sprite_comp = component_manager.get_component(entity_id, SpriteComponent)
                anim_comp = component_manager.get_component(entity_id, AnimationComponent)
                
                if transform and sprite_comp:
                    # 创建Arcade精灵
                    sprite = self._create_arcade_sprite(
                        entity_id, transform, sprite_comp, anim_comp
                    )
                    if sprite:
                        sprite_list.append(sprite)
                        self._entity_sprites[entity_id] = sprite
                        self._entity_components[entity_id] = (transform, sprite_comp, anim_comp)
            
            self._sprite_lists[z_index] = sprite_list
        
        self._cached_entities = entities
        logger.debug(f"重建SpriteList: {len(entities)} 个实体，{len(self._sprite_lists)} 个层级")
    
    def _create_arcade_sprite(self, entity_id: int,
                              transform: TransformComponent,
                              sprite_comp: SpriteComponent,
                              anim_comp: Optional[AnimationComponent]) -> Optional[arcade.Sprite]:
        """创建Arcade精灵"""
        try:
            # 如果有动画纹理，使用它
            if anim_comp:
                texture = anim_comp.get_current_texture()
                if texture:
                    sprite = arcade.Sprite()
                    sprite.texture = texture
                    sprite.center_x = transform.x
                    sprite.center_y = transform.y
                    sprite.width = sprite_comp.width
                    sprite.height = sprite_comp.height
                    sprite.alpha = sprite_comp.alpha
                    return sprite
            
            # 否则创建纯色精灵
            sprite = arcade.SpriteSolidColor(
                int(sprite_comp.width),
                int(sprite_comp.height),
                (*sprite_comp.color, sprite_comp.alpha)
            )
            sprite.center_x = transform.x
            sprite.center_y = transform.y
            return sprite
            
        except Exception as e:
            logger.error(f"创建精灵失败 (entity {entity_id}): {e}")
            return None
    
    def _update_sprites(self, component_manager: ComponentManager) -> None:
        """更新所有精灵的位置和状态"""
        for entity_id, (transform, sprite_comp, anim_comp) in self._entity_components.items():
            sprite = self._entity_sprites.get(entity_id)
            if not sprite:
                continue
            
            # 更新位置
            sprite.center_x = transform.x
            sprite.center_y = transform.y
            
            # 更新动画纹理
            if anim_comp:
                texture = anim_comp.get_current_texture()
                if texture and sprite.texture != texture:
                    sprite.texture = texture
                
                # 更新缩放
                if anim_comp.scale != 1.0:
                    sprite.scale = anim_comp.scale
            
            # 更新透明度
            sprite.alpha = sprite_comp.alpha
    
    def mark_dirty(self) -> None:
        """标记需要重建"""
        self._needs_rebuild = True
    
    def clear(self) -> None:
        """清理所有资源"""
        for sprite_list in self._sprite_lists.values():
            sprite_list.clear()
        self._sprite_lists.clear()
        self._entity_sprites.clear()
        self._entity_components.clear()
        self._cached_entities.clear()
