"""
测试ECS系统模块
"""

import pytest
from src.ecs import World
from src.ecs.systems import MovementSystem, HealthSystem
from src.ecs.components import (
    TransformComponent, VelocityComponent, HealthComponent
)


class TestMovementSystem:
    """测试移动系统"""
    
    def test_basic_movement(self):
        """测试基本移动"""
        world = World()
        movement_system = MovementSystem(priority=10)
        world.add_system(movement_system)
        
        # 创建移动的实体
        entity = world.create_entity()
        world.add_component(entity, TransformComponent(x=100, y=100))
        world.add_component(entity, VelocityComponent(vx=1.0, vy=0.0, base_speed=100.0))
        
        # 更新一帧（假设60fps）
        world.update(1/60)
        
        transform = world.get_component(entity, TransformComponent)
        # 应该向右移动 100 * (1/60) ≈ 1.67 像素
        assert transform.x > 100
        assert transform.y == 100
    
    def test_speed_multiplier(self):
        """测试速度倍率"""
        velocity = VelocityComponent(vx=1.0, vy=0.0, base_speed=100.0)
        
        assert velocity.get_actual_speed() == 100.0
        
        velocity.apply_multiplier(0.5)  # 减速50%
        assert velocity.get_actual_speed() == 50.0
        
        velocity.reset_multiplier()
        assert velocity.get_actual_speed() == 100.0


class TestHealthSystem:
    """测试生命值系统"""
    
    def test_death_detection(self):
        """测试死亡检测"""
        world = World()
        health_system = HealthSystem(priority=30)
        world.add_system(health_system)
        
        # 创建实体
        entity = world.create_entity()
        world.add_component(entity, HealthComponent(current=50, max_health=100))
        
        # 造成伤害
        health = world.get_component(entity, HealthComponent)
        health.take_damage(60)
        
        # 更新系统
        world.update(1/60)
        
        # 实体应该被标记为死亡
        assert health.is_dead


class TestSystemPriority:
    """测试系统优先级"""
    
    def test_priority_order(self):
        """测试系统按优先级排序"""
        world = World()
        
        # 添加系统（不按优先级顺序）
        system1 = MovementSystem(priority=20)
        system2 = HealthSystem(priority=10)
        system3 = MovementSystem(priority=30)
        
        world.add_system(system1)
        world.add_system(system2)
        world.add_system(system3)
        
        # 获取系统列表并检查顺序
        systems = world._system_manager.get_systems()
        priorities = [s.priority for s in systems]
        
        assert priorities == [10, 20, 30]