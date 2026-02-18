import pytest
from enum import Enum


class TestGameState:
    """游戏状态测试"""

    def test_game_state_enum_exists(self):
        """测试游戏状态枚举存在"""
        from src.core.game_state import GameStateType
        
        assert hasattr(GameStateType, 'MENU')
        assert hasattr(GameStateType, 'PLAYING')
        assert hasattr(GameStateType, 'PAUSED')
        assert hasattr(GameStateType, 'GAME_OVER')
        assert hasattr(GameStateType, 'VICTORY')

    def test_game_state_initial_state(self):
        """测试游戏状态初始值为菜单"""
        from src.core.game_state import GameState
        
        state = GameState()
        assert state.current_state.name == 'MENU'

    def test_game_state_transition(self):
        """测试游戏状态转换"""
        from src.core.game_state import GameState, GameStateType
        
        state = GameState()
        
        state.change_state(GameStateType.PLAYING)
        assert state.current_state == GameStateType.PLAYING
        
        state.change_state(GameStateType.PAUSED)
        assert state.current_state == GameStateType.PAUSED
        
        state.change_state(GameStateType.GAME_OVER)
        assert state.current_state == GameStateType.GAME_OVER

    def test_game_state_is_playing(self):
        """测试是否正在游戏"""
        from src.core.game_state import GameState, GameStateType
        
        state = GameState()
        assert not state.is_playing()
        
        state.change_state(GameStateType.PLAYING)
        assert state.is_playing()

    def test_game_state_is_paused(self):
        """测试是否暂停"""
        from src.core.game_state import GameState, GameStateType
        
        state = GameState()
        assert not state.is_paused()
        
        state.change_state(GameStateType.PLAYING)
        state.change_state(GameStateType.PAUSED)
        assert state.is_paused()

    def test_game_state_is_game_over(self):
        """测试是否游戏结束"""
        from src.core.game_state import GameState, GameStateType
        
        state = GameState()
        assert not state.is_game_over()
        
        state.change_state(GameStateType.GAME_OVER)
        assert state.is_game_over()
