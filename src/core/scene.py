"""
场景基类 - 游戏场景的基础抽象类
"""
from abc import ABC, abstractmethod
from typing import Optional


class Scene(ABC):
    """
    场景基类
    
    所有游戏场景都应该继承这个类
    """
    
    def __init__(self, name: str):
        """
        初始化场景
        
        Args:
            name: 场景名称
        """
        self.name = name
        self.is_active = False
    
    @abstractmethod
    def enter(self):
        """进入场景时调用"""
        pass
    
    @abstractmethod
    def exit(self):
        """退出场景时调用"""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """
        更新场景
        
        Args:
            dt: 时间增量（秒）
        """
        pass
    
    @abstractmethod
    def render(self):
        """渲染场景"""
        pass
    
    def handle_event(self, event) -> bool:
        """
        处理事件
        
        Args:
            event: 事件对象
            
        Returns:
            True if 事件被处理
        """
        return False
    
    def on_enter(self):
        """进入场景时的回调（可以被子类重写）"""
        self.is_active = True
    
    def on_exit(self):
        """退出场景时的回调（可以被子类重写）"""
        self.is_active = False
