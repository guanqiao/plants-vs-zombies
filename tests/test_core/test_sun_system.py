import pytest
from unittest.mock import MagicMock


class TestSun:
    """阳光测试"""

    def test_sun_initialization(self):
        """测试阳光初始化"""
        from src.core.sun_system import Sun
        
        sun = Sun(100, 200)
        
        assert sun.x == 100
        assert sun.y == 200
        assert sun.value == 25
        assert sun.is_collected == False

    def test_sun_get_rect(self):
        """测试阳光获取碰撞矩形"""
        from src.core.sun_system import Sun
        
        sun = Sun(100, 200)
        rect = sun.get_rect()
        
        assert rect.centerx == 100
        assert rect.centery == 200

    def test_sun_update_falling(self):
        """测试阳光下落"""
        from src.core.sun_system import Sun
        
        sun = Sun(100, 50)
        sun.target_y = 300
        
        sun.update(1.0)
        assert sun.y > 50

    def test_sun_collect(self):
        """测试收集阳光"""
        from src.core.sun_system import Sun
        
        sun = Sun(100, 200)
        assert sun.is_collected == False
        
        sun.collect()
        assert sun.is_collected == True

    def test_sun_lifetime(self):
        """测试阳光生命周期"""
        from src.core.sun_system import Sun
        
        sun = Sun(100, 200)
        sun.lifetime = 5.0
        
        sun.update(6.0)
        assert sun.is_expired()


class TestSunSystem:
    """阳光系统测试"""

    def test_sun_system_initialization(self):
        """测试阳光系统初始化"""
        from src.core.sun_system import SunSystem
        
        system = SunSystem()
        assert len(system.suns) == 0
        assert system.spawn_timer >= 0

    def test_sun_system_spawn_sun(self):
        """测试生成阳光"""
        from src.core.sun_system import SunSystem
        
        system = SunSystem()
        system.spawn_interval = 0.1
        
        system.update(0.2, MagicMock())
        assert len(system.suns) > 0

    def test_sun_system_collect_sun(self):
        """测试收集阳光"""
        from src.core.sun_system import SunSystem, Sun
        from unittest.mock import MagicMock
        
        system = SunSystem()
        sun = Sun(100, 200)
        system.suns.append(sun)
        
        game_manager = MagicMock()
        game_manager.sun_count = 50
        
        result = system.collect_sun(100, 200, game_manager)
        assert result == True
        assert sun.is_collected == True

    def test_sun_system_collect_sun_miss(self):
        """测试未点击到阳光"""
        from src.core.sun_system import SunSystem, Sun
        from unittest.mock import MagicMock
        
        system = SunSystem()
        sun = Sun(100, 200)
        system.suns.append(sun)
        
        game_manager = MagicMock()
        
        result = system.collect_sun(500, 500, game_manager)
        assert result == False
        assert sun.is_collected == False

    def test_sun_system_remove_expired_suns(self):
        """测试移除过期阳光"""
        from src.core.sun_system import SunSystem, Sun
        
        system = SunSystem()
        sun = Sun(100, 200)
        sun.lifetime = 0
        system.suns.append(sun)
        
        system.update(0.1, MagicMock())
        assert len(system.suns) == 0

    def test_sun_system_add_sun_from_plant(self):
        """测试植物产生阳光"""
        from src.core.sun_system import SunSystem
        
        system = SunSystem()
        
        system.add_sun_from_plant(200, 150)
        assert len(system.suns) == 1
        assert system.suns[0].value == 25
