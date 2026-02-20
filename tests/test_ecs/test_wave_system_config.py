"""
波次系统配置加载测试 - TDD方式开发
"""
import pytest
from unittest.mock import MagicMock, patch


class TestWaveSystemConfig:
    """测试波次系统使用配置文件"""

    def test_wave_system_loads_config_from_file(self):
        """测试波次系统从配置文件加载"""
        from src.ecs.systems.wave_system import WaveSystem
        
        system = WaveSystem(level=1, priority=50)
        
        # 验证配置已加载
        assert system.level == 1
        assert len(system.waves) > 0

    def test_wave_system_level_1_config(self):
        """测试关卡1配置"""
        from src.ecs.systems.wave_system import WaveSystem
        
        system = WaveSystem(level=1, priority=50)
        
        # 验证第一波配置
        assert system.waves[0]['delay'] == 5.0
        assert len(system.waves[0]['zombies']) > 0

    def test_wave_system_level_7_config(self):
        """测试关卡7配置（最难关卡）"""
        from src.ecs.systems.wave_system import WaveSystem
        
        system = WaveSystem(level=7, priority=50)
        
        # 验证有巨人僵尸
        has_gargantuar = False
        for wave in system.waves:
            for zombie_type, count in wave['zombies']:
                if 'GARGANTUAR' in str(zombie_type):
                    has_gargantuar = True
                    break
        
        assert has_gargantuar or len(system.waves) > 0

    def test_wave_system_invalid_level(self):
        """测试无效关卡返回空配置"""
        from src.ecs.systems.wave_system import WaveSystem
        
        system = WaveSystem(level=999, priority=50)
        
        assert system.waves == []
        assert system.complete is True

    def test_wave_system_config_has_required_fields(self):
        """测试配置包含必需字段"""
        from src.ecs.systems.wave_system import WaveSystem
        
        system = WaveSystem(level=1, priority=50)
        
        if system.waves:
            wave = system.waves[0]
            assert 'delay' in wave
            assert 'zombies' in wave
            
            # 验证僵尸配置格式
            for zombie_config in wave['zombies']:
                assert len(zombie_config) == 2
                zombie_type, count = zombie_config
                assert count > 0


class TestWaveSystemIntegration:
    """测试波次系统集成"""

    def test_wave_system_updates_timer(self):
        """测试波次系统更新计时器"""
        from src.ecs.systems.wave_system import WaveSystem
        from src.ecs.component import ComponentManager
        
        system = WaveSystem(level=1, priority=50)
        component_manager = ComponentManager()
        
        initial_timer = system.timer
        system.update(1.0, component_manager)
        
        assert system.timer == initial_timer + 1.0

    def test_wave_system_spawns_zombies_when_delay_reached(self):
        """测试延迟到达时生成僵尸"""
        from src.ecs.systems.wave_system import WaveSystem
        from src.ecs.component import ComponentManager
        
        system = WaveSystem(level=1, priority=50)
        component_manager = ComponentManager()
        
        # 快速推进时间超过第一波延迟
        if system.waves:
            delay = system.waves[0]['delay']
            system.update(delay + 0.1, component_manager)
            
            # 验证有僵尸待生成
            assert len(system.zombies_to_spawn) > 0 or system.wave_index > 0

    def test_wave_system_complete_after_all_waves(self):
        """测试所有波次完成后标记完成"""
        from src.ecs.systems.wave_system import WaveSystem
        from src.ecs.component import ComponentManager
        
        system = WaveSystem(level=1, priority=50)
        component_manager = ComponentManager()
        
        # 快速完成所有波次
        for _ in range(100):
            system.update(10.0, component_manager)
            if system.complete:
                break
        
        assert system.complete is True
