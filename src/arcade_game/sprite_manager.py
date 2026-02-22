"""
精灵图资源管理器

负责加载、缓存和管理游戏中的精灵图资源
支持多状态精灵和动画帧管理
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import arcade


@dataclass
class AnimationFrame:
    """动画帧"""
    texture: arcade.Texture
    duration: float  # 帧持续时间（秒）


class Animation:
    """
    动画类
    
    管理一组动画帧和播放逻辑
    """
    
    def __init__(self, name: str, frames: List[AnimationFrame], loop: bool = True):
        self.name = name
        self.frames = frames
        self.loop = loop
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.is_playing = False
        self.frame_events: Dict[int, callable] = {}  # 特定帧触发的事件
    
    def play(self) -> None:
        """开始播放"""
        self.is_playing = True
        self.current_frame_index = 0
        self.frame_timer = 0.0
    
    def stop(self) -> None:
        """停止播放"""
        self.is_playing = False
    
    def reset(self) -> None:
        """重置到第一帧"""
        self.current_frame_index = 0
        self.frame_timer = 0.0
    
    def update(self, dt: float) -> None:
        """更新动画"""
        if not self.is_playing or not self.frames:
            return
        
        self.frame_timer += dt
        current_frame = self.frames[self.current_frame_index]
        
        # 检查是否需要切换到下一帧
        while self.frame_timer >= current_frame.duration:
            self.frame_timer -= current_frame.duration
            
            # 触发帧事件
            if self.current_frame_index in self.frame_events:
                self.frame_events[self.current_frame_index]()
            
            # 切换到下一帧
            self.current_frame_index += 1
            
            if self.current_frame_index >= len(self.frames):
                if self.loop:
                    self.current_frame_index = 0
                else:
                    self.current_frame_index = len(self.frames) - 1
                    self.is_playing = False
                    break
            
            current_frame = self.frames[self.current_frame_index]
    
    def get_current_texture(self) -> Optional[arcade.Texture]:
        """获取当前帧的纹理"""
        if not self.frames or self.current_frame_index >= len(self.frames):
            return None
        return self.frames[self.current_frame_index].texture
    
    def add_frame_event(self, frame_index: int, callback: callable) -> None:
        """添加帧事件"""
        self.frame_events[frame_index] = callback
    
    def clone(self) -> 'Animation':
        """克隆动画（用于多个实体共享动画数据但独立播放）"""
        new_anim = Animation(self.name, self.frames, self.loop)
        new_anim.frame_events = self.frame_events.copy()
        return new_anim


class SpriteSheet:
    """
    精灵表
    
    从单个图片加载多帧动画
    """
    
    def __init__(self, texture: arcade.Texture, frame_width: int, frame_height: int):
        self.texture = texture
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames: List[arcade.Texture] = []
        self._split_frames()
    
    def _split_frames(self) -> None:
        """将大图分割成多个小帧"""
        cols = self.texture.width // self.frame_width
        rows = self.texture.height // self.frame_height
        
        for row in range(rows):
            for col in range(cols):
                x = col * self.frame_width
                y = row * self.frame_height
                
                # 从纹理中裁剪出单帧
                frame = arcade.Texture(
                    name=f"{self.texture.name}_frame_{row}_{col}",
                    image=self.texture.image.crop((
                        x, y,
                        x + self.frame_width,
                        y + self.frame_height
                    ))
                )
                self.frames.append(frame)
    
    def get_frame(self, index: int) -> Optional[arcade.Texture]:
        """获取指定帧"""
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None
    
    def create_animation(self, frame_indices: List[int], 
                        frame_duration: float = 0.1,
                        loop: bool = True,
                        name: str = "animation") -> Animation:
        """从指定帧创建动画"""
        frames = []
        for idx in frame_indices:
            texture = self.get_frame(idx)
            if texture:
                frames.append(AnimationFrame(texture, frame_duration))
        
        return Animation(name, frames, loop)


class SpriteManager:
    """
    精灵管理器
    
    管理所有游戏精灵资源的单例类
    """
    
    _instance = None
    MAX_TEXTURE_CACHE_SIZE = 100  # 最大纹理缓存数量
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._textures: Dict[str, arcade.Texture] = {}
        self._animations: Dict[str, Animation] = {}
        self._sprite_sheets: Dict[str, SpriteSheet] = {}
        self._resource_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "images")
        self._texture_access_order: List[str] = []  # 记录纹理访问顺序用于LRU清理
    
    def load_texture(self, name: str, path: str) -> Optional[arcade.Texture]:
        """
        加载纹理
        
        Args:
            name: 纹理名称（用于缓存）
            path: 图片路径
            
        Returns:
            加载的纹理或None
        """
        if name in self._textures:
            # 更新访问顺序
            self._update_access_order(name)
            return self._textures[name]
        
        # 检查是否需要清理缓存
        self._cleanup_cache_if_needed()
        
        try:
            full_path = os.path.join(self._resource_path, path)
            if os.path.exists(full_path):
                texture = arcade.load_texture(full_path)
                self._textures[name] = texture
                self._texture_access_order.append(name)
                return texture
            else:
                # 如果文件不存在，返回None
                return None
        except Exception as e:
            print(f"加载纹理失败 {path}: {e}")
            return None
    
    def get_texture(self, name: str) -> Optional[arcade.Texture]:
        """获取已加载的纹理"""
        if name in self._textures:
            # 更新访问顺序
            self._update_access_order(name)
        return self._textures.get(name)
    
    def _update_access_order(self, name: str) -> None:
        """更新纹理访问顺序（LRU）"""
        if name in self._texture_access_order:
            self._texture_access_order.remove(name)
        self._texture_access_order.append(name)
    
    def _cleanup_cache_if_needed(self) -> None:
        """如果缓存过大，清理最少使用的纹理"""
        if len(self._textures) >= self.MAX_TEXTURE_CACHE_SIZE:
            # 清理最久未使用的20%纹理
            cleanup_count = self.MAX_TEXTURE_CACHE_SIZE // 5
            for _ in range(cleanup_count):
                if self._texture_access_order:
                    oldest_name = self._texture_access_order.pop(0)
                    if oldest_name in self._textures:
                        del self._textures[oldest_name]
    
    def load_sprite_sheet(self, name: str, path: str, 
                         frame_width: int, frame_height: int) -> Optional[SpriteSheet]:
        """
        加载精灵表
        
        Args:
            name: 精灵表名称
            path: 图片路径
            frame_width: 单帧宽度
            frame_height: 单帧高度
            
        Returns:
            SpriteSheet对象或None
        """
        if name in self._sprite_sheets:
            return self._sprite_sheets[name]
        
        texture = self.load_texture(name, path)
        if texture:
            sprite_sheet = SpriteSheet(texture, frame_width, frame_height)
            self._sprite_sheets[name] = sprite_sheet
            return sprite_sheet
        return None
    
    def register_animation(self, name: str, animation: Animation) -> None:
        """注册动画模板"""
        self._animations[name] = animation
    
    def get_animation(self, name: str) -> Optional[Animation]:
        """
        获取动画（返回克隆，以便多个实体独立播放）
        
        Args:
            name: 动画名称
            
        Returns:
            动画的克隆实例或None
        """
        anim = self._animations.get(name)
        if anim:
            return anim.clone()
        return None
    
    def create_placeholder_texture(self, name: str, width: int, height: int,
                                   color: Tuple[int, int, int]) -> arcade.Texture:
        """
        创建占位纹理（用于没有精灵图时）
        
        Args:
            name: 纹理名称
            width: 宽度
            height: 高度
            color: 颜色
            
        Returns:
            创建的纹理
        """
        if name in self._textures:
            return self._textures[name]
        
        # 创建纯色图片
        from PIL import Image
        image = Image.new('RGBA', (width, height), (*color, 255))
        
        # 添加边框
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width-1, height-1], outline=(0, 0, 0, 255), width=2)
        
        texture = arcade.Texture(name=name, image=image)
        self._textures[name] = texture
        return texture
    
    def create_colored_circle_texture(self, name: str, radius: int,
                                      color: Tuple[int, int, int]) -> arcade.Texture:
        """
        创建圆形占位纹理
        
        Args:
            name: 纹理名称
            radius: 半径
            color: 颜色
            
        Returns:
            创建的纹理
        """
        if name in self._textures:
            return self._textures[name]
        
        from PIL import Image, ImageDraw
        size = radius * 2
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([0, 0, size-1, size-1], fill=(*color, 255), outline=(0, 0, 0, 255), width=2)
        
        texture = arcade.Texture(name=name, image=image)
        self._textures[name] = texture
        return texture
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._textures.clear()
        self._animations.clear()
        self._sprite_sheets.clear()


# 全局访问函数
def get_sprite_manager() -> SpriteManager:
    """获取精灵管理器实例"""
    return SpriteManager()
