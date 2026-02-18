from typing import Dict, Optional, TYPE_CHECKING
from src.core.scene import Scene

if TYPE_CHECKING:
    import pygame


class SceneManager:
    """场景管理器 - 管理游戏场景的切换和生命周期"""
    
    def __init__(self):
        self._scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self._current_scene_name: Optional[str] = None
    
    def register_scene(self, name: str, scene: Scene):
        """注册场景"""
        self._scenes[name] = scene
    
    def unregister_scene(self, name: str):
        """注销场景"""
        if name in self._scenes:
            del self._scenes[name]
    
    def change_scene(self, name: str):
        """切换场景"""
        if name not in self._scenes:
            return
        
        if self.current_scene is not None:
            self.current_scene.exit()
        
        self.current_scene = self._scenes[name]
        self._current_scene_name = name
        self.current_scene.enter()
    
    def update(self, dt: float):
        """更新当前场景"""
        if self.current_scene is not None:
            self.current_scene.update(dt)
    
    def render(self, screen: 'pygame.Surface'):
        """渲染当前场景"""
        if self.current_scene is not None:
            self.current_scene.render(screen)
    
    def handle_event(self, event):
        """处理事件"""
        if self.current_scene is not None:
            self.current_scene.handle_event(event)
    
    def has_scene(self, name: str) -> bool:
        """检查场景是否存在"""
        return name in self._scenes
    
    def get_current_scene_name(self) -> Optional[str]:
        """获取当前场景名称"""
        return self._current_scene_name
    
    def clear(self):
        """清除所有场景"""
        if self.current_scene is not None:
            self.current_scene.exit()
        self._scenes.clear()
        self.current_scene = None
        self._current_scene_name = None
