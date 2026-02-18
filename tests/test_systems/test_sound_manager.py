import pytest
from unittest.mock import MagicMock, patch


class TestSoundManager:
    """音效管理器测试"""

    def test_sound_manager_initialization(self):
        """测试音效管理器初始化"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            manager = SoundManager()
            assert manager is not None
            assert manager.sounds == {}
            assert manager.music_enabled == True
            assert manager.sfx_enabled == True

    def test_sound_manager_load_sound(self):
        """测试加载音效"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.Sound') as mock_sound:
                mock_sound.return_value = MagicMock()
                manager = SoundManager()
                
                manager.load_sound('shoot', 'shoot.wav')
                assert 'shoot' in manager.sounds

    def test_sound_manager_play_sound(self):
        """测试播放音效"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.Sound') as mock_sound:
                mock_sound_instance = MagicMock()
                mock_sound.return_value = mock_sound_instance
                manager = SoundManager()
                
                manager.load_sound('shoot', 'shoot.wav')
                manager.play_sound('shoot')
                
                mock_sound_instance.play.assert_called_once()

    def test_sound_manager_play_sound_disabled(self):
        """测试禁用音效时不播放"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.Sound') as mock_sound:
                mock_sound_instance = MagicMock()
                mock_sound.return_value = mock_sound_instance
                manager = SoundManager()
                
                manager.sfx_enabled = False
                manager.load_sound('shoot', 'shoot.wav')
                manager.play_sound('shoot')
                
                mock_sound_instance.play.assert_not_called()

    def test_sound_manager_set_volume(self):
        """测试设置音量"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.Sound') as mock_sound:
                mock_sound_instance = MagicMock()
                mock_sound.return_value = mock_sound_instance
                manager = SoundManager()
                
                manager.load_sound('shoot', 'shoot.wav')
                manager.set_volume('shoot', 0.5)
                
                mock_sound_instance.set_volume.assert_called_with(0.5)

    def test_sound_manager_set_master_volume(self):
        """测试设置主音量"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            manager = SoundManager()
            manager.set_master_volume(0.8)
            assert manager.master_volume == 0.8

    def test_sound_manager_toggle_sfx(self):
        """测试切换音效开关"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            manager = SoundManager()
            
            assert manager.sfx_enabled == True
            manager.toggle_sfx()
            assert manager.sfx_enabled == False
            manager.toggle_sfx()
            assert manager.sfx_enabled == True

    def test_sound_manager_toggle_music(self):
        """测试切换音乐开关"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            manager = SoundManager()
            
            assert manager.music_enabled == True
            manager.toggle_music()
            assert manager.music_enabled == False

    def test_sound_manager_play_music(self):
        """测试播放背景音乐"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.music') as mock_music:
                manager = SoundManager()
                manager.play_music('background.mp3')
                
                mock_music.load.assert_called()
                mock_music.play.assert_called()

    def test_sound_manager_stop_music(self):
        """测试停止背景音乐"""
        from src.systems.sound_manager import SoundManager
        
        with patch('pygame.mixer.init'):
            with patch('pygame.mixer.music') as mock_music:
                manager = SoundManager()
                manager.stop_music()
                
                mock_music.stop.assert_called()
