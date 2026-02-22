"""
音效合成器 - 程序生成游戏音效

使用 numpy 生成各种波形数据，无需外部音频文件
"""

import numpy as np
import arcade
import tempfile
import os
from typing import Optional, Tuple
from ..core.logger import get_module_logger

logger = get_module_logger(__name__)

# 音频参数
SAMPLE_RATE = 44100
BIT_DEPTH = 16
MAX_AMPLITUDE = 32767


class SoundSynthesizer:
    """
    音效合成器
    
    使用程序生成各种游戏音效
    """
    
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self._temp_dir = tempfile.mkdtemp(prefix="game_sounds_")
        
    def _float_to_int16(self, data: np.ndarray) -> np.ndarray:
        """将浮点音频数据转换为 16bit 整数"""
        data = np.clip(data, -1.0, 1.0)
        return (data * MAX_AMPLITUDE).astype(np.int16)
    
    def _save_wave_file(self, data: np.ndarray, filename: str) -> str:
        """
        将 numpy 数组保存为 WAV 文件
        
        Args:
            data: 音频数据，范围 [-1.0, 1.0]
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        import struct
        
        # 转换为 16bit 整数
        int_data = self._float_to_int16(data)
        
        # 创建 WAV 文件
        num_channels = 1
        sample_width = 2  # 16bit
        num_frames = len(int_data)
        data_size = num_frames * sample_width
        
        file_path = os.path.join(self._temp_dir, filename)
        
        with open(file_path, 'wb') as f:
            # RIFF 头
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + data_size))
            f.write(b'WAVE')
            
            # fmt 子块
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))  # 子块大小
            f.write(struct.pack('<H', 1))   # 音频格式 (PCM)
            f.write(struct.pack('<H', num_channels))
            f.write(struct.pack('<I', self.sample_rate))
            f.write(struct.pack('<I', self.sample_rate * num_channels * sample_width))
            f.write(struct.pack('<H', num_channels * sample_width))
            f.write(struct.pack('<H', sample_width * 8))
            
            # data 子块
            f.write(b'data')
            f.write(struct.pack('<I', data_size))
            f.write(int_data.tobytes())
        
        return file_path
    
    def _create_sound(self, data: np.ndarray, filename: str) -> arcade.Sound:
        """
        将 numpy 数组转换为 arcade.Sound
        
        Args:
            data: 音频数据，范围 [-1.0, 1.0]
            filename: 临时文件名
            
        Returns:
            arcade.Sound 对象
        """
        file_path = self._save_wave_file(data, filename)
        
        try:
            sound = arcade.load_sound(file_path)
            return sound
        except Exception as e:
            logger.error(f"加载音效失败 {filename}: {e}")
            raise
    
    def generate_sine_wave(
        self, 
        frequency: float, 
        duration: float, 
        amplitude: float = 0.5,
        fade_in: float = 0.01,
        fade_out: float = 0.05
    ) -> arcade.Sound:
        """
        生成正弦波音效
        
        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            fade_in: 淡入时间 (秒)
            fade_out: 淡出时间 (秒)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # 应用淡入淡出
        fade_in_samples = int(fade_in * self.sample_rate)
        fade_out_samples = int(fade_out * self.sample_rate)
        
        if fade_in_samples > 0:
            fade_in_curve = np.linspace(0, 1, min(fade_in_samples, len(wave)))
            wave[:len(fade_in_curve)] *= fade_in_curve
        
        if fade_out_samples > 0:
            fade_out_curve = np.linspace(1, 0, min(fade_out_samples, len(wave)))
            wave[-len(fade_out_curve):] *= fade_out_curve
        
        return self._create_sound(wave, f"sine_{frequency:.0f}hz.wav")
    
    def generate_square_wave(
        self, 
        frequency: float, 
        duration: float, 
        amplitude: float = 0.3
    ) -> arcade.Sound:
        """
        生成方波音效
        
        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        
        # 快速淡出
        fade_samples = int(0.02 * self.sample_rate)
        if fade_samples > 0 and len(wave) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            wave[-fade_samples:] *= fade_curve
        
        return self._create_sound(wave, f"square_{frequency:.0f}hz.wav")
    
    def generate_sawtooth_wave(
        self, 
        frequency: float, 
        duration: float, 
        amplitude: float = 0.4
    ) -> arcade.Sound:
        """
        生成锯齿波音效
        
        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * (2 * (t * frequency - np.floor(t * frequency + 0.5)))
        
        # 淡出
        fade_samples = int(0.05 * self.sample_rate)
        if fade_samples > 0 and len(wave) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            wave[-fade_samples:] *= fade_curve
        
        return self._create_sound(wave, f"saw_{frequency:.0f}hz.wav")
    
    def generate_noise(
        self, 
        duration: float, 
        amplitude: float = 0.5,
        lowpass: Optional[float] = None
    ) -> arcade.Sound:
        """
        生成噪声音效
        
        Args:
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            lowpass: 低通滤波频率 (Hz)，None 表示不滤波
            
        Returns:
            arcade.Sound 对象
        """
        samples = int(self.sample_rate * duration)
        wave = amplitude * (2 * np.random.random(samples) - 1)
        
        # 简单的移动平均滤波
        if lowpass is not None:
            window_size = max(1, int(self.sample_rate / lowpass / 2))
            if window_size > 1:
                kernel = np.ones(window_size) / window_size
                wave = np.convolve(wave, kernel, mode='same')
        
        # 淡出
        fade_samples = int(0.1 * self.sample_rate)
        if fade_samples > 0 and len(wave) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            wave[-fade_samples:] *= fade_curve
        
        return self._create_sound(wave, f"noise_{duration:.2f}s.wav")
    
    def generate_sweep(
        self, 
        start_freq: float, 
        end_freq: float, 
        duration: float, 
        amplitude: float = 0.5
    ) -> arcade.Sound:
        """
        生成频率扫描音效（滑音）
        
        Args:
            start_freq: 起始频率 (Hz)
            end_freq: 结束频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        # 指数频率变化
        freq = start_freq * (end_freq / start_freq) ** (t / duration)
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = amplitude * np.sin(phase)
        
        return self._create_sound(wave, f"sweep_{start_freq:.0f}_{end_freq:.0f}hz.wav")
    
    def generate_dual_tone(
        self, 
        freq1: float, 
        freq2: float, 
        duration: float, 
        amplitude: float = 0.4
    ) -> arcade.Sound:
        """
        生成双音音效
        
        Args:
            freq1: 频率 1 (Hz)
            freq2: 频率 2 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = amplitude * 0.5 * (np.sin(2 * np.pi * freq1 * t) + np.sin(2 * np.pi * freq2 * t))
        
        # 淡出
        fade_samples = int(0.1 * self.sample_rate)
        if fade_samples > 0 and len(wave) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            wave[-fade_samples:] *= fade_curve
        
        return self._create_sound(wave, f"dual_{freq1:.0f}_{freq2:.0f}hz.wav")
    
    def generate_chord(
        self, 
        frequencies: Tuple[float, ...], 
        duration: float, 
        amplitude: float = 0.4
    ) -> arcade.Sound:
        """
        生成和弦音效（多音叠加）
        
        Args:
            frequencies: 频率元组 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅 (0.0 - 1.0)
            
        Returns:
            arcade.Sound 对象
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.zeros_like(t)
        
        for freq in frequencies:
            wave += amplitude * np.sin(2 * np.pi * freq * t) / len(frequencies)
        
        # 淡出
        fade_samples = int(0.15 * self.sample_rate)
        if fade_samples > 0 and len(wave) > fade_samples:
            fade_curve = np.linspace(1, 0, fade_samples)
            wave[-fade_samples:] *= fade_curve
        
        return self._create_sound(wave, f"chord_{len(frequencies)}notes.wav")
    
    def generate_plant_sound(self) -> arcade.Sound:
        """生成种植音效 - 短促上升音"""
        return self.generate_sweep(400, 800, 0.1, 0.5)
    
    def generate_shoot_sound(self) -> arcade.Sound:
        """生成射击音效 - 短促噪声爆发"""
        return self.generate_noise(0.05, 0.4, lowpass=2000)
    
    def generate_hit_sound(self) -> arcade.Sound:
        """生成击中音效 - 低频打击"""
        return self.generate_sine_wave(200, 0.08, 0.6, fade_in=0.001, fade_out=0.05)
    
    def generate_collect_sun_sound(self) -> arcade.Sound:
        """生成收集阳光音效 - 清脆铃声"""
        return self.generate_dual_tone(880, 1320, 0.15, 0.4)
    
    def generate_zombie_death_sound(self) -> arcade.Sound:
        """生成僵尸死亡音效 - 低沉下降音"""
        return self.generate_sweep(200, 100, 0.3, 0.5)
    
    def generate_zombie_eat_sound(self) -> arcade.Sound:
        """生成僵尸吃植物音效 - 咀嚼声"""
        # 生成低频噪声调制
        duration = 0.2
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 载波
        carrier = np.sin(2 * np.pi * 100 * t)
        # 调制信号（噪声）
        modulator = 0.5 + 0.5 * (2 * np.random.random(samples) - 1)
        
        wave = 0.4 * carrier * modulator
        
        return self._create_sound(wave, "zombie_eat.wav")
    
    def generate_game_over_sound(self) -> arcade.Sound:
        """生成游戏结束音效 - 悲伤下降音阶"""
        # 连续三个下降的音
        duration = 0.8
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # 三个音符的频率
        freqs = np.piecewise(t, 
            [t < 0.25, (t >= 0.25) & (t < 0.5), t >= 0.5],
            [440, 349, 293]  # A4, F4, D4
        )
        
        phase = 2 * np.pi * np.cumsum(freqs) / self.sample_rate
        wave = 0.4 * np.sin(phase)
        
        # 整体淡出
        fade_curve = np.linspace(1, 0, samples)
        wave *= fade_curve
        
        return self._create_sound(wave, "game_over.wav")
    
    def generate_victory_sound(self) -> arcade.Sound:
        """生成胜利音效 - 胜利和弦"""
        # C 大调和弦：C4, E4, G4, C5
        return self.generate_chord((261.63, 329.63, 392.00, 523.25), 0.6, 0.4)
    
    def generate_button_click_sound(self) -> arcade.Sound:
        """生成按钮点击音效 - 短促高频"""
        return self.generate_square_wave(2000, 0.03, 0.3)
    
    def generate_explosion_sound(self) -> arcade.Sound:
        """生成爆炸音效 - 噪声爆发"""
        return self.generate_noise(0.3, 0.6, lowpass=800)
    
    def generate_cherry_bomb_sound(self) -> arcade.Sound:
        """生成樱桃炸弹音效"""
        return self.generate_noise(0.4, 0.7, lowpass=600)
    
    def generate_potato_mine_sound(self) -> arcade.Sound:
        """生成土豆雷音效"""
        return self.generate_sweep(150, 50, 0.25, 0.6)
    
    def generate_ice_hit_sound(self) -> arcade.Sound:
        """生成冰冻击中音效"""
        return self.generate_dual_tone(600, 1200, 0.12, 0.4)
    
    def generate_fire_hit_sound(self) -> arcade.Sound:
        """生成火焰击中音效"""
        return self.generate_sawtooth_wave(300, 0.15, 0.4)
    
    def generate_splash_sound(self) -> arcade.Sound:
        """生成溅射音效"""
        # 使用噪声模拟水声
        duration = 0.25
        samples = int(self.sample_rate * duration)
        
        # 生成带滤波的噪声
        noise = np.random.random(samples) * 2 - 1
        
        # 简单的移动平均滤波
        window_size = 10
        kernel = np.ones(window_size) / window_size
        filtered = np.convolve(noise, kernel, mode='same')
        
        # 振幅包络
        t = np.linspace(0, duration, samples, False)
        envelope = np.exp(-t * 10)  # 快速衰减
        
        wave = 0.5 * filtered * envelope
        
        return self._create_sound(wave, "splash.wav")


# 全局合成器实例
_synthesizer: Optional[SoundSynthesizer] = None


def get_synthesizer() -> SoundSynthesizer:
    """获取全局音效合成器实例"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = SoundSynthesizer()
    return _synthesizer
