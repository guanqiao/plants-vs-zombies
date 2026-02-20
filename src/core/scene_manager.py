"""
场景管理器 - 管理游戏场景的切换和生命周期
"""
from typing import Dict, Optional
from .scene import Scene


class SceneManager:
    """
    场景管理器
    
    管理所有游戏场景的注册、切换和生命周期
    """
    
    def __init__(self):
        """初始化场景管理器"""
        self._scenes: Dict[str, Scene] = {}
        self._current_scene: Optional[Scene] = None
    
    def register_scene(self, scene: Scene) -> None:
        """
        注册场景
        
        Args:
            scene: 场景实例
        """
        self._scenes[scene.name] = scene
    
    def change_scene(self, scene_name: str) -> bool:
        """
        切换到指定场景
        
        Args:
            scene_name: 场景名称
            
        Returns:
            True if 切换成功
        """
        if scene_name not in self._scenes:
            return False
        
        # 退出当前场景
        if self._current_scene:
            self._current_scene.on_exit()
            self._current_scene.exit()
        
        # 进入新场景
        self._current_scene = self._scenes[scene_name]
        self._current_scene.on_enter()
        self._current_scene.enter()
        
        return True
    
    def update(self, dt: float) -> None:
        """
        更新当前场景
        
        Args:
            dt: 时间增量（秒）
        """
        if self._current_scene:
            self._current_scene.update(dt)
    
    def render(self) -> None:
        """渲染当前场景"""
        if self._current_scene:
            self._current_scene.render()
    
    def handle_event(self, event) -> bool:
        """
        处理事件
        
        Args:
            event: 事件对象
            
        Returns:
            True if 事件被处理
        """
        if self._current_scene:
            return self._current_scene.handle_event(event)
        return False
    
    def get_current_scene(self) -> Optional[Scene]:
        """
        获取当前场景
        
        Returns:
            当前场景实例或None
        """
        return self._current_scene
    
    def has_scene(self, scene_name: str) -> bool:
        """
        检查是否存在指定场景
        
        Args:
            scene_name: 场景名称
            
        Returns:
            True if 场景存在
        """
        return scene_name in self._scenes
