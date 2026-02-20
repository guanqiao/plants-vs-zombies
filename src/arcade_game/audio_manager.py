"""
音效管理器 - 管理游戏中的所有音效和音乐

包括：
- 音效播放
- 背景音乐
- 音量控制
- 静音功能
"""

from typing import Dict, Optional
from enum import Enum, auto
import arcade
from ..core.logger import get_module_logger


logger = get_module_logger(__name__)


class SoundType(Enum):
    """音效类型枚举"""
    PLANT = auto()           # 种植
    SHOOT = auto()           # 射击
    HIT = auto()             # 击中
    COLLECT_SUN = auto()     # 收集阳光
    ZOMBIE_DEATH = auto()    # 僵尸死亡
    ZOMBIE_EAT = auto()      # 僵尸吃植物
    GAME_OVER = auto()       # 游戏结束
    VICTORY = auto()         # 胜利
    BUTTON_CLICK = auto()    # 按钮点击
    EXPLOSION = auto()       # 爆炸
    CHERRY_BOMB = auto()     # 樱桃炸弹
    POTATO_MINE = auto()     # 土豆雷
    ICE_HIT = auto()         # 冰冻击中
    FIRE_HIT = auto()        # 火焰击中
    SPLASH = auto()          # 溅射


class AudioManager:
    """
    音效管理器
    
    管理游戏中的所有音频资源
    """
    
    def __init__(self):
        # 音效字典
        self.sounds: Dict[SoundType, arcade.Sound] = {}
        
        # 音量设置 (0.0 - 1.0)
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.music_volume = 0.5
        
        # 静音状态
        self.is_muted = False
        
        # 当前播放的背景音乐
        self.current_music: Optional[arcade.Sound] = None
        self.music_player = None
        
        # 加载音效
        self._load_sounds()
    
    def _load_sounds(self) -> None:
        """加载所有音效"""
        # 检查assets目录是否存在
        import os
        assets_dir = "assets/sounds"
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)
        
        # 尝试加载自定义音效，如果失败则静默跳过
        sound_files = {
            SoundType.PLANT: "plant.wav",
            SoundType.SHOOT: "shoot.wav",
            SoundType.HIT: "hit.wav",
            SoundType.COLLECT_SUN: "collect_sun.wav",
            SoundType.ZOMBIE_DEATH: "zombie_death.wav",
            SoundType.ZOMBIE_EAT: "zombie_eat.wav",
            SoundType.GAME_OVER: "game_over.wav",
            SoundType.VICTORY: "victory.wav",
            SoundType.BUTTON_CLICK: "button_click.wav",
            SoundType.EXPLOSION: "explosion.wav",
            SoundType.CHERRY_BOMB: "cherry_bomb.wav",
            SoundType.POTATO_MINE: "potato_mine.wav",
            SoundType.ICE_HIT: "ice_hit.wav",
            SoundType.FIRE_HIT: "fire_hit.wav",
            SoundType.SPLASH: "splash.wav"
        }
        
        for sound_type, filename in sound_files.items():
            file_path = os.path.join(assets_dir, filename)
            if os.path.exists(file_path):
                try:
                    self.sounds[sound_type] = arcade.load_sound(file_path)
                except Exception as e:
                    logger.warning(f"无法加载音效 {filename}: {e}")
    
    def play_sound(self, sound_type: SoundType, volume: float = 1.0) -> None:
        """
        播放音效
        
        Args:
            sound_type: 音效类型
            volume: 音量倍率 (0.0 - 1.0)
        """
        if self.is_muted:
            return
        
        sound = self.sounds.get(sound_type)
        if sound:
            final_volume = self.master_volume * self.sfx_volume * volume
            arcade.play_sound(sound, final_volume)
    
    def play_music(self, music_path: str, loop: bool = True) -> None:
        """
        播放背景音乐
        
        Args:
            music_path: 音乐文件路径
            loop: 是否循环播放
        """
        if self.is_muted:
            return
        
        # 停止当前音乐
        self.stop_music()
        
        try:
            self.current_music = arcade.load_sound(music_path)
            if self.current_music:
                self.music_player = arcade.play_sound(
                    self.current_music,
                    self.master_volume * self.music_volume,
                    loop=loop
                )
        except Exception as e:
            logger.warning(f"无法加载音乐: {music_path}, 错误: {e}")
    
    def stop_music(self) -> None:
        """停止背景音乐"""
        if self.music_player:
            arcade.stop_sound(self.music_player)
            self.music_player = None
            self.current_music = None
    
    def pause_music(self) -> None:
        """暂停背景音乐"""
        # Arcade不直接支持暂停，这里可以记录状态
        pass
    
    def resume_music(self) -> None:
        """恢复背景音乐"""
        pass
    
    def set_master_volume(self, volume: float) -> None:
        """
        设置主音量
        
        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def set_sfx_volume(self, volume: float) -> None:
        """
        设置音效音量
        
        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """
        设置音乐音量
        
        Args:
            volume: 音量 (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        self._update_music_volume()
    
    def _update_music_volume(self) -> None:
        """更新当前音乐的音量"""
        # Arcade不支持动态调整音量，需要重新播放
        pass
    
    def toggle_mute(self) -> bool:
        """
        切换静音状态
        
        Returns:
            当前静音状态
        """
        self.is_muted = not self.is_muted
        
        if self.is_muted:
            self.stop_music()
        
        return self.is_muted
    
    def mute(self) -> None:
        """静音"""
        self.is_muted = True
        self.stop_music()
    
    def unmute(self) -> None:
        """取消静音"""
        self.is_muted = False
    
    def load_sound(self, sound_type: SoundType, file_path: str) -> bool:
        """
        加载音效文件
        
        Args:
            sound_type: 音效类型
            file_path: 文件路径
            
        Returns:
            是否加载成功
        """
        try:
            sound = arcade.load_sound(file_path)
            self.sounds[sound_type] = sound
            return True
        except Exception as e:
            logger.error(f"加载音效失败: {file_path}, 错误: {e}")
            return False
    
    def play_plant_sound(self) -> None:
        """播放种植音效"""
        self.play_sound(SoundType.PLANT)
    
    def play_shoot_sound(self) -> None:
        """播放射击音效"""
        self.play_sound(SoundType.SHOOT)
    
    def play_hit_sound(self) -> None:
        """播放击中音效"""
        self.play_sound(SoundType.HIT)
    
    def play_collect_sun_sound(self) -> None:
        """播放收集阳光音效"""
        self.play_sound(SoundType.COLLECT_SUN)
    
    def play_zombie_death_sound(self) -> None:
        """播放僵尸死亡音效"""
        self.play_sound(SoundType.ZOMBIE_DEATH)
    
    def play_zombie_eat_sound(self) -> None:
        """播放僵尸吃植物音效"""
        self.play_sound(SoundType.ZOMBIE_EAT)
    
    def play_game_over_sound(self) -> None:
        """播放游戏结束音效"""
        self.play_sound(SoundType.GAME_OVER)
    
    def play_victory_sound(self) -> None:
        """播放胜利音效"""
        self.play_sound(SoundType.VICTORY)
    
    def play_button_click_sound(self) -> None:
        """播放按钮点击音效"""
        self.play_sound(SoundType.BUTTON_CLICK)
    
    def play_explosion_sound(self) -> None:
        """播放爆炸音效"""
        self.play_sound(SoundType.EXPLOSION)
    
    def play_cherry_bomb_sound(self) -> None:
        """播放樱桃炸弹音效"""
        self.play_sound(SoundType.CHERRY_BOMB)
    
    def play_potato_mine_sound(self) -> None:
        """播放土豆雷音效"""
        self.play_sound(SoundType.POTATO_MINE)
    
    def play_ice_hit_sound(self) -> None:
        """播放冰冻击中音效"""
        self.play_sound(SoundType.ICE_HIT)
    
    def play_fire_hit_sound(self) -> None:
        """播放火焰击中音效"""
        self.play_sound(SoundType.FIRE_HIT)
    
    def play_splash_sound(self) -> None:
        """播放溅射音效"""
        self.play_sound(SoundType.SPLASH)


# 全局音效管理器实例
_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """获取全局音效管理器实例"""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager


def init_audio_manager() -> AudioManager:
    """初始化音效管理器"""
    global _audio_manager
    _audio_manager = AudioManager()
    return _audio_manager
