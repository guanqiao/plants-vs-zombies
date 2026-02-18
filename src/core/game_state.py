from enum import Enum, auto


class GameStateType(Enum):
    """游戏状态类型枚举"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class GameState:
    """游戏状态管理器"""
    
    def __init__(self):
        self.current_state = GameStateType.MENU
    
    def change_state(self, new_state: GameStateType):
        """切换游戏状态"""
        self.current_state = new_state
    
    def is_playing(self) -> bool:
        """是否正在游戏"""
        return self.current_state == GameStateType.PLAYING
    
    def is_paused(self) -> bool:
        """是否暂停"""
        return self.current_state == GameStateType.PAUSED
    
    def is_game_over(self) -> bool:
        """是否游戏结束"""
        return self.current_state == GameStateType.GAME_OVER
    
    def is_victory(self) -> bool:
        """是否胜利"""
        return self.current_state == GameStateType.VICTORY
    
    def is_menu(self) -> bool:
        """是否在菜单"""
        return self.current_state == GameStateType.MENU
