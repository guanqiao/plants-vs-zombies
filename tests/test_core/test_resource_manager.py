import pytest
from unittest.mock import Mock, patch, MagicMock
import pygame


class TestResourceManager:
    """资源管理器测试"""

    def test_resource_manager_initialization(self):
        """测试资源管理器初始化"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        assert manager is not None

    def test_resource_manager_singleton(self):
        """测试资源管理器单例模式"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager1 = ResourceManager()
            manager2 = ResourceManager()
        
        assert manager1 is manager2

    def test_resource_manager_load_image(self):
        """测试加载图片"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        mock_surface = MagicMock()
        with patch('pygame.image.load', return_value=mock_surface):
            with patch('os.path.exists', return_value=True):
                result = manager.load_image('test.png')
        
        assert result is not None

    def test_resource_manager_load_image_cached(self):
        """测试图片缓存"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        manager.clear_cache()
        
        mock_surface = MagicMock()
        with patch('pygame.image.load', return_value=mock_surface) as mock_load:
            with patch('os.path.exists', return_value=True):
                result1 = manager.load_image('test.png')
                result2 = manager.load_image('test.png')
        
        assert mock_load.call_count == 1
        assert result1 is result2

    def test_resource_manager_load_sound(self):
        """测试加载音效"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        mock_sound = MagicMock()
        with patch('pygame.mixer.Sound', return_value=mock_sound):
            with patch('os.path.exists', return_value=True):
                result = manager.load_sound('test.wav')
        
        assert result is not None

    def test_resource_manager_load_sound_cached(self):
        """测试音效缓存"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        manager.clear_cache()
        
        mock_sound = MagicMock()
        with patch('pygame.mixer.Sound', return_value=mock_sound) as mock_sound_func:
            with patch('os.path.exists', return_value=True):
                result1 = manager.load_sound('test.wav')
                result2 = manager.load_sound('test.wav')
        
        assert mock_sound_func.call_count == 1
        assert result1 is result2

    def test_resource_manager_load_nonexistent_image(self):
        """测试加载不存在的图片"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        with patch('os.path.exists', return_value=False):
            result = manager.load_image('nonexistent.png')
        
        assert result is None

    def test_resource_manager_load_nonexistent_sound(self):
        """测试加载不存在的音效"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        with patch('os.path.exists', return_value=False):
            result = manager.load_sound('nonexistent.wav')
        
        assert result is None

    def test_resource_manager_clear_cache(self):
        """测试清除缓存"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager()
        
        mock_surface = MagicMock()
        with patch('pygame.image.load', return_value=mock_surface):
            with patch('os.path.exists', return_value=True):
                manager.load_image('test.png')
        
        manager.clear_cache()
        
        assert len(manager._image_cache) == 0
        assert len(manager._sound_cache) == 0

    def test_resource_manager_get_instance(self):
        """测试获取实例"""
        from src.core.resource_manager import ResourceManager
        ResourceManager._instance = None
        
        with patch('pygame.mixer.init'):
            manager = ResourceManager.get_instance()
        
        assert manager is not None
