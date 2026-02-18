"""
测试音效管理器
"""

import pytest
from src.arcade_game.audio_manager import AudioManager, SoundType, get_audio_manager, init_audio_manager


class TestAudioManager:
    """测试音效管理器"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.audio = AudioManager()
    
    def test_initialization(self):
        """测试初始化"""
        assert self.audio.master_volume == 1.0
        assert self.audio.sfx_volume == 1.0
        assert self.audio.music_volume == 0.5
        assert not self.audio.is_muted
        assert self.audio.current_music is None
    
    def test_set_master_volume(self):
        """测试设置主音量"""
        self.audio.set_master_volume(0.5)
        assert self.audio.master_volume == 0.5
        
        # 测试边界值
        self.audio.set_master_volume(1.5)
        assert self.audio.master_volume == 1.0
        
        self.audio.set_master_volume(-0.5)
        assert self.audio.master_volume == 0.0
    
    def test_set_sfx_volume(self):
        """测试设置音效音量"""
        self.audio.set_sfx_volume(0.7)
        assert self.audio.sfx_volume == 0.7
        
        # 测试边界值
        self.audio.set_sfx_volume(2.0)
        assert self.audio.sfx_volume == 1.0
    
    def test_set_music_volume(self):
        """测试设置音乐音量"""
        self.audio.set_music_volume(0.3)
        assert self.audio.music_volume == 0.3
    
    def test_toggle_mute(self):
        """测试切换静音"""
        # 初始状态：未静音
        assert not self.audio.is_muted
        
        # 切换静音
        result = self.audio.toggle_mute()
        assert result is True
        assert self.audio.is_muted
        
        # 再次切换
        result = self.audio.toggle_mute()
        assert result is False
        assert not self.audio.is_muted
    
    def test_mute(self):
        """测试静音"""
        self.audio.mute()
        assert self.audio.is_muted is True
    
    def test_unmute(self):
        """测试取消静音"""
        self.audio.mute()
        self.audio.unmute()
        assert self.audio.is_muted is False
    
    def test_play_sound_when_muted(self):
        """测试静音时不播放音效"""
        self.audio.mute()
        # 静音时不应该抛出异常
        self.audio.play_sound(SoundType.PLANT)
        # 如果到这里没有异常，测试通过
        assert True
    
    def test_load_sound_invalid_path(self):
        """测试加载无效路径的音效"""
        result = self.audio.load_sound(SoundType.PLANT, "invalid/path/sound.wav")
        assert result is False
    
    def test_convenience_methods(self):
        """测试便捷方法"""
        # 静音状态下调用，不会抛出异常
        self.audio.mute()
        
        # 测试所有便捷方法
        self.audio.play_plant_sound()
        self.audio.play_shoot_sound()
        self.audio.play_hit_sound()
        self.audio.play_collect_sun_sound()
        self.audio.play_zombie_death_sound()
        self.audio.play_zombie_eat_sound()
        self.audio.play_game_over_sound()
        self.audio.play_victory_sound()
        self.audio.play_button_click_sound()
        
        # 如果到这里没有异常，测试通过
        assert True


class TestGlobalAudioManager:
    """测试全局音效管理器"""
    
    def test_get_audio_manager(self):
        """测试获取全局实例"""
        # 清除之前的实例
        import src.arcade_game.audio_manager as audio_module
        audio_module._audio_manager = None
        
        # 获取实例
        manager1 = get_audio_manager()
        assert manager1 is not None
        
        # 再次获取应该是同一个实例
        manager2 = get_audio_manager()
        assert manager1 is manager2
    
    def test_init_audio_manager(self):
        """测试初始化音效管理器"""
        # 初始化
        manager = init_audio_manager()
        assert manager is not None
        
        # 再次初始化应该是新实例
        import src.arcade_game.audio_manager as audio_module
        old_manager = audio_module._audio_manager
        new_manager = init_audio_manager()
        assert new_manager is not old_manager


class TestSoundType:
    """测试音效类型枚举"""
    
    def test_sound_type_values(self):
        """测试音效类型值"""
        assert SoundType.PLANT is not None
        assert SoundType.SHOOT is not None
        assert SoundType.HIT is not None
        assert SoundType.COLLECT_SUN is not None
        assert SoundType.ZOMBIE_DEATH is not None
        assert SoundType.ZOMBIE_EAT is not None
        assert SoundType.GAME_OVER is not None
        assert SoundType.VICTORY is not None
        assert SoundType.BUTTON_CLICK is not None
    
    def test_sound_type_uniqueness(self):
        """测试音效类型唯一性"""
        sound_types = list(SoundType)
        assert len(sound_types) == len(set(sound_types))
