"""
ECS组件查询缓存测试
"""
import pytest
from src.ecs.world import World
from src.ecs.components import TransformComponent, PlantComponent, ZombieComponent


class TestComponentQueryCache:
    """测试组件查询缓存功能"""

    def test_query_cache_basic(self):
        """测试基本查询缓存功能"""
        world = World()
        manager = world._component_manager
        
        # 创建实体并添加组件
        entity1 = world.create_entity()
        manager.add_component(entity1, TransformComponent(x=0, y=0))
        manager.add_component(entity1, PlantComponent())
        
        entity2 = world.create_entity()
        manager.add_component(entity2, TransformComponent(x=10, y=10))
        manager.add_component(entity2, ZombieComponent())
        
        # 第一次查询（应该缓存）
        result1 = manager.query(TransformComponent, PlantComponent)
        
        # 第二次查询（应该使用缓存）
        result2 = manager.query(TransformComponent, PlantComponent)
        
        # 结果应该相同
        assert set(result1) == set(result2)
        assert len(result1) == 1
        assert entity1 in result1

    def test_query_cache_invalidation(self):
        """测试缓存失效机制"""
        world = World()
        manager = world._component_manager
        
        # 创建实体并添加组件
        entity1 = world.create_entity()
        manager.add_component(entity1, TransformComponent(x=0, y=0))
        manager.add_component(entity1, PlantComponent())
        
        # 第一次查询
        result1 = manager.query(TransformComponent, PlantComponent)
        assert len(result1) == 1
        
        # 添加新实体（应该使缓存失效）
        entity2 = world.create_entity()
        manager.add_component(entity2, TransformComponent(x=10, y=10))
        manager.add_component(entity2, PlantComponent())
        
        # 再次查询（应该返回新结果）
        result2 = manager.query(TransformComponent, PlantComponent)
        assert len(result2) == 2
        assert entity1 in result2
        assert entity2 in result2

    def test_query_cache_removal(self):
        """测试移除组件时缓存失效"""
        world = World()
        manager = world._component_manager
        
        # 创建实体并添加组件
        entity1 = world.create_entity()
        manager.add_component(entity1, TransformComponent(x=0, y=0))
        manager.add_component(entity1, PlantComponent())
        
        # 查询
        result1 = manager.query(TransformComponent, PlantComponent)
        assert len(result1) == 1
        
        # 移除组件（应该使缓存失效）
        manager.remove_component(entity1, PlantComponent)
        
        # 再次查询
        result2 = manager.query(TransformComponent, PlantComponent)
        assert len(result2) == 0

    def test_query_cache_performance(self):
        """测试缓存性能提升"""
        import time
        
        world = World()
        manager = world._component_manager
        
        # 创建大量实体
        for i in range(100):
            entity = world.create_entity()
            manager.add_component(entity, TransformComponent(x=i, y=i))
            if i % 2 == 0:
                manager.add_component(entity, PlantComponent())
        
        # 第一次查询（无缓存）
        start = time.time()
        result1 = manager.query(TransformComponent, PlantComponent)
        first_query_time = time.time() - start
        
        # 第二次查询（有缓存）
        start = time.time()
        result2 = manager.query(TransformComponent, PlantComponent)
        second_query_time = time.time() - start
        
        # 结果应该相同（缓存可能使查询更快，但即使时间相同也接受）
        assert set(result1) == set(result2)
        # 缓存查询应该更快或相等（在极快的情况下可能相等）
        assert second_query_time <= first_query_time

    def test_query_cache_multiple_types(self):
        """测试多种组件类型组合的缓存"""
        world = World()
        manager = world._component_manager
        
        # 创建不同组合的实体
        entity1 = world.create_entity()
        manager.add_component(entity1, TransformComponent(x=0, y=0))
        manager.add_component(entity1, PlantComponent())
        
        entity2 = world.create_entity()
        manager.add_component(entity2, TransformComponent(x=10, y=10))
        manager.add_component(entity2, ZombieComponent())
        
        entity3 = world.create_entity()
        manager.add_component(entity3, TransformComponent(x=20, y=20))
        manager.add_component(entity3, PlantComponent())
        manager.add_component(entity3, ZombieComponent())
        
        # 查询不同组合
        plants = manager.query(TransformComponent, PlantComponent)
        zombies = manager.query(TransformComponent, ZombieComponent)
        both = manager.query(TransformComponent, PlantComponent, ZombieComponent)
        
        assert len(plants) == 2  # entity1, entity3
        assert len(zombies) == 2  # entity2, entity3
        assert len(both) == 1  # entity3

    def test_query_cache_single_component(self):
        """测试单组件查询缓存"""
        world = World()
        manager = world._component_manager
        
        # 创建实体
        entity1 = world.create_entity()
        manager.add_component(entity1, TransformComponent(x=0, y=0))
        
        entity2 = world.create_entity()
        manager.add_component(entity2, TransformComponent(x=10, y=10))
        
        # 查询
        result1 = manager.query(TransformComponent)
        result2 = manager.query(TransformComponent)
        
        assert len(result1) == 2
        assert set(result1) == set(result2)
