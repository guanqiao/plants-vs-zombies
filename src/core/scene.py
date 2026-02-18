from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pygame
    from src.core.game_manager import GameManager


class Scene(ABC):
    """场景基类"""
    
    def __init__(self, game_manager: 'GameManager'):
        self.game_manager = game_manager
    
    def enter(self):
        """进入场景时调用"""
        pass
    
    def exit(self):
        """退出场景时调用"""
        pass
    
    @abstractmethod
    def update(self, dt: float):
        """更新场景"""
        pass
    
    @abstractmethod
    def render(self, screen: 'pygame.Surface'):
        """渲染场景"""
        pass
    
    @abstractmethod
    def handle_event(self, event):
        """处理事件"""
        pass
