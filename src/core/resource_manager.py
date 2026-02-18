import pygame
import os
from pathlib import Path
from typing import Dict, Optional


class ResourceManager:
    """资源管理器 - 加载和缓存游戏资源"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._assets_dir = Path(__file__).parent.parent.parent / 'assets'
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        
        pygame.mixer.init()
    
    def load_image(self, path: str) -> Optional[pygame.Surface]:
        """加载图片资源"""
        if path in self._image_cache:
            return self._image_cache[path]
        
        full_path = self._assets_dir / 'images' / path
        if not os.path.exists(full_path):
            return None
        
        try:
            image = pygame.image.load(str(full_path))
            self._image_cache[path] = image
            return image
        except pygame.error:
            return None
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """加载音效资源"""
        if path in self._sound_cache:
            return self._sound_cache[path]
        
        full_path = self._assets_dir / 'sounds' / path
        if not os.path.exists(full_path):
            return None
        
        try:
            sound = pygame.mixer.Sound(str(full_path))
            self._sound_cache[path] = sound
            return sound
        except pygame.error:
            return None
    
    def get_image(self, path: str) -> Optional[pygame.Surface]:
        """获取已缓存的图片"""
        return self._image_cache.get(path)
    
    def get_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """获取已缓存的音效"""
        return self._sound_cache.get(path)
    
    def clear_cache(self):
        """清除所有缓存"""
        self._image_cache.clear()
        self._sound_cache.clear()
    
    def preload_images(self, paths: list):
        """预加载图片列表"""
        for path in paths:
            self.load_image(path)
    
    def preload_sounds(self, paths: list):
        """预加载音效列表"""
        for path in paths:
            self.load_sound(path)
    
    @classmethod
    def get_instance(cls) -> 'ResourceManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
