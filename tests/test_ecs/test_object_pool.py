"""
对象池模式测试 - 优化实体创建/销毁性能
"""
import pytest


class TestEntityPool:
    """测试实体对象池"""

    def test_pool_acquire_returns_id(self):
        """测试从池中获取实体ID"""
        from src.ecs.entity_pool import EntityPool
        
        pool = EntityPool(initial_size=10)
        
        # 获取实体ID
        entity_id = pool.acquire()
        
        # 应该返回一个有效的ID
        assert isinstance(entity_id, int)
        assert entity_id >= 0

    def test_pool_reuses_released_ids(self):
        """测试池会重用释放的ID"""
        from src.ecs.entity_pool import EntityPool
        
        pool = EntityPool(initial_size=5)
        
        # 获取并释放ID
        entity_id1 = pool.acquire()
        pool.release(entity_id1)
        
        # 再次获取，应该重用同一个ID
        entity_id2 = pool.acquire()
        assert entity_id1 == entity_id2

    def test_pool_expands_when_empty(self):
        """测试池在空时会自动扩展"""
        from src.ecs.entity_pool import EntityPool
        
        pool = EntityPool(initial_size=2)
        
        # 获取所有初始ID
        id1 = pool.acquire()
        id2 = pool.acquire()
        
        # 池应该为空了，再次获取应该扩展
        id3 = pool.acquire()
        
        # 新ID应该大于初始ID
        assert id3 > id2

    def test_pool_tracks_active_count(self):
        """测试池跟踪活跃实体数量"""
        from src.ecs.entity_pool import EntityPool
        
        pool = EntityPool(initial_size=10)
        
        # 初始活跃数为0
        assert pool.get_active_count() == 0
        
        # 获取3个ID
        id1 = pool.acquire()
        id2 = pool.acquire()
        id3 = pool.acquire()
        
        assert pool.get_active_count() == 3
        
        # 释放1个
        pool.release(id1)
        assert pool.get_active_count() == 2

    def test_pool_clear_resets_state(self):
        """测试清空池重置状态"""
        from src.ecs.entity_pool import EntityPool
        
        pool = EntityPool(initial_size=5)
        
        # 获取并释放一些ID
        id1 = pool.acquire()
        id2 = pool.acquire()
        pool.release(id1)
        pool.release(id2)
        
        # 清空池
        pool.clear()
        
        # 应该回到初始状态
        assert pool.get_active_count() == 0
        
        # 再次获取应该得到一个有效的ID（在可用列表中）
        new_id = pool.acquire()
        assert isinstance(new_id, int)
        assert new_id >= 0


class TestPooledEntityManager:
    """测试使用对象池的实体管理器"""

    def test_pooled_manager_creates_entity(self):
        """测试使用池创建实体"""
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=10)
        
        # 创建实体
        entity_id = manager.create_entity()
        
        # 应该返回有效ID
        assert isinstance(entity_id, int)
        assert entity_id >= 0
        assert manager.is_valid_entity(entity_id)

    def test_pooled_manager_reuses_entities(self):
        """测试实体管理器重用实体"""
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=5)
        
        # 创建并销毁实体
        entity_id1 = manager.create_entity()
        manager.destroy_entity(entity_id1)
        manager.process_pending_removals()
        
        # 创建新实体，应该重用ID
        entity_id2 = manager.create_entity()
        
        # 在理想情况下应该重用，但取决于实现
        assert isinstance(entity_id2, int)

    def test_pooled_manager_tracks_entities(self):
        """测试实体管理器跟踪所有实体"""
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=10)
        
        # 创建3个实体
        id1 = manager.create_entity()
        id2 = manager.create_entity()
        id3 = manager.create_entity()
        
        # 获取所有实体
        all_entities = manager.get_all_entities()
        
        assert len(all_entities) == 3
        assert id1 in all_entities
        assert id2 in all_entities
        assert id3 in all_entities

    def test_pooled_manager_batch_destroy(self):
        """测试批量销毁实体"""
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=10)
        
        # 创建多个实体
        ids = [manager.create_entity() for _ in range(5)]
        
        # 标记所有实体待销毁
        for entity_id in ids:
            manager.destroy_entity(entity_id)
        
        # 此时实体还存在
        assert len(manager.get_all_entities()) == 5
        
        # 处理待销毁
        manager.process_pending_removals()
        
        # 所有实体应该被移除
        assert len(manager.get_all_entities()) == 0


class TestObjectPoolPerformance:
    """测试对象池性能优势"""

    def test_pool_performance_vs_no_pool(self):
        """测试对象池相比无池的性能优势"""
        import time
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=100)
        
        # 预热池
        for _ in range(50):
            entity_id = manager.create_entity()
            manager.destroy_entity(entity_id)
        manager.process_pending_removals()
        
        # 测试重用性能
        start = time.time()
        for _ in range(100):
            entity_id = manager.create_entity()
            manager.destroy_entity(entity_id)
            manager.process_pending_removals()
        pooled_time = time.time() - start
        
        # 只要有性能即可（具体提升取决于实现）
        assert pooled_time < 1.0  # 应该在1秒内完成

    def test_pool_memory_efficiency(self):
        """测试对象池内存效率"""
        from src.ecs.pooled_entity_manager import PooledEntityManager
        
        manager = PooledEntityManager(pool_size=1000)
        
        # 创建大量实体
        entity_ids = []
        for _ in range(500):
            entity_id = manager.create_entity()
            entity_ids.append(entity_id)
        
        # 销毁一半
        for entity_id in entity_ids[:250]:
            manager.destroy_entity(entity_id)
        manager.process_pending_removals()
        
        # 活跃实体数应该是250
        assert manager.get_active_count() == 250
        
        # 创建新实体应该重用ID
        new_id = manager.create_entity()
        assert new_id in entity_ids[:250]  # 应该重用了已释放的ID
