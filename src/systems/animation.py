import pygame
from typing import List, Dict, Optional


class Animation:
    """动画组件 - 管理帧动画"""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, 
                 loop: bool = True):
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.timer = 0.0
        self.is_playing = True
    
    def update(self, dt: float):
        """更新动画"""
        if not self.is_playing or len(self.frames) == 0:
            return
        
        self.timer += dt
        
        if self.timer >= self.frame_duration:
            self.timer = 0.0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.is_playing = False
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """获取当前帧"""
        if self.frames and 0 <= self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return None
    
    def reset(self):
        """重置动画"""
        self.current_frame = 0
        self.timer = 0.0
        self.is_playing = True
    
    def pause(self):
        """暂停动画"""
        self.is_playing = False
    
    def resume(self):
        """恢复动画"""
        self.is_playing = True
    
    def set_frame(self, frame_index: int):
        """设置当前帧"""
        if 0 <= frame_index < len(self.frames):
            self.current_frame = frame_index
            self.timer = 0.0


class AnimationManager:
    """动画管理器 - 管理多个动画"""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
    
    def add_animation(self, name: str, animation: Animation):
        """添加动画"""
        self.animations[name] = animation
    
    def play(self, name: str):
        """播放指定动画"""
        if name in self.animations:
            if self.current_animation != name:
                self.current_animation = name
                self.animations[name].reset()
            self.animations[name].resume()
    
    def stop(self, name: str):
        """停止指定动画"""
        if name in self.animations:
            self.animations[name].pause()
    
    def stop_all(self):
        """停止所有动画"""
        for animation in self.animations.values():
            animation.pause()
    
    def update(self, dt: float):
        """更新当前动画"""
        if self.current_animation and self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
    
    def update_all(self, dt: float):
        """更新所有动画"""
        for animation in self.animations.values():
            animation.update(dt)
    
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """获取当前动画的当前帧"""
        if self.current_animation and self.current_animation in self.animations:
            return self.animations[self.current_animation].get_current_frame()
        return None
    
    def create_simple_animation(self, base_color: tuple, width: int, height: int,
                                 frame_count: int = 4, variation: int = 10) -> Animation:
        """创建简单的颜色变化动画"""
        frames = []
        for i in range(frame_count):
            offset = (i - frame_count // 2) * variation
            color = (
                max(0, min(255, base_color[0] + offset)),
                max(0, min(255, base_color[1] + offset)),
                max(0, min(255, base_color[2] + offset))
            )
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(surface, color, (0, 0, width, height))
            frames.append(surface)
        
        return Animation(frames, frame_duration=0.15, loop=True)
