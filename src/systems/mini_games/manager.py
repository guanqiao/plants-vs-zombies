"""
小游戏管理器

管理所有小游戏的创建和切换
"""
from typing import Optional, Dict
from .types import MiniGameType
from .base_game import BaseMiniGame
from .aquarium import ZombieAquarium
from .beghouled import BeghouledGame
from .bowling import WallnutBowling


class MiniGameManager:
    """
    小游戏管理器
    
    负责创建和管理小游戏实例
    """
    
    def __init__(self):
        """初始化小游戏管理器"""
        self._current_game: Optional[BaseMiniGame] = None
        self._game_type: Optional[MiniGameType] = None
    
    def start_game(self, game_type: MiniGameType) -> BaseMiniGame:
        """
        开始指定类型的小游戏
        
        Args:
            game_type: 小游戏类型
            
        Returns:
            小游戏实例
        """
        self._game_type = game_type
        
        if game_type == MiniGameType.ZOMBIE_AQUARIUM:
            self._current_game = ZombieAquarium()
        elif game_type == MiniGameType.BEGHOULED:
            self._current_game = BeghouledGame()
        elif game_type == MiniGameType.WALLNUT_BOWLING:
            self._current_game = WallnutBowling()
        else:
            raise ValueError(f"Unknown mini game type: {game_type}")
        
        return self._current_game
    
    def stop_game(self) -> None:
        """停止当前小游戏"""
        self._current_game = None
        self._game_type = None
    
    def get_current_game(self) -> Optional[BaseMiniGame]:
        """
        获取当前小游戏
        
        Returns:
            当前小游戏实例或None
        """
        return self._current_game
    
    def get_game_type(self) -> Optional[MiniGameType]:
        """
        获取当前小游戏类型
        
        Returns:
            当前小游戏类型或None
        """
        return self._game_type
    
    def is_game_running(self) ->