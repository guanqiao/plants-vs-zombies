"""
测试植物配置管理器
"""

import pytest
from src.core.plant_config import (
    PlantConfig, PlantConfigManager,
    get_plant_config_manager, get_plant_config
)
from src.ecs.components import PlantType


class TestPlantConfig:
    """测试植物配置数据类"""
    
    def test_default_values(self):
        """测试默认值"""
        config = PlantConfig()
        
        assert config.name == ""
        assert config.cost == 100
        assert config.health == 100
        assert config.width == 60.0
        assert config.height == 80.0
        assert config.color == (0, 200, 0)
        assert config.is_shooter is False
        assert config.is_explosive is False
        assert config.is_sun_producer is False
    
    def test_custom_values(self):
        """测试自定义值"""
        config = PlantConfig(
            name="豌豆射手",
            cost=100,
            health=100,
            is_shooter=True
        )
        
        assert config.name == "豌豆射手"
        assert config.cost == 100
        assert config.is_shooter is True


class TestPlantConfigManager:
    """测试植物配置管理器"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        # 重置单例状态
        PlantConfigManager._instance = None
        PlantConfigManager._initialized = False
        self.manager = PlantConfigManager()
    
    def test_singleton(self):
        """测试单例模式"""
        manager1 = PlantConfigManager()
        manager2 = PlantConfigManager()
        
        assert manager1 is manager2
    
    def test_get_config(self):
        """测试获取配置"""
        config = self.manager.get_config(PlantType.PEASHOOTER)
        
        assert isinstance(config, PlantConfig)
        assert config.name == "豌豆射手"
        assert config.cost == 100
        assert config.is_shooter is True
    
    def test_get_all_configs(self):
        """测试获取所有配置"""
        configs = self.manager.get_all_configs()
        
        assert len(configs) > 0
        assert PlantType.PEASHOOTER in configs
        assert PlantType.SUNFLOWER in configs
    
    def test_get_cost(self):
        """测试获取成本"""
        cost = self.manager.get_cost(PlantType.SUNFLOWER)
        
        assert cost == 50
    
    def test_get_health(self):
        """测试获取生命值"""
        health = self.manager.get_health(PlantType.WALLNUT)
        
        assert health == 400
    
    def test_get_size(self):
        """测试获取尺寸"""
        width, height = self.manager.get_size(PlantType.PEASHOOTER)
        
        assert width == 60.0
        assert height == 80.0
    
    def test_get_color(self):
        """测试获取颜色"""
        color = self.manager.get_color(PlantType.SUNFLOWER)
        
        assert color == (255, 255, 0)
    
    def test_is_shooter(self):
        """测试射手判断"""
        assert self.manager.is_shooter(PlantType.PEASHOOTER) is True
        assert self.manager.is_shooter(PlantType.SUNFLOWER) is False
    
    def test_is_explosive(self):
        """测试爆炸类判断"""
        assert self.manager.is_explosive(PlantType.CHERRY_BOMB) is True
        assert self.manager.is_explosive(PlantType.PEASHOOTER) is False
    
    def test_is_sun_producer(self):
        """测试阳光产生判断"""
        assert self.manager.is_sun_producer(PlantType.SUNFLOWER) is True
        assert self.manager.is_sun_producer(PlantType.PEASHOOTER) is False


class TestGlobalFunctions:
    """测试全局函数"""
    
    def test_get_plant_config_manager(self):
        """测试获取全局管理器"""
        manager = get_plant_config_manager()
        
        assert isinstance(manager, PlantConfigManager)
        
        # 再次获取应该是同一个实例
        manager2 = get_plant_config_manager()
        assert manager is manager2
    
    def test_get_plant_config(self):
        """测试便捷获取配置函数"""
        config = get_plant_config(PlantType.PEASHOOTER)
        
        assert isinstance(config, PlantConfig)
        assert config.name == "豌豆射手"


class TestConfigLoading:
    """测试配置加载"""
    
    def test_sunflower_config(self):
        """测试向日葵配置"""
        config = get_plant_config(PlantType.SUNFLOWER)
        
        assert config.name == "向日葵"
        assert config.cost == 50
        assert config.health == 100
        assert config.is_sun_producer is True
        assert config.sun_production_interval == 24.0
        assert config.sun_amount == 25
    
    def test_peashooter_config(self):
        """测试豌豆射手配置"""
        config = get_plant_config(PlantType.PEASHOOTER)
        
        assert config.name == "豌豆射手"
        assert config.cost == 100
        assert config.is_shooter is True
        assert config.fire_rate == 1.5
        assert config.projectile_damage == 20
        assert config.projectile_speed == 400.0
    
    def test_cherry_bomb_config(self):
        """测试樱桃炸弹配置"""
        config = get_plant_config(PlantType.CHERRY_BOMB)
        
        assert config.name == "樱桃炸弹"
        assert config.cost == 150
        assert config.is_explosive is True
        assert config.explosion_radius == 100.0
        assert config.explosion_damage == 1800
    
    def test_threepeater_config(self):
        """测试三线射手配置"""
        config = get_plant_config(PlantType.THREEPEATER)
        
        assert config.name == "三线射手"
        assert config.cost == 325
        assert config.is_shooter is True
        assert config.rows == 3
