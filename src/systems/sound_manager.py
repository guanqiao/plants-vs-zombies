import pygame
from typing import Dict, Optional


class SoundManager:
    """音效管理器 - 管理游戏音效和背景音乐"""
    
    def __init__(self):
        try:
            pygame.mixer.init()
        except:
            pass
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_enabled = True
        self.sfx_enabled = True
        self.master_volume = 1.0
        self.current_music: Optional[str] = None
    
    def load_sound(self, name: str, filepath: str) -> bool:
        """加载音效文件"""
        try:
            sound = pygame.mixer.Sound(filepath)
            self.sounds[name] = sound
            return True
        except:
            self.sounds[name] = None
            return False
    
    def play_sound(self, name: str):
        """播放音效"""
        if not self.sfx_enabled:
            return
        
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].play()
    
    def stop_sound(self, name: str):
        """停止音效"""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].stop()
    
    def set_volume(self, name: str, volume: float):
        """设置单个音效音量"""
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].set_volume(volume * self.master_volume)
    
    def set_master_volume(self, volume: float):
        """设置主音量"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        for sound in self.sounds.values():
            if sound:
                current_volume = sound.get_volume()
                sound.set_volume(current_volume * self.master_volume)
    
    def toggle_sfx(self):
        """切换音效开关"""
        self.sfx_enabled = not self.sfx_enabled
    
    def toggle_music(self):
        """切换音乐开关"""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
    
    def play_music(self, filepath: str, loops: int = -1):
        """播放背景音乐"""
        if not self.music_enabled:
            return
        
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(loops)
            self.current_music = filepath
        except:
            pass
    
    def stop_music(self):
        """停止背景音乐"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except:
            pass
    
    def pause_music(self):
        """暂停背景音乐"""
        try:
            pygame.mixer.music.pause()
        except:
            pass
    
    def resume_music(self):
        """恢复背景音乐"""
        if self.music_enabled:
            try:
                pygame.mixer.music.unpause()
            except:
                pass
    
    def preload_game_sounds(self):
        """预加载游戏常用音效"""
        sound_files = {
            'shoot': 'assets/sounds/shoot.wav',
            'explosion': 'assets/sounds/explosion.wav',
            'sun_collect': 'assets/sounds/sun_collect.wav',
            'zombie_die': 'assets/sounds/zombie_die.wav',
            'plant': 'assets/sounds/plant.wav',
            'splat': 'assets/sounds/splat.wav',
        }
        
        for name, filepath in sound_files.items():
            self.load_sound(name, filepath)
