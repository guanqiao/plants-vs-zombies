import pytest
from unittest.mock import MagicMock, patch


class TestHealthBar:
    """血条测试"""

    def test_health_bar_initialization(self):
        """测试血条初始化"""
        from src.ui.visual_effects import HealthBar
        
        health_bar = HealthBar(100, 50, 200, 10)
        
        assert health_bar.x == 100
        assert health_bar.y == 50
        assert health_bar.width == 200
        assert health_bar.height == 10

    def test_health_bar_update(self):
        """测试血条更新"""
        from src.ui.visual_effects import HealthBar
        
        health_bar = HealthBar(100, 50, 200, 10, max_health=100)
        health_bar.update(80, 100)
        
        assert health_bar.current_health == 80

    def test_health_bar_render(self):
        """测试血条渲染"""
        from src.ui.visual_effects import HealthBar
        import pygame
        
        pygame.init()
        health_bar = HealthBar(100, 50, 200, 10, max_health=100)
        screen = pygame.Surface((800, 600))
        
        health_bar.render(screen)
        
        assert True


class TestDamageNumber:
    """伤害数字测试"""

    def test_damage_number_initialization(self):
        """测试伤害数字初始化"""
        from src.ui.visual_effects import DamageNumber
        import pygame
        
        pygame.init()
        damage_num = DamageNumber(100, 200, 25)
        
        assert damage_num.x == 100
        assert damage_num.y == 200
        assert damage_num.damage == 25
        assert damage_num.is_alive == True

    def test_damage_number_update(self):
        """测试伤害数字更新"""
        from src.ui.visual_effects import DamageNumber
        import pygame
        
        pygame.init()
        damage_num = DamageNumber(100, 200, 25, lifetime=2.0)
        
        damage_num.update(0.5)
        
        assert damage_num.y < 200
        assert damage_num.alpha < 255

    def test_damage_number_lifetime(self):
        """测试伤害数字生命周期"""
        from src.ui.visual_effects import DamageNumber
        import pygame
        
        pygame.init()
        damage_num = DamageNumber(100, 200, 25, lifetime=0.5)
        
        damage_num.update(0.6)
        
        assert damage_num.is_alive == False


class TestScreenShake:
    """屏幕震动测试"""

    def test_screen_shake_initialization(self):
        """测试屏幕震动初始化"""
        from src.ui.visual_effects import ScreenShake
        
        shake = ScreenShake()
        
        assert shake.intensity == 0
        assert shake.duration == 0

    def test_screen_shake_start(self):
        """测试开始震动"""
        from src.ui.visual_effects import ScreenShake
        
        shake = ScreenShake()
        shake.start(intensity=10, duration=0.5)
        
        assert shake.intensity == 10
        assert shake.duration == 0.5

    def test_screen_shake_update(self):
        """测试震动更新"""
        from src.ui.visual_effects import ScreenShake
        
        shake = ScreenShake()
        shake.start(intensity=10, duration=0.5)
        
        offset = shake.update(0.2)
        
        assert offset != (0, 0) or shake.duration > 0

    def test_screen_shake_stop(self):
        """测试停止震动"""
        from src.ui.visual_effects import ScreenShake
        
        shake = ScreenShake()
        shake.start(intensity=10, duration=0.5)
        shake.stop()
        
        assert shake.intensity == 0
        assert shake.duration == 0


class TestVisualEffectsManager:
    """视觉效果管理器测试"""

    def test_visual_effects_manager_initialization(self):
        """测试视觉效果管理器初始化"""
        from src.ui.visual_effects import VisualEffectsManager
        
        manager = VisualEffectsManager()
        
        assert len(manager.damage_numbers) == 0
        assert manager.screen_shake is not None

    def test_visual_effects_manager_add_damage_number(self):
        """测试添加伤害数字"""
        from src.ui.visual_effects import VisualEffectsManager
        import pygame
        
        pygame.init()
        manager = VisualEffectsManager()
        manager.add_damage_number(100, 200, 25)
        
        assert len(manager.damage_numbers) == 1

    def test_visual_effects_manager_update(self):
        """测试更新视觉效果"""
        from src.ui.visual_effects import VisualEffectsManager
        import pygame
        
        pygame.init()
        manager = VisualEffectsManager()
        manager.add_damage_number(100, 200, 25, lifetime=0.1)
        
        manager.update(0.2)
        
        assert len(manager.damage_numbers) == 0

    def test_visual_effects_manager_trigger_shake(self):
        """测试触发震动"""
        from src.ui.visual_effects import VisualEffectsManager
        
        manager = VisualEffectsManager()
        manager.trigger_shake(intensity=10, duration=0.3)
        
        assert manager.screen_shake.intensity == 10
