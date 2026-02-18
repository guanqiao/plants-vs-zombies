"""
测试空间哈希系统
"""

import pytest
from src.core.spatial_hash import (
    AABB, SpatialHash, ObjectPool, PerformanceMonitor
)


class TestAABB:
    """测试轴对齐包围盒"""
    
    def test_initialization(self):
        """测试初始化"""
        aabb = AABB(x=10, y=20, width=30, height=40)
        
        assert aabb.x == 10
        assert aabb.y == 20
        assert aabb.width == 30
        assert aabb.height == 40
    
    def test_properties(self):
        """测试属性"""
        aabb = AABB(x=10, y=20, width=30, height=40)
        
        assert aabb.left == 10
        assert aabb.right == 40
        assert aabb.bottom == 20
        assert aabb.top == 60
    
    def test_intersects(self):
        """测试相交检测"""
        aabb1 = AABB(x=0, y=0, width=10, height=10)
        aabb2 = AABB(x=5, y=5, width=10, height=10)
        aabb3 = AABB(x=20, y=20, width=10, height=10)
        
        # 相交
        assert aabb1.intersects(aabb2)
        assert aabb2.intersects(aabb1)
        
        # 不相交
        assert not aabb1.intersects(aabb3)
        assert not aabb3.intersects(aabb1)
    
    def test_contains_point(self):
        """测试点包含"""
        aabb = AABB(x=0, y=0, width=10, height=10)
        
        # 内部点
        assert aabb.contains_point(5, 5)
        
        # 边界点
        assert aabb.contains_point(0, 0)
        assert aabb.contains_point(10, 10)
        
        # 外部点
        assert not aabb.contains_point(15, 15)
        assert not aabb.contains_point(-5, -5)


class TestSpatialHash:
    """测试空间哈希"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.spatial_hash = SpatialHash(cell_size=100.0)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.spatial_hash.cell_size == 100.0
        assert len(self.spatial_hash.grid) == 0
        assert len(self.spatial_hash.entity_cells) == 0
    
    def test_insert(self):
        """测试插入"""
        aabb = AABB(x=50, y=50, width=10, height=10)
        self.spatial_hash.insert(1, aabb)
        
        # 检查实体被记录
        assert 1 in self.spatial_hash.entity_cells
        
        # 检查网格中有数据
        assert len(self.spatial_hash.grid) > 0
    
    def test_remove(self):
        """测试移除"""
        aabb = AABB(x=50, y=50, width=10, height=10)
        self.spatial_hash.insert(1, aabb)
        
        # 确认插入成功
        assert 1 in self.spatial_hash.entity_cells
        
        # 移除
        self.spatial_hash.remove(1)
        
        # 确认移除成功
        assert 1 not in self.spatial_hash.entity_cells
    
    def test_update(self):
        """测试更新"""
        aabb1 = AABB(x=50, y=50, width=10, height=10)
        self.spatial_hash.insert(1, aabb1)
        
        # 更新位置
        aabb2 = AABB(x=200, y=200, width=10, height=10)
        self.spatial_hash.update(1, aabb2)
        
        # 确认实体仍在
        assert 1 in self.spatial_hash.entity_cells
    
    def test_query_point(self):
        """测试点查询"""
        aabb = AABB(x=50, y=50, width=10, height=10)
        self.spatial_hash.insert(1, aabb)
        
        # 查询内部点
        results = self.spatial_hash.query_point(55, 55)
        assert 1 in results
        
        # 查询外部点
        results = self.spatial_hash.query_point(200, 200)
        assert 1 not in results
    
    def test_query_aabb(self):
        """测试AABB查询"""
        aabb1 = AABB(x=50, y=50, width=10, height=10)
        aabb2 = AABB(x=200, y=200, width=10, height=10)
        
        self.spatial_hash.insert(1, aabb1)
        self.spatial_hash.insert(2, aabb2)
        
        # 查询区域包含实体1
        query = AABB(x=0, y=0, width=100, height=100)
        results = self.spatial_hash.query_aabb(query)
        assert 1 in results
        assert 2 not in results
    
    def test_query_radius(self):
        """测试半径查询"""
        aabb = AABB(x=100, y=100, width=10, height=10)
        self.spatial_hash.insert(1, aabb)
        
        # 查询半径内
        results = self.spatial_hash.query_radius(105, 105, 50)
        assert 1 in results
        
        # 查询半径外
        results = self.spatial_hash.query_radius(500, 500, 50)
        assert 1 not in results
    
    def test_get_nearby_entities(self):
        """测试获取附近实体"""
        aabb1 = AABB(x=50, y=50, width=10, height=10)
        aabb2 = AABB(x=60, y=60, width=10, height=10)
        aabb3 = AABB(x=500, y=500, width=10, height=10)
        
        self.spatial_hash.insert(1, aabb1)
        self.spatial_hash.insert(2, aabb2)
        self.spatial_hash.insert(3, aabb3)
        
        # 查询实体1附近的实体
        nearby = self.spatial_hash.get_nearby_entities(1, 200)
        assert 2 in nearby
        assert 3 not in nearby
        assert 1 not in nearby  # 不包含自身
    
    def test_clear(self):
        """测试清空"""
        aabb = AABB(x=50, y=50, width=10, height=10)
        self.spatial_hash.insert(1, aabb)
        
        # 确认有数据
        assert len(self.spatial_hash.grid) > 0
        
        # 清空
        self.spatial_hash.clear()
        
        # 确认清空
        assert len(self.spatial_hash.grid) == 0
        assert len(self.spatial_hash.entity_cells) == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.spatial_hash.get_stats()
        
        assert 'cell_size' in stats
        assert 'total_cells' in stats
        assert 'total_entities' in stats
        assert 'avg_entities_per_cell' in stats
    
    def test_multiple_entities_same_cell(self):
        """测试同一单元中的多个实体"""
        aabb1 = AABB(x=10, y=10, width=5, height=5)
        aabb2 = AABB(x=20, y=20, width=5, height=5)
        aabb3 = AABB(x=30, y=30, width=5, height=5)
        
        self.spatial_hash.insert(1, aabb1)
        self.spatial_hash.insert(2, aabb2)
        self.spatial_hash.insert(3, aabb3)
        
        # 查询应该返回所有实体
        results = self.spatial_hash.query_point(25, 25)
        assert len(results) == 3


class TestObjectPool:
    """测试对象池"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.factory_call_count = 0
        
        def factory():
            self.factory_call_count += 1
            return {'id': self.factory_call_count}
        
        def reset(obj):
            obj['used'] = True
        
        self.pool = ObjectPool(factory, reset, initial_size=5)
    
    def test_initialization(self):
        """测试初始化"""
        stats = self.pool.get_stats()
        assert stats['available'] == 5
        assert stats['in_use'] == 0
        assert stats['total'] == 5
    
    def test_acquire(self):
        """测试获取对象"""
        obj = self.pool.acquire()
        
        assert obj is not None
        assert obj['used'] is True
        
        stats = self.pool.get_stats()
        assert stats['available'] == 4
        assert stats['in_use'] == 1
    
    def test_release(self):
        """测试释放对象"""
        obj = self.pool.acquire()
        
        stats = self.pool.get_stats()
        assert stats['in_use'] == 1
        
        self.pool.release(obj)
        
        stats = self.pool.get_stats()
        assert stats['available'] == 5
        assert stats['in_use'] == 0
    
    def test_release_all(self):
        """测试释放所有对象"""
        # 获取多个对象
        objs = [self.pool.acquire() for _ in range(3)]
        
        stats = self.pool.get_stats()
        assert stats['in_use'] == 3
        
        # 释放所有
        self.pool.release_all()
        
        stats = self.pool.get_stats()
        assert stats['in_use'] == 0
        assert stats['available'] == 5
    
    def test_expand_pool(self):
        """测试池扩展"""
        # 获取超过初始大小的对象
        objs = [self.pool.acquire() for _ in range(10)]
        
        stats = self.pool.get_stats()
        assert stats['total'] == 10
        assert stats['in_use'] == 10
        assert stats['available'] == 0


class TestPerformanceMonitor:
    """测试性能监控器"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.monitor = PerformanceMonitor(history_size=10)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.monitor.history_size == 10
        assert len(self.monitor.fps_history) == 0
    
    def test_update(self):
        """测试更新"""
        self.monitor.update(0.016, 100, 50)
        
        assert len(self.monitor.fps_history) == 1
        assert len(self.monitor.frame_time_history) == 1
        assert len(self.monitor.entity_count_history) == 1
        assert len(self.monitor.collision_check_history) == 1
    
    def test_history_limit(self):
        """测试历史记录限制"""
        # 添加超过限制的数据
        for i in range(15):
            self.monitor.update(0.016, i, i * 10)
        
        # 应该只保留最近10个
        assert len(self.monitor.fps_history) == 10
    
    def test_get_average_fps(self):
        """测试获取平均FPS"""
        # 添加数据（0.016秒 = 62.5 FPS）
        for _ in range(5):
            self.monitor.update(0.016, 100, 50)
        
        avg_fps = self.monitor.get_average_fps()
        assert avg_fps > 60
    
    def test_get_average_frame_time(self):
        """测试获取平均帧时间"""
        # 添加数据
        for _ in range(5):
            self.monitor.update(0.016, 100, 50)
        
        avg_time = self.monitor.get_average_frame_time()
        assert 15 < avg_time < 17  # 0.016秒 = 16毫秒
    
    def test_get_stats(self):
        """测试获取统计信息"""
        self.monitor.update(0.016, 100, 50)
        
        stats = self.monitor.get_stats()
        
        assert 'avg_fps' in stats
        assert 'avg_frame_time_ms' in stats
        assert 'current_entity_count' in stats
        assert 'avg_entity_count' in stats
        assert 'avg_collision_checks' in stats
    
    def test_clear(self):
        """测试清空"""
        # 添加数据
        for _ in range(5):
            self.monitor.update(0.016, 100, 50)
        
        # 清空
        self.monitor.clear()
        
        # 确认清空
        assert len(self.monitor.fps_history) == 0
        assert len(self.monitor.frame_time_history) == 0


class TestSpatialHashPerformance:
    """测试空间哈希性能"""
    
    def test_large_number_of_entities(self):
        """测试大量实体"""
        spatial_hash = SpatialHash(cell_size=100.0)
        
        # 插入1000个实体
        for i in range(1000):
            x = (i * 10) % 1000
            y = (i * 10) % 1000
            aabb = AABB(x=x, y=y, width=5, height=5)
            spatial_hash.insert(i, aabb)
        
        # 验证所有实体都在
        assert len(spatial_hash.entity_cells) == 1000
        
        # 查询性能测试
        results = spatial_hash.query_point(500, 500)
        # 应该只返回该单元中的实体，而不是全部1000个
        assert len(results) <= 100
    
    def test_query_performance(self):
        """测试查询性能"""
        spatial_hash = SpatialHash(cell_size=100.0)
        
        # 插入实体
        for i in range(100):
            aabb = AABB(x=i*10, y=i*10, width=5, height=5)
            spatial_hash.insert(i, aabb)
        
        # 多次查询
        for _ in range(100):
            results = spatial_hash.query_radius(500, 500, 200)
            # 查询应该很快，不会返回所有实体
            assert len(results) <= 50
