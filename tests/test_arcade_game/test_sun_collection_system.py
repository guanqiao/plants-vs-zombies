"""
测试阳光收集系统
"""

import pytest
from src.ecs import World
from src.arcade_game.entity_factory import EntityFactory
from src.arcade_game.sun_collection_system import SunCollectionSystem
from src.ecs.components import (
    TransformComponent, SunProducerComponent, VelocityComponent
)


class TestSunCollectionSystem:
    """测试阳光收集系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.sun_system = SunCollectionSystem(self.world, self.entity_factory)
        self.collected_amounts = []
        self.sun_system.register_collection_callback(self._on_sun_collected)
    
    def _on_sun_collected(self, amount: int, x: float, y: float):
        """收集回调"""
        self.collected_amounts.append(amount)
    
    def test_auto_spawn_timer(self):
        """测试自动生成计时器"""
        # 初始状态
        assert self.sun_system.auto_spawn_timer == 0.0
        
        # 更新计时器
        self.sun_system.update(5.0)
        assert self.sun_system.auto_spawn_timer == 5.0
        
        # 超过间隔，应该生成阳光并重置
        initial_count = self.sun_system.get_sun_count()
        self.sun_system.update(6.0)  # 总共11秒
        # 检查生成了阳光
        assert self.sun_system.get_sun_count() > initial_count
        assert self.sun_system.auto_spawn_timer == 0.0
    
    def test_spawn_falling_sun(self):
        """测试生成掉落阳光"""
        # 生成阳光
        sun = self.sun_system._spawn_falling_sun()
        
        # 检查实体创建
        assert sun is not None
        
        # 检查组件
        transform = self.world.get_component(sun, TransformComponent)
        assert transform is not None
        assert transform.y > 500  # 从屏幕顶部开始
        
        # 检查速度组件
        velocity = self.world.get_component(sun, VelocityComponent)
        assert velocity is not None
        assert velocity.vy < 0  # 向下移动
        
        # 检查阳光组件
        sun_producer = self.world.get_component(sun, SunProducerComponent)
        assert sun_producer is not None
        assert not sun_producer.is_auto  # 天空掉落的不是自动产生
    
    def test_is_point_in_sun(self):
        """测试点是否在阳光内"""
        # 阳光中心在(100, 100)，大小40
        assert self.sun_system._is_point_in_sun(100, 100, 100, 100)  # 中心点
        assert self.sun_system._is_point_in_sun(90, 90, 100, 100)   # 内部
        assert self.sun_system._is_point_in_sun(110, 110, 100, 100) # 内部
        assert not self.sun_system._is_point_in_sun(50, 50, 100, 100)  # 外部
        assert not self.sun_system._is_point_in_sun(150, 150, 100, 100) # 外部
    
    def test_handle_mouse_press_collect_sun(self):
        """测试鼠标点击收集阳光"""
        # 生成阳光
        sun = self.sun_system._spawn_falling_sun()
        transform = self.world.get_component(sun, TransformComponent)
        
        # 点击阳光位置
        result = self.sun_system.handle_mouse_press(transform.x, transform.y)
        
        # 检查收集成功
        assert result is True
        assert len(self.collected_amounts) == 1
        assert self.collected_amounts[0] == 25  # 阳光价值
        
        # 检查阳光被移除（需要触发销毁处理）
        self.world.update(0.1)
        assert self.sun_system.get_sun_count() == 0
    
    def test_handle_mouse_press_miss_sun(self):
        """测试鼠标点击未命中阳光"""
        # 生成阳光
        sun = self.sun_system._spawn_falling_sun()
        
        # 点击远离阳光的位置
        result = self.sun_system.handle_mouse_press(10, 10)
        
        # 检查未收集
        assert result is False
        assert len(self.collected_amounts) == 0
        
        # 检查阳光仍在
        assert self.sun_system.get_sun_count() == 1
    
    def test_collect_sun(self):
        """测试收集阳光"""
        # 生成阳光
        sun = self.entity_factory.create_sun(100, 100, 25, is_auto=False)
        sun_producer = self.world.get_component(sun, SunProducerComponent)
        
        # 收集阳光
        self.sun_system._collect_sun(sun.id, sun_producer)
        
        # 检查回调被触发
        assert len(self.collected_amounts) == 1
        assert self.collected_amounts[0] == 25
        
        # 检查实体被销毁
        self.world.update(0.1)  # 触发销毁处理
        assert self.sun_system.get_sun_count() == 0
    
    def test_reset(self):
        """测试重置系统"""
        # 生成多个阳光
        for _ in range(3):
            self.sun_system._spawn_falling_sun()
        
        # 设置计时器
        self.sun_system.auto_spawn_timer = 100.0
        
        # 检查初始状态
        assert self.sun_system.get_sun_count() == 3
        
        # 重置
        self.sun_system.reset()
        
        # 检查重置状态
        assert self.sun_system.auto_spawn_timer == 0.0
        self.world.update(0.1)  # 触发销毁处理
        assert self.sun_system.get_sun_count() == 0
    
    def test_get_sun_count(self):
        """测试获取阳光数量"""
        # 初始状态
        assert self.sun_system.get_sun_count() == 0
        
        # 生成阳光
        self.sun_system._spawn_falling_sun()
        assert self.sun_system.get_sun_count() == 1
        
        # 再生成一个
        self.sun_system._spawn_falling_sun()
        assert self.sun_system.get_sun_count() == 2


class TestSunCollectionSystemIntegration:
    """测试阳光收集系统集成"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.sun_system = SunCollectionSystem(self.world, self.entity_factory)
        self.collected_amounts = []
        self.sun_system.register_collection_callback(self._on_sun_collected)
    
    def _on_sun_collected(self, amount: int, x: float, y: float):
        """收集回调"""
        self.collected_amounts.append(amount)
    
    def test_full_collection_workflow(self):
        """测试完整收集流程"""
        # 1. 生成掉落阳光
        sun = self.sun_system._spawn_falling_sun()
        assert self.sun_system.get_sun_count() == 1
        
        # 2. 获取阳光位置
        transform = self.world.get_component(sun, TransformComponent)
        
        # 3. 点击收集
        result = self.sun_system.handle_mouse_press(transform.x, transform.y)
        assert result is True
        
        # 4. 检查收集到的阳光值
        assert len(self.collected_amounts) == 1
        assert self.collected_amounts[0] == 25
        
        # 5. 检查阳光被移除
        self.world.update(0.1)
        assert self.sun_system.get_sun_count() == 0
    
    def test_multiple_suns_collection(self):
        """测试收集多个阳光"""
        # 生成3个阳光
        suns = []
        for _ in range(3):
            sun = self.sun_system._spawn_falling_sun()
            suns.append(sun)
        
        assert self.sun_system.get_sun_count() == 3
        
        # 收集所有阳光
        for sun in suns:
            transform = self.world.get_component(sun, TransformComponent)
            self.sun_system.handle_mouse_press(transform.x, transform.y)
        
        # 检查收集到的总值
        assert len(self.collected_amounts) == 3
        assert sum(self.collected_amounts) == 75  # 3 * 25
    
    def test_auto_spawn_over_time(self):
        """测试随时间自动生成阳光"""
        # 初始状态
        initial_count = self.sun_system.get_sun_count()
        
        # 模拟时间流逝（超过生成间隔）
        for _ in range(12):
            self.sun_system.update(1.0)  # 每次1秒
        
        # 检查生成了至少一个阳光
        assert self.sun_system.get_sun_count() > initial_count
