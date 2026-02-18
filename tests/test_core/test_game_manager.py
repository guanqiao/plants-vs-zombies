import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGameManager:
    """游戏管理器测试"""

    def test_game_manager_initialization(self):
        """测试游戏管理器初始化"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                assert manager is not None
                assert manager.running == True
                assert manager.sun_count == 50

    def test_game_manager_screen_size(self):
        """测试游戏窗口大小"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                assert manager.SCREEN_WIDTH == 900
                assert manager.SCREEN_HEIGHT == 600

    def test_game_manager_add_sun(self):
        """测试添加阳光"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                initial_sun = manager.sun_count
                manager.add_sun(25)
                assert manager.sun_count == initial_sun + 25

    def test_game_manager_spend_sun(self):
        """测试消耗阳光"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                manager.sun_count = 100
                result = manager.spend_sun(50)
                assert result == True
                assert manager.sun_count == 50

    def test_game_manager_spend_sun_insufficient(self):
        """测试阳光不足时消耗"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                manager.sun_count = 30
                result = manager.spend_sun(50)
                assert result == False
                assert manager.sun_count == 30

    def test_game_manager_quit(self):
        """测试退出游戏"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                assert manager.running == True
                manager.running = False
                assert manager.running == False

    def test_game_manager_reset(self):
        """测试重置游戏"""
        from src.core.game_manager import GameManager
        
        with patch('pygame.init'):
            with patch('pygame.display.set_mode') as mock_display:
                mock_display.return_value = MagicMock()
                manager = GameManager()
                
                manager.sun_count = 200
                manager.reset()
                assert manager.sun_count == 50
