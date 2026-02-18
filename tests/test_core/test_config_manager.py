import pytest
from pathlib import Path
import tempfile
import os


class TestConfigManager:
    """配置管理器测试"""

    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        
        assert config is not None

    def test_config_manager_load_plant_config(self):
        """测试加载植物配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        plant_config = config.get_plant_config('sunflower')
        
        assert plant_config is not None
        assert 'cost' in plant_config
        assert 'health' in plant_config

    def test_config_manager_load_zombie_config(self):
        """测试加载僵尸配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        zombie_config = config.get_zombie_config('normal')
        
        assert zombie_config is not None
        assert 'health' in zombie_config
        assert 'speed' in zombie_config

    def test_config_manager_get_nonexistent_plant(self):
        """测试获取不存在的植物配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        plant_config = config.get_plant_config('nonexistent_plant')
        
        assert plant_config is None

    def test_config_manager_get_nonexistent_zombie(self):
        """测试获取不存在的僵尸配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        zombie_config = config.get_zombie_config('nonexistent_zombie')
        
        assert zombie_config is None

    def test_config_manager_get_all_plants(self):
        """测试获取所有植物配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        plants = config.get_all_plants()
        
        assert plants is not None
        assert len(plants) > 0

    def test_config_manager_get_all_zombies(self):
        """测试获取所有僵尸配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        zombies = config.get_all_zombies()
        
        assert zombies is not None
        assert len(zombies) > 0

    def test_config_manager_get_game_config(self):
        """测试获取游戏配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        game_config = config.get_game_config()
        
        assert game_config is not None
        assert 'screen_width' in game_config
        assert 'screen_height' in game_config
        assert 'fps' in game_config

    def test_config_manager_get_level_config(self):
        """测试获取关卡配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        level_config = config.get_level_config(1)
        
        assert level_config is not None
        assert 'waves' in level_config

    def test_config_manager_get_nonexistent_level(self):
        """测试获取不存在的关卡配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        level_config = config.get_level_config(999)
        
        assert level_config is None

    def test_config_manager_reload(self):
        """测试重新加载配置"""
        from src.core.config_manager import ConfigManager
        
        config = ConfigManager()
        config.reload()
        
        plant_config = config.get_plant_config('sunflower')
        assert plant_config is not None
