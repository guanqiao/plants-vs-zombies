"""
游戏状态管理器

管理游戏的不同状态（菜单、游戏中、暂停等）
"""

from enum import Enum, auto
from typing import Optional, Callable


class GameStateType(Enum):
    """游戏状态类型枚举 - 用于测试兼容"""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class GameState:
    """
    游戏状态类 - 用于测试兼容
    
    提供与测试兼容的API
    """
    
    def __init__(self):
        """初始化游戏状态"""
        self.current_state = GameStateType.MENU
        self._previous_state: Optional[GameStateType] = None
    
    def change_state(self, new_state: GameStateType) -> None:
        """
        改变游戏状态
        
        Args:
            new_state: 新的游戏状态
        """
        if self.current_state == new_state:
            return
        
        self._previous_state = self.current_state
        self.current_state = new_state
    
    def is_playing(self) -> bool:
        """检查是否在游戏中"""
        return self.current_state == GameStateType.PLAYING
    
    def is_paused(self) -> bool:
        """检查是否暂停"""
        return self.current_state == GameStateType.PAUSED
    
    def is_game_over(self) -> bool:
        """检查是否游戏结束"""
        return self.current_state == GameStateType.GAME_OVER


class ExtendedGameState(Enum):
    """扩展游戏状态枚举 - 用于完整游戏"""
    MAIN_MENU = auto()
    LEVEL_SELECT = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    SETTINGS = auto()


class GameStateManager:
    """
    游戏状态管理器
    
    管理游戏状态转换和相关逻辑
    
    Attributes:
        current_state: 当前游戏状态
        previous_state: 上一个游戏状态
        current_level: 当前关卡
        max_unlocked_level: 最大解锁关卡
        current_difficulty: 当前难度等级
    """
    
    def __init__(self):
        """初始化游戏状态管理器"""
        self.current_state = ExtendedGameState.MAIN_MENU
        self.previous_state: Optional[ExtendedGameState] = None
        self.current_level = 1
        self.max_unlocked_level = 1
        self.score = 0
        self.current_difficulty = "normal"  # 默认普通难度
        
        # 状态改变回调
        self.on_state_change: Optional[Callable[[ExtendedGameState, ExtendedGameState], None]] = None
        self.on_start_game: Optional[Callable[[int, str], None]] = None
        self.on_pause: Optional[Callable[[], None]] = None
        self.on_resume: Optional[Callable[[], None]] = None
        self.on_restart: Optional[Callable[[], None]] = None
        self.on_quit: Optional[Callable[[], None]] = None
        self.on_difficulty_change: Optional[Callable[[str], None]] = None
    
    def change_state(self, new_state: ExtendedGameState) -> None:
        """
        改变游戏状态
        
        Args:
            new_state: 新的游戏状态
        """
        if self.current_state == new_state:
            return
        
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # 触发回调
        if self.on_state_change:
            self.on_state_change(self.previous_state, self.current_state)
    
    def is_in_menu(self) -> bool:
        """检查是否在菜单中"""
        return self.current_state in {
            ExtendedGameState.MAIN_MENU,
            ExtendedGameState.LEVEL_SELECT,
            ExtendedGameState.SETTINGS
        }
    
    def is_playing(self) -> bool:
        """检查是否在游戏中"""
        return self.current_state == ExtendedGameState.PLAYING
    
    def is_paused(self) -> bool:
        """检查是否暂停"""
        return self.current_state == ExtendedGameState.PAUSED
    
    def is_game_over(self) -> bool:
        """检查是否游戏结束"""
        return self.current_state == ExtendedGameState.GAME_OVER
    
    def is_victory(self) -> bool:
        """检查是否胜利"""
        return self.current_state == ExtendedGameState.VICTORY
    
    def start_game(self, level: int = 1, difficulty: str = "normal") -> None:
        """
        开始游戏
        
        Args:
            level: 关卡号
            difficulty: 难度等级 ('easy', 'normal', 'hard')
        """
        self.current_level = level
        self.current_difficulty = difficulty
        self.change_state(ExtendedGameState.PLAYING)
        
        if self.on_start_game:
            self.on_start_game(level, difficulty)
    
    def set_difficulty(self, difficulty: str) -> None:
        """
        设置游戏难度
        
        Args:
            difficulty: 难度等级 ('easy', 'normal', 'hard')
        """
        self.current_difficulty = difficulty
        if self.on_difficulty_change:
            self.on_difficulty_change(difficulty)
    
    def pause_game(self) -> None:
        """暂停游戏"""
        if self.current_state == ExtendedGameState.PLAYING:
            self.change_state(ExtendedGameState.PAUSED)
            
            if self.on_pause:
                self.on_pause()
    
    def resume_game(self) -> None:
        """继续游戏"""
        if self.current_state == ExtendedGameState.PAUSED:
            self.change_state(ExtendedGameState.PLAYING)
            
            if self.on_resume:
                self.on_resume()
    
    def restart_game(self) -> None:
        """重新开始游戏"""
        self.change_state(ExtendedGameState.PLAYING)
        
        if self.on_restart:
            self.on_restart()
    
    def game_over(self, score: int = 0) -> None:
        """
        游戏结束
        
        Args:
            score: 最终得分
        """
        self.score = score
        self.change_state(ExtendedGameState.GAME_OVER)
    
    def victory(self, score: int = 0) -> None:
        """
        游戏胜利
        
        Args:
            score: 最终得分
        """
        self.score = score
        
        # 解锁下一关
        if self.current_level >= self.max_unlocked_level:
            self.max_unlocked_level = min(self.current_level + 1, 7)
        
        self.change_state(ExtendedGameState.VICTORY)
    
    def go_to_main_menu(self) -> None:
        """返回主菜单"""
        self.change_state(ExtendedGameState.MAIN_MENU)
    
    def go_to_level_select(self) -> None:
        """进入关卡选择"""
        self.change_state(ExtendedGameState.LEVEL_SELECT)
    
    def go_to_settings(self) -> None:
        """进入设置"""
        self.change_state(ExtendedGameState.SETTINGS)
    
    def quit_game(self) -> None:
        """退出游戏"""
        if self.on_quit:
            self.on_quit()
    
    def toggle_pause(self) -> None:
        """切换暂停状态"""
        if self.current_state == ExtendedGameState.PLAYING:
            self.pause_game()
        elif self.current_state == ExtendedGameState.PAUSED:
            self.resume_game()
    
    def next_level(self) -> None:
        """进入下一关"""
        if self.current_level < 7:
            self.start_game(self.current_level + 1)
    
    def get_state_name(self) -> str:
        """获取当前状态名称"""
        state_names = {
            ExtendedGameState.MAIN_MENU: "主菜单",
            ExtendedGameState.LEVEL_SELECT: "关卡选择",
            ExtendedGameState.PLAYING: "游戏中",
            ExtendedGameState.PAUSED: "暂停",
            ExtendedGameState.GAME_OVER: "游戏结束",
            ExtendedGameState.VICTORY: "胜利",
            ExtendedGameState.SETTINGS: "设置"
        }
        return state_names.get(self.current_state, "未知")
