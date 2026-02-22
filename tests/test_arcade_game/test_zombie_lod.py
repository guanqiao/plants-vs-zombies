"""
测试僵尸LOD系统
"""

import pytest
from src.arcade_game.zombie_lod_system import (
    ZombieLODSystem, LODLevel, LODConfig, ZombieLODState, get_zombie_lod_system
)


class TestLODLevel:
    """测试LOD等级枚举"""
    
    def test_lod_levels_exist(self):
        """测试所有LOD等级存在"""
        assert LODLevel.HIGH is not None
        assert LODLevel.MEDIUM is not None
        assert LODLevel.LOW is not None
        assert LODLevel.CULLED is not None


class TestLODConfig:
    """测试LOD配置"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = LODConfig()
        assert config.high_distance == 200.0
        assert config.medium_distance == 400.0
        assert config.low_distance == 600.0
        assert config.high_fps == 60
        assert config.medium_fps == 30
        assert config.low_fps == 15
    
    def test_config_customization(self):
        """测试自定义配置"""
        config = LODConfig(
            high_distance=100.0,
            medium_distance=200.0,
            low_fps=10
        )
        assert config.high_distance == 100.0
        assert config.medium_distance == 200.0
        assert config.low_fps == 10


class TestZombieLODState:
    """测试僵尸LOD状态"""
    
    def test_initial_state(self):
        """测试初始状态"""
        state = ZombieLODState()
        assert state.current_level == LODLevel.HIGH
        assert state.distance_to_camera == 0.0
        assert state.is_on_screen is True
    
    def test_lod_level_transition(self):
        """测试LOD等级切换"""
        state = ZombieLODState()
        config = LODConfig()
        
        # 设置距离为中等
        state.distance_to_camera = 300.0
        state.update(0.1, config)
        
        assert state.current_level == LODLevel.MEDIUM
    
    def test_culled_state(self):
        """测试剔除状态"""
        state = ZombieLODState()
        config = LODConfig()
        
        # 设置距离超过低质量阈值
        state.distance_to_camera = 700.0
        state.update(0.1, config)
        
        assert state.current_level == LODLevel.CULLED
        assert not state.should_render()
    
    def test_off_screen_culling(self):
        """测试屏幕外剔除"""
        state = ZombieLODState()
        state.is_on_screen = False
        
        assert not state.should_render()
    
    def test_animation_skip(self):
        """测试动画跳帧"""
        state = ZombieLODState()
        config = LODConfig()
        
        # 设置为中等质量（30fps）
        state.distance_to_camera = 300.0
        state.update(0.1, config)
        
        assert state.current_level == LODLevel.MEDIUM
        # 中等质量应该每2帧渲染一次
        assert state.render_every_n_frames == 2


class TestZombieLODSystem:
    """测试僵尸LOD系统"""
    
    def test_system_creation(self):
        """测试系统创建"""
        system = ZombieLODSystem()
        assert system is not None
    
    def test_system_with_screen_size(self):
        """测试带屏幕大小的系统创建"""
        system = ZombieLODSystem(screen_width=800, screen_height=600)
        assert system._screen_width == 800
        assert system._screen_height == 600
    
    def test_update_and_get_level(self):
        """测试更新和获取等级"""
        system = ZombieLODSystem()
        # 设置摄像机位置在僵尸附近
        system.set_camera_position(100, 100)
        
        # 更新近距离僵尸
        system.update(0.1, 1, zombie_x=100, zombie_y=100)
        level = system.get_lod_level(1)
        
        assert level == LODLevel.HIGH
    
    def test_should_render(self):
        """测试是否应该渲染"""
        system = ZombieLODSystem()
        system.set_camera_position(100, 100)
        
        # 近距离僵尸应该渲染
        system.update(0.1, 1, zombie_x=100, zombie_y=100)
        assert system.should_render(1)
        
        # 远距离僵尸可能被剔除
        system.set_camera_position(0, 0)
        system.update(0.1, 2, zombie_x=1000, zombie_y=100)
        # 根据配置，这个距离可能被剔除
    
    def test_should_update_animation(self):
        """测试是否应该更新动画"""
        system = ZombieLODSystem()
        
        system.update(0.1, 1, zombie_x=100, zombie_y=100)
        # 高质量应该更新动画
        assert system.should_update_animation(1)
    
    def test_feature_toggles(self):
        """测试特效开关"""
        system = ZombieLODSystem()
        system.set_camera_position(100, 100)
        config = system.get_config()
        
        # 近距离应该启用所有特效
        system.update(0.1, 1, zombie_x=100, zombie_y=100)
        assert system.should_render_shadow(1) == config.enable_shadow_high
        assert system.should_render_dust(1) == config.enable_dust_high
        assert system.should_render_expression(1) == config.enable_expression_high
    
    def test_camera_position(self):
        """测试摄像机位置设置"""
        system = ZombieLODSystem()
        system.set_camera_position(400, 300)
        
        assert system._camera_x == 400
        assert system._camera_y == 300
    
    def test_screen_size_update(self):
        """测试屏幕大小更新"""
        system = ZombieLODSystem()
        system.set_screen_size(1024, 768)
        
        assert system._screen_width == 1024
        assert system._screen_height == 768
    
    def test_config_update(self):
        """测试配置更新"""
        system = ZombieLODSystem()
        system.update_config(high_distance=150.0)
        
        config = system.get_config()
        assert config.high_distance == 150.0
    
    def test_remove_zombie(self):
        """测试移除僵尸"""
        system = ZombieLODSystem()
        system.update(0.1, 1, zombie_x=100, zombie_y=100)
        
        system.remove_zombie(1)
        
        assert 1 not in system._states
    
    def test_clear(self):
        """测试清除所有状态"""
        system = ZombieLODSystem()
        for i in range(5):
            system.update(0.1, i, zombie_x=100 + i * 50, zombie_y=100)
        
        system.clear()
        
        assert len(system._states) == 0
    
    def test_get_stats(self):
        """测试获取统计信息"""
        system = ZombieLODSystem()
        
        # 设置摄像机位置，使不同距离的僵尸落在不同LOD等级
        system.set_camera_position(100, 100)
        
        # 创建不同距离的僵尸（相对于摄像机）
        system.update(0.1, 1, zombie_x=100, zombie_y=100)   # HIGH (距离0)
        system.update(0.1, 2, zombie_x=350, zombie_y=100)   # MEDIUM (距离250)
        system.update(0.1, 3, zombie_x=550, zombie_y=100)   # LOW (距离450)
        system.update(0.1, 4, zombie_x=750, zombie_y=100)   # CULLED (距离650)
        
        stats = system.get_stats()
        
        assert stats['total'] == 4
        assert stats['high'] >= 1
        assert stats['culled'] >= 1


class TestSingleton:
    """测试单例模式"""
    
    def test_get_lod_system_singleton(self):
        """测试LOD系统单例"""
        system1 = get_zombie_lod_system()
        system2 = get_zombie_lod_system()
        
        assert system1 is system2


class TestIntegration:
    """集成测试"""
    
    def test_full_lod_sequence(self):
        """测试完整的LOD序列"""
        system = ZombieLODSystem()
        zombie_id = 1
        
        # 设置摄像机位置作为参考点
        system.set_camera_position(0, 0)
        
        # 1. 僵尸在近距离 - 高质量
        system.update(0.1, zombie_id, zombie_x=100, zombie_y=100)
        assert system.get_lod_level(zombie_id) == LODLevel.HIGH
        assert system.should_render(zombie_id)
        assert system.should_render_shadow(zombie_id)
        assert system.should_render_dust(zombie_id)
        assert system.should_render_expression(zombie_id)
        
        # 2. 僵尸移动到中等距离
        system.update(0.1, zombie_id, zombie_x=300, zombie_y=100)
        assert system.get_lod_level(zombie_id) == LODLevel.MEDIUM
        # 中等质量可能禁用某些特效
        
        # 3. 僵尸移动到远距离
        system.update(0.1, zombie_id, zombie_x=500, zombie_y=100)
        assert system.get_lod_level(zombie_id) == LODLevel.LOW
        
        # 4. 僵尸移动到极远距离 - 被剔除
        system.update(0.1, zombie_id, zombie_x=700, zombie_y=100)
        assert system.get_lod_level(zombie_id) == LODLevel.CULLED
        assert not system.should_render(zombie_id)
    
    def test_multiple_zombies_different_distances(self):
        """测试多个僵尸不同距离"""
        system = ZombieLODSystem()
        # 设置摄像机位置
        system.set_camera_position(0, 0)
        
        # 创建不同距离的僵尸
        distances = [100, 250, 450, 650]
        expected_levels = [
            LODLevel.HIGH,
            LODLevel.MEDIUM,
            LODLevel.LOW,
            LODLevel.CULLED
        ]
        
        for i, (dist, expected) in enumerate(zip(distances, expected_levels)):
            system.update(0.1, i, zombie_x=dist, zombie_y=100)
            assert system.get_lod_level(i) == expected, f"僵尸{i}在距离{dist}应该是{expected}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
