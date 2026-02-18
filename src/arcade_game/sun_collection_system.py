"""
阳光收集系统 - 处理阳光的生成和收集

包括：
- 天空掉落阳光
- 向日葵产生阳光
- 点击收集阳光
"""

import random
from typing import List, Optional, Callable
import arcade
from ..ecs import World, Entity
from ..ecs.components import (
    TransformComponent, SunProducerComponent, VelocityComponent,
    SpriteComponent
)
from .entity_factory import EntityFactory


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
    SUN_VALUE = 25  # 每个阳光的价值
    
    # 生成配置
    AUTO_SPAWN_INTERVAL = 10.0  # 天空阳光生成间隔（秒）
    GRID_START_X = 100
    GRID_END_X = 820
    GRID_START_Y = 50
    GRID_END_Y = 550
    
    def __init__(self, world: World, entity_factory: EntityFactory):
        self.world = world
        self.entity_factory = entity_factory
        
        # 计时器
        self.auto_spawn_timer = 0.0
        
        # 收集回调
        self.on_sun_collected_callbacks: List[Callable[[int], None]] = []
    
    def update(self, dt: float) -> None:
        """更新阳光系统"""
        # 更新自动生成计时器
        self.auto_spawn_timer += dt
        
        # 检查是否需要自动生成阳光
        if self.auto_spawn_timer >= self.AUTO_SPAWN_INTERVAL:
            self.auto_spawn_timer = 0.0
            self._spawn_falling_sun()
        
        # 更新所有阳光
        self._update_suns(dt)
    
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
        
        # 创建阳光实体
        sun = self.entity_factory.create_sun(x, y, self.SUN_VALUE, is_auto=False)
        
        # 添加下落速度
        velocity = VelocityComponent(
            vx=0.0,
            vy=-1.0,  # 向下移动
            base_speed=self.SUN_FALL_SPEED
        )
        self.world.add_component(sun, velocity)
        
        return sun
    
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
        # 获取阳光价值
        value = sun_producer.production_amount
        
        # 触发收集回调
        for callback in self.on_sun_collected_callbacks:
            callback(value)
        
        # 销毁阳光实体
        sun_entity = self.world.get_entity(sun_id)
        if sun_entity:
            self.world.destroy_entity(sun_entity)
    
    def register_collection_callback(self, callback: Callable[[int], None]) -> None:
        """
        注册阳光收集回调
        
        Args:
            callback: 回调函数，接收收集的阳光数量
        """
        self.on_sun_collected_callbacks.append(callback)
    
    def unregister_collection_callback(self, callback: Callable[[int], None]) -> None:
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
        # 创建阳光（停留在植物位置）
        sun = self.entity_factory.create_sun(x, y, self.SUN_VALUE, is_auto=True)
        
        # 不添加速度组件，让它停留在原地
        
        return sun
    
    def render_suns(self) -> None:
        """渲染所有阳光"""
        sun_ids = self.world.query_entities(TransformComponent, SunProducerComponent)
        
        for sun_id in sun_ids:
            sun_entity = self.world.get_entity(sun_id)
            if not sun_entity:
                continue
                
            transform = self.world.get_component(sun_entity, TransformComponent)
            if not transform:
                continue
            
            # 绘制阳光（圆形）
            arcade.draw_circle_filled(
                transform.x, transform.y,
                self.SUN_SIZE / 2,
                self.SUN_COLOR
            )
            
            # 绘制边框
            arcade.draw_circle_outline(
                transform.x, transform.y,
                self.SUN_SIZE / 2,
                arcade.color.ORANGE,
                2
            )
            
            # 绘制阳光值
            arcade.draw_text(
                f"{self.SUN_VALUE}",
                transform.x, transform.y,
                arcade.color.BLACK,
                12,
                anchor_x="center",
                anchor_y="center"
            )
    
    def reset(self) -> None:
        """重置系统"""
        self.auto_spawn_timer = 0.0
        
        # 清除所有阳光
        suns = self.world.query_entities(SunProducerComponent)
        for sun_id in suns:
            sun_entity = self.world.get_entity(sun_id)
            if sun_entity:
                self.world.destroy_entity(sun_entity)
    
    def get_sun_count(self) -> int:
        """获取当前阳光数量（可收集的）"""
        return len(self.world.query_entities(TransformComponent, SunProducerComponent))
