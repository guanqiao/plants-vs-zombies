"""
阳光收集系统 - 处理阳光的生成和收集

包括：
- 天空掉落阳光
- 向日葵产生阳光
- 点击收集阳光
- 增强的视觉效果（发光、脉动、拖尾）
"""

import random
import math
from typing import List, Optional, Callable, Tuple
import arcade
from ..ecs import World, Entity
from ..ecs.components import (
    TransformComponent, SunProducerComponent, VelocityComponent,
    SpriteComponent
)
from .entity_factory import EntityFactory


class SunVisualEffect:
    """阳光视觉效果"""
    
    def __init__(self):
        self.time = 0.0
        self.pulse_phase = 0.0
        self.glow_intensity = 1.0
        self.trail_positions: List[Tuple[float, float, float]] = []  # (x, y, alpha)
    
    def update(self, dt: float, x: float, y: float) -> None:
        """更新效果"""
        self.time += dt
        self.pulse_phase = math.sin(self.time * 3) * 0.5 + 0.5
        
        # 添加拖尾
        self.trail_positions.append((x, y, 1.0))
        
        # 更新拖尾
        new_trail = []
        for tx, ty, alpha in self.trail_positions:
            new_alpha = alpha - dt * 3
            if new_alpha > 0:
                new_trail.append((tx, ty, new_alpha))
        self.trail_positions = new_trail[-10:]  # 保留最近10个位置


class SunCollectionSystem:
    """
    阳光收集系统
    
    管理所有阳光的生成和收集逻辑
    """
    
    # 屏幕配置
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 600
    
    # 阳光配置
    SUN_SIZE = 40
    SUN_COLOR = (255, 255, 0)  # 黄色
    SUN_FALL_SPEED = 50.0  # 下落速度（像素/秒）
    
    # 生成配置
    GRID_START_X = 100
    GRID_END_X = 820
    GRID_START_Y = 50
    GRID_END_Y = 550
    
    # 颜色配置
    SUN_GLOW_COLOR = (255, 220, 100)
    SUN_INNER_COLOR = (255, 240, 150)
    
    def __init__(self, world: World, entity_factory: EntityFactory):
        self.world = world
        self.entity_factory = entity_factory
        
        # 计时器
        self.auto_spawn_timer = 0.0
        
        # 动态配置（根据难度调整）
        self.auto_spawn_interval = 10.0  # 天空阳光生成间隔（秒）
        self.sun_value = 25  # 每个阳光的价值
        
        # 收集回调 - 接收 (amount, x, y)
        self.on_sun_collected_callbacks: List[Callable[[int, float, float], None]] = []
        
        # 阳光视觉效果
        self._sun_effects: dict = {}  # sun_id -> SunVisualEffect
        self._global_time = 0.0
    
    def set_difficulty_config(self, auto_spawn_interval: float, sun_value: int) -> None:
        """
        设置难度相关配置
        
        Args:
            auto_spawn_interval: 天空阳光生成间隔（秒）
            sun_value: 每个阳光的价值
        """
        self.auto_spawn_interval = auto_spawn_interval
        self.sun_value = sun_value
        
        # 阳光视觉效果
        self._sun_effects: dict = {}  # sun_id -> SunVisualEffect
        self._global_time = 0.0
    
    def update(self, dt: float) -> None:
        """更新阳光系统"""
        self._global_time += dt
        
        # 更新自动生成计时器
        self.auto_spawn_timer += dt
        
        # 检查是否需要自动生成阳光（使用动态间隔）
        if self.auto_spawn_timer >= self.auto_spawn_interval:
            self.auto_spawn_timer = 0.0
            self._spawn_falling_sun()
        
        # 更新所有阳光
        self._update_suns(dt)
        
        # 更新阳光视觉效果
        self._update_sun_effects(dt)
    
    def _spawn_falling_sun(self) -> Optional[Entity]:
        """
        生成从天空掉落的阳光
        
        Returns:
            生成的阳光实体
        """
        # 随机X坐标（在网格范围内）
        x = random.uniform(self.GRID_START_X, self.GRID_END_X)
        # 从屏幕顶部开始
        y = self.SCREEN_HEIGHT - 50
        
        # 创建阳光实体（使用动态阳光价值）
        sun = self.entity_factory.create_sun(x, y, self.sun_value, is_auto=False)
        
        # 添加下落速度
        velocity = VelocityComponent(
            vx=0.0,
            vy=-1.0,
            base_speed=self.SUN_FALL_SPEED
        )
        self.world.add_component(sun, velocity)
        
        # 创建视觉效果
        self._sun_effects[sun.id] = SunVisualEffect()
        
        return sun
    
    def _update_sun_effects(self, dt: float) -> None:
        """更新阳光视觉效果"""
        sun_ids = self.world.query_entities(TransformComponent, SunProducerComponent)
        
        # 清理已消失的阳光效果
        existing_ids = set(sun_ids)
        for sun_id in list(self._sun_effects.keys()):
            if sun_id not in existing_ids:
                del self._sun_effects[sun_id]
        
        # 更新现有效果
        for sun_id in sun_ids:
            sun_entity = self.world.get_entity(sun_id)
            if not sun_entity:
                continue
            
            transform = self.world.get_component(sun_entity, TransformComponent)
            if not transform:
                continue
            
            if sun_id not in self._sun_effects:
                self._sun_effects[sun_id] = SunVisualEffect()
            
            self._sun_effects[sun_id].update(dt, transform.x, transform.y)
    
    def _update_suns(self, dt: float) -> None:
        """更新所有阳光的状态"""
        # 获取所有阳光实体ID
        sun_ids = self.world.query_entities(TransformComponent, SunProducerComponent)
        
        for sun_id in sun_ids:
            sun_entity = self.world.get_entity(sun_id)
            if not sun_entity:
                continue
                
            sun_producer = self.world.get_component(sun_entity, SunProducerComponent)
            
            # 只处理非自动产生的阳光（天空掉落的）
            if not sun_producer.is_auto:
                transform = self.world.get_component(sun_entity, TransformComponent)
                velocity = self.world.get_component(sun_entity, VelocityComponent)
                
                if transform and velocity:
                    # 检查是否落地
                    if transform.y <= self.GRID_START_Y + 20:
                        # 停止下落
                        velocity.vx = 0.0
                        velocity.vy = 0.0
                        velocity.base_speed = 0.0
                        
                        # 设置一个停留时间后消失
                        sun_producer.lifetime = 8.0  # 停留8秒
    
    def handle_mouse_press(self, x: float, y: float) -> bool:
        """
        处理鼠标点击收集阳光
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            
        Returns:
            是否收集到了阳光
        """
        # 获取所有可收集的阳光ID
        sun_ids = self.world.query_entities(TransformComponent, SunProducerComponent)
        
        for sun_id in sun_ids:
            sun_entity = self.world.get_entity(sun_id)
            if not sun_entity:
                continue
                
            sun_producer = self.world.get_component(sun_entity, SunProducerComponent)
            
            # 检查是否可以收集
            if not sun_producer.is_collectable:
                continue
            
            transform = self.world.get_component(sun_entity, TransformComponent)
            if not transform:
                continue
            
            # 检查点击是否在阳光范围内
            if self._is_point_in_sun(x, y, transform.x, transform.y):
                # 收集阳光
                self._collect_sun(sun_id, sun_producer)
                return True
        
        return False
    
    def _is_point_in_sun(self, px: float, py: float, 
                         sun_x: float, sun_y: float) -> bool:
        """
        检查点是否在阳光范围内
        
        Args:
            px: 点X坐标
            py: 点Y坐标
            sun_x: 阳光中心X坐标
            sun_y: 阳光中心Y坐标
            
        Returns:
            是否在范围内
        """
        half_size = self.SUN_SIZE / 2
        return (sun_x - half_size <= px <= sun_x + half_size and
                sun_y - half_size <= py <= sun_y + half_size)
    
    def _collect_sun(self, sun_id: int, sun_producer: SunProducerComponent) -> None:
        """
        收集阳光
        
        Args:
            sun_id: 阳光实体ID
            sun_producer: 阳光生产组件
        """
        # 获取阳光价值和位置
        value = sun_producer.production_amount
        
        # 获取阳光位置
        sun_entity = self.world.get_entity(sun_id)
        x, y = 0.0, 0.0
        if sun_entity:
            transform = self.world.get_component(sun_entity, TransformComponent)
            if transform:
                x, y = transform.x, transform.y
        
        # 触发收集回调
        for callback in self.on_sun_collected_callbacks:
            callback(value, x, y)
        
        # 销毁阳光实体
        if sun_entity:
            self.world.destroy_entity(sun_entity)
    
    def register_collection_callback(self, callback: Callable[[int, float, float], None]) -> None:
        """
        注册阳光收集回调
        
        Args:
            callback: 回调函数，接收 (amount, x, y)
        """
        self.on_sun_collected_callbacks.append(callback)
    
    def unregister_collection_callback(self, callback: Callable[[int, float, float], None]) -> None:
        """注销阳光收集回调"""
        if callback in self.on_sun_collected_callbacks:
            self.on_sun_collected_callbacks.remove(callback)
    
    def spawn_sunflower_sun(self, x: float, y: float) -> Optional[Entity]:
        """
        生成向日葵产生的阳光
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            生成的阳光实体
        """
        # 创建阳光（停留在植物位置，使用动态阳光价值）
        sun = self.entity_factory.create_sun(x, y, self.sun_value, is_auto=True)
        
        # 创建视觉效果
        self._sun_effects[sun.id] = SunVisualEffect()
        
        return sun
    
    def render_suns(self) -> None:
        """渲染所有阳光（带增强视觉效果）"""
        sun_ids = self.world.query_entities(TransformComponent, SunProducerComponent)
        
        for sun_id in sun_ids:
            sun_entity = self.world.get_entity(sun_id)
            if not sun_entity:
                continue
                
            transform = self.world.get_component(sun_entity, TransformComponent)
            if not transform:
                continue
            
            # 获取视觉效果
            effect = self._sun_effects.get(sun_id)
            pulse = effect.pulse_phase if effect else 0.5
            
            x, y = transform.x, transform.y
            base_size = self.SUN_SIZE / 2
            
            # 绘制拖尾效果
            if effect and effect.trail_positions:
                for i, (tx, ty, alpha) in enumerate(effect.trail_positions[:-1]):
                    trail_alpha = int(alpha * 100)
                    trail_size = base_size * (0.3 + 0.3 * alpha)
                    if trail_alpha > 0:
                        arcade.draw_circle_filled(
                            tx, ty, trail_size,
                            (*self.SUN_GLOW_COLOR, trail_alpha)
                        )
            
            # 绘制外发光
            glow_size = base_size * (1.5 + pulse * 0.3)
            glow_alpha = int(80 + pulse * 40)
            arcade.draw_circle_filled(x, y, glow_size, (*self.SUN_GLOW_COLOR, glow_alpha))
            
            # 绘制光芒
            self._draw_sun_rays(x, y, base_size, pulse)
            
            # 绘制主体
            arcade.draw_circle_filled(x, y, base_size, self.SUN_COLOR)
            
            # 绘制内部渐变
            inner_size = base_size * 0.7
            arcade.draw_circle_filled(x, y, inner_size, self.SUN_INNER_COLOR)
            
            # 绘制中心高光
            highlight_size = base_size * 0.3
            arcade.draw_circle_filled(x - base_size * 0.2, y + base_size * 0.2, 
                                     highlight_size, (255, 255, 255, 200))
            
            # 绘制边框
            arcade.draw_circle_outline(x, y, base_size, (255, 180, 0), 2)
            
            # 绘制阳光值
            arcade.draw_text(
                f"{self.sun_value}",
                x, y - 2,
                (200, 150, 0), 10,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )
    
    def _draw_sun_rays(self, x: float, y: float, base_size: float, pulse: float) -> None:
        """绘制阳光光芒"""
        ray_count = 8
        ray_length = base_size * (1.3 + pulse * 0.2)
        ray_width = 3
        
        for i in range(ray_count):
            angle = (i / ray_count) * math.pi * 2 + self._global_time * 0.5
            
            # 光芒起点和终点
            start_x = x + math.cos(angle) * base_size * 0.9
            start_y = y + math.sin(angle) * base_size * 0.9
            end_x = x + math.cos(angle) * ray_length
            end_y = y + math.sin(angle) * ray_length
            
            alpha = int(150 + pulse * 50)
            arcade.draw_line(start_x, start_y, end_x, end_y, 
                           (*self.SUN_GLOW_COLOR, alpha), ray_width)
    
    def reset(self) -> None:
        """重置系统"""
        self.auto_spawn_timer = 0.0
        
        # 清除所有阳光
        suns = self.world.query_entities(SunProducerComponent)
        for sun_id in suns:
            sun_entity = self.world.get_entity(sun_id)
            if sun_entity:
                self.world.destroy_entity(sun_entity)
        
        # 清除视觉效果
        self._sun_effects.clear()
    
    def get_sun_count(self) -> int:
        """获取当前阳光数量（可收集的）"""
        return len(self.world.query_entities(TransformComponent, SunProducerComponent))
