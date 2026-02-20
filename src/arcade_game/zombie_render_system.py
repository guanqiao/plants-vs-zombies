"""
僵尸渲染系统 - 集成所有僵尸视觉效果

包括：
- 程序化动画渲染
- 视觉效果（受击、死亡）
- 特殊僵尸效果
"""

import arcade
from typing import Optional, Tuple
from ..ecs.system import System
from ..ecs.component import ComponentManager
from ..ecs.components import TransformComponent, SpriteComponent, ZombieComponent
from ..ecs.components.zombie import ZombieType, ZombieTypeComponent
from ..ecs.components.animation_component import AnimationComponent
from ..ecs.components.health import HealthComponent
from .zombie_animation_renderer import ZombieAnimationRenderer, ZombieBodyPart
from .zombie_visual_system import ZombieVisualSystem, DeathType
from .special_zombie_effects import SpecialZombieEffects
from ..core.logger import get_module_logger


logger = get_module_logger(__name__)


class ZombieRenderSystem(System):
    """
    僵尸渲染系统
    
    负责渲染所有僵尸实体，集成：
    - 程序化行走动画
    - 受击视觉效果
    - 特殊僵尸效果
    """
    
    def __init__(self, priority: int = 95):
        super().__init__(priority)
        self._anim_renderer = ZombieAnimationRenderer()
        self._visual_system = ZombieVisualSystem()
        self._special_effects = SpecialZombieEffects()
        self._time = 0.0
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新所有僵尸动画和效果"""
        self._time += dt
        
        # 更新视觉效果系统
        self._visual_system.update(dt)
        
        # 更新特殊效果
        self._special_effects.update(dt)
        
        # 获取所有僵尸实体
        zombies = component_manager.query(
            TransformComponent, SpriteComponent, ZombieComponent
        )
        
        for zombie_id in zombies:
            transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie = component_manager.get_component(zombie_id, ZombieComponent)
            anim_comp = component_manager.get_component(zombie_id, AnimationComponent)
            
            if not transform or not zombie:
                continue
            
            # 判断是否移动
            is_moving = not zombie.is_attacking
            is_attacking = zombie.is_attacking
            
            # 更新程序化动画
            self._anim_renderer.update(
                dt, zombie_id, is_moving, is_attacking, 
                is_hurt=self._visual_system.get_hit_flash_intensity(zombie_id) > 0
            )
            
            # 更新特殊僵尸效果
            self._update_special_effects(zombie_id, transform, zombie, dt, component_manager)
    
    def _update_special_effects(self, zombie_id: int, transform, zombie, 
                                dt: float, component_manager: ComponentManager) -> None:
        """更新特殊僵尸效果"""
        zombie_type_comp = component_manager.get_component(zombie_id, ZombieTypeComponent)
        if not zombie_type_comp:
            return
        
        zombie_type = zombie_type_comp.zombie_type
        
        # 气球僵尸漂浮
        if zombie_type == ZombieType.BALLOON:
            offset = self._special_effects.get_balloon_offset(zombie_id, dt)
            # 这里可以修改transform.y，但需要在渲染时应用
        
        # 跳跳僵尸弹跳
        if zombie_type == ZombieType.POGO:
            offset, compression = self._special_effects.get_pogo_offset(zombie_id, dt)
        
        # 矿工僵尸挖掘
        if zombie_type == ZombieType.MINER:
            self._special_effects.update_miner_dig(zombie_id, dt, transform.x, transform.y)
        
        # 撑杆僵尸跳跃
        if zombie_type == ZombieType.POLE_VAULTER and zombie.has_pole:
            if self._special_effects.is_pole_vaulting(zombie_id):
                new_x, new_y, completed = self._special_effects.update_pole_vault(zombie_id, dt)
                if not completed:
                    transform.x = new_x
                    transform.y = new_y
    
    def render(self, component_manager: ComponentManager) -> None:
        """渲染所有僵尸"""
        # 先渲染死亡动画
        self._visual_system.render()
        
        # 获取所有僵尸实体
        zombies = component_manager.query(
            TransformComponent, SpriteComponent, ZombieComponent
        )
        
        for zombie_id in zombies:
            self._render_zombie(zombie_id, component_manager)
    
    def _render_zombie(self, zombie_id: int, component_manager: ComponentManager) -> None:
        """渲染单个僵尸"""
        transform = component_manager.get_component(zombie_id, TransformComponent)
        sprite = component_manager.get_component(zombie_id, SpriteComponent)
        zombie = component_manager.get_component(zombie_id, ZombieComponent)
        anim_comp = component_manager.get_component(zombie_id, AnimationComponent)
        zombie_type_comp = component_manager.get_component(zombie_id, ZombieTypeComponent)
        
        if not transform or not sprite or not zombie:
            return
        
        # 获取基础颜色
        base_color = sprite.color
        
        # 应用受击闪烁
        render_color = self._visual_system.apply_hit_flash_to_color(zombie_id, base_color)
        
        # 获取渲染偏移（震动效果）
        offset_x, offset_y = self._visual_system.get_render_offset(zombie_id)
        
        # 获取脉冲缩放
        pulse_scale = self._visual_system.get_hit_pulse_scale(zombie_id)
        
        # 计算最终位置
        final_x = transform.x + offset_x
        final_y = transform.y + offset_y
        
        # 应用特殊僵尸的Y轴偏移
        if zombie_type_comp:
            if zombie_type_comp.zombie_type == ZombieType.BALLOON:
                balloon_offset = self._special_effects.get_balloon_offset(0, 0)
                final_y += balloon_offset
            elif zombie_type_comp.zombie_type == ZombieType.POGO:
                pogo_offset, _ = self._special_effects.get_pogo_offset(0, 0)
                final_y += pogo_offset
        
        # 获取部位脱落状态
        visual_state = self._visual_system.get_or_create_state(zombie_id)
        
        # 使用程序化动画渲染器渲染僵尸
        self._anim_renderer.render(
            zombie_id, final_x, final_y,
            render_color,
            sprite.width * pulse_scale,
            sprite.height * pulse_scale,
            is_flipped_x=anim_comp.is_flipped_x if anim_comp else True
        )
        
        # 渲染特殊僵尸效果
        self._render_special_effects(zombie_id, final_x, final_y, sprite.height, 
                                     zombie_type_comp, zombie)
        
        # 渲染血液粒子
        self._visual_system.render_blood_particles(zombie_id, final_x, final_y)
        
        # 渲染护甲（如果破碎）
        if zombie.has_armor and visual_state.armor_broken:
            armor_type = self._get_armor_type(zombie_type_comp)
            self._visual_system.render_flying_armor(zombie_id, final_x, final_y, armor_type)
    
    def _render_special_effects(self, zombie_id: int, x: float, y: float, 
                                height: float, zombie_type_comp, zombie) -> None:
        """渲染特殊僵尸效果"""
        if not zombie_type_comp:
            return
        
        zombie_type = zombie_type_comp.zombie_type
        
        # 撑杆僵尸渲染撑杆
        if zombie_type == ZombieType.POLE_VAULTER and zombie.has_pole:
            self._special_effects.render_pole(zombie_id, x, y, is_flipped=True)
        
        # 舞王僵尸渲染召唤效果
        if zombie_type == ZombieType.DANCER:
            self._special_effects.render_dancer_effect(zombie_id, x, y)
        
        # 气球僵尸渲染气球
        if zombie_type == ZombieType.BALLOON:
            self._special_effects.render_balloon(zombie_id, x, y, height)
        
        # 巨人僵尸渲染砸地效果
        if zombie_type == ZombieType.GARGANTUAR:
            self._special_effects.render_gargantuar_smash(zombie_id, x, y)
        
        # 矿工僵尸渲染隧道
        if zombie_type == ZombieType.MINER:
            self._special_effects.render_miner_tunnel(zombie_id)
        
        # 跳跳僵尸渲染跳跳杆
        if zombie_type == ZombieType.POGO:
            self._special_effects.render_pogo(zombie_id, x, y, height)
    
    def _get_armor_type(self, zombie_type_comp) -> str:
        """根据僵尸类型获取护甲类型"""
        if not zombie_type_comp:
            return 'none'
        
        armor_map = {
            ZombieType.CONEHEAD: 'cone',
            ZombieType.BUCKETHEAD: 'bucket',
            ZombieType.FOOTBALL: 'football',
            ZombieType.SCREEN_DOOR: 'screen',
        }
        return armor_map.get(zombie_type_comp.zombie_type, 'none')
    
    def trigger_hit(self, zombie_id: int, damage: int = 10) -> None:
        """触发僵尸受击效果"""
        self._visual_system.trigger_hit(zombie_id, damage)
    
    def trigger_armor_break(self, zombie_id: int) -> None:
        """触发护甲破碎效果"""
        self._visual_system.trigger_armor_break(zombie_id)
    
    def detach_part(self, zombie_id: int, part: str) -> None:
        """
        使僵尸部位脱落
        
        Args:
            zombie_id: 僵尸实体ID
            part: 部位名称 ('head', 'left_arm', 'right_arm')
        """
        self._visual_system.detach_part(zombie_id, part)
        
        # 同时更新动画渲染器
        part_map = {
            'head': ZombieBodyPart.HEAD,
            'left_arm': ZombieBodyPart.ARM_LEFT,
            'right_arm': ZombieBodyPart.ARM_RIGHT,
        }
        if part in part_map:
            self._anim_renderer.detach_part(zombie_id, part_map[part])
    
    def start_death_animation(self, zombie_id: int, x: float, y: float,
                             zombie_type: str = 'normal',
                             death_type: DeathType = DeathType.NORMAL) -> None:
        """开始死亡动画"""
        self._visual_system.start_death_animation(zombie_id, x, y, zombie_type, death_type)
    
    def start_pole_vault(self, zombie_id: int, start_x: float, target_x: float, start_y: float) -> None:
        """开始撑杆跳跃"""
        self._special_effects.start_pole_vault(zombie_id, start_x, target_x, start_y)
    
    def start_dancer_summon(self, zombie_id: int) -> None:
        """开始舞王召唤"""
        self._special_effects.start_dancer_summon(zombie_id)
    
    def start_gargantuar_smash(self, zombie_id: int) -> None:
        """开始巨人砸地"""
        self._special_effects.start_gargantuar_smash(zombie_id)
    
    def pop_balloon(self, zombie_id: int) -> None:
        """击破气球"""
        self._special_effects.pop_balloon(zombie_id)
    
    def remove_zombie(self, zombie_id: int) -> None:
        """移除僵尸的所有效果"""
        self._visual_system.remove_state(zombie_id)
        self._anim_renderer.reset(zombie_id)
        self._special_effects.remove_zombie(zombie_id)
    
    def clear(self) -> None:
        """清除所有效果"""
        self._visual_system.clear()
        self._anim_renderer.clear()
        self._special_effects.clear()
        self._time = 0.0
