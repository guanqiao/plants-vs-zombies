"""
小游戏基类

所有小游戏的抽象基类，定义通用接口
"""

from abc import ABC, abstractmethod
import pygame


class BaseMiniGame(ABC):
    """
    小游戏基类
    
    所有小游戏必须实现以下接口：
    - update: 更新游戏状态
    - render: 渲染游戏画面
    - handle_click: 处理鼠标点击
    
    Attributes:
        running: 游戏是否进行中
        score: 游戏得分
    """
    
    def __init__(self):
        """初始化小游戏"""
        self.running = True
        self.score = 0
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        更新游戏状态
        
        Args:
            dt: 时间增量（秒）
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        渲染游戏画面
        
        Args:
            screen: Pygame屏幕表面
        """
        pass
    
    @abstractmethod
    def handle_click(self, x: int, y: int) -> bool:
        """
        处理鼠标点击
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            
        Returns:
            是否处理了点击事件
        """
        pass
    
    def is_game_over(self) -> bool:
        """
        检查游戏是否结束
        
        Returns:
            游戏是否结束
        """
        return not self.running
    
    def get_score(self) -> int:
        """
        获取游戏得分
        
        Returns:
            当前得分
        """
        return self.score
