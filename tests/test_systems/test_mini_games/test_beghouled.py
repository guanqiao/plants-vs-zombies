"""
测试宝石迷阵小游戏
"""

import pytest
from src.systems.mini_games.beghouled import BeghouledGame


class TestBeghouledGame:
    """测试宝石迷阵游戏"""
    
    def test_initialization(self):
        """测试初始化"""
        game = BeghouledGame()
        
        assert game.running is True
        assert game.score == 0
        assert game.matches == 0
        assert game.target_matches == 75
        assert len(game.grid) == 8  # 8行
        assert len(game.grid[0]) == 8  # 8列
    
    def test_grid_initialized(self):
        """测试网格已初始化"""
        game = BeghouledGame()
        
        # 检查所有格子都有值
        for row in range(game.GRID_ROWS):
            for col in range(game.GRID_COLS):
                assert 0 <= game.grid[row][col] < len(game.COLORS)
    
    def test_find_matches_horizontal(self):
        """测试查找水平匹配"""
        game = BeghouledGame()
        
        # 手动设置水平三连
        game.grid[0][0] = 0
        game.grid[0][1] = 0
        game.grid[0][2] = 0
        
        matches = game._find_matches()
        
        assert (0, 0) in matches
        assert (0, 1) in matches
        assert (0, 2) in matches
    
    def test_find_matches_vertical(self):
        """测试查找垂直匹配"""
        game = BeghouledGame()
        
        # 手动设置垂直三连
        game.grid[0][0] = 1
        game.grid[1][0] = 1
        game.grid[2][0] = 1
        
        matches = game._find_matches()
        
        assert (0, 0) in matches
        assert (1, 0) in matches
        assert (2, 0) in matches
    
    def test_remove_matches(self):
        """测试移除匹配"""
        game = BeghouledGame()
        
        # 设置一些匹配
        game.grid[0][0] = 0
        game.grid[0][1] = 0
        game.grid[0][2] = 0
        
        matches = game._find_matches()
        game._remove_matches(matches)
        
        # 匹配的格子应该被清空（设为-1后重新填充）
        assert game.grid[0][0] != 0 or game.grid[0][1] != 0 or game.grid[0][2] != 0
    
    def test_can_swap_adjacent(self):
        """测试相邻格子可以交换"""
        game = BeghouledGame()
        
        result = game._can_swap((0, 0), (0, 1))
        
        assert result is True
    
    def test_cannot_swap_non_adjacent(self):
        """测试非相邻格子不能交换"""
        game = BeghouledGame()
        
        result = game._can_swap((0, 0), (0, 2))
        
        assert result is False
    
    def test_swap_cells(self):
        """测试交换格子"""
        game = BeghouledGame()
        
        # 记住原始值
        val1 = game.grid[0][0]
        val2 = game.grid[0][1]
        
        game._swap_cells((0, 0), (0, 1))
        
        assert game.grid[0][0] == val2
        assert game.grid[0][1] == val1
    
    def test_handle_click_select_cell(self):
        """测试点击选择格子"""
        game = BeghouledGame()
        
        # 点击第一个格子
        x = game.GRID_OFFSET_X + 10
        y = game.GRID_OFFSET_Y + 10
        
        result = game.handle_click(x, y)
        
        assert result is True
        assert game.selected_cell == (0, 0)
    
    def test_game_over_by_matches(self):
        """测试达到目标匹配数游戏结束"""
        game = BeghouledGame()
        game.matches = 75
        
        game.update(0.1)
        
        assert game.running is False
    
    def test_get_score(self):
        """测试获取分数"""
        game = BeghouledGame()
        game.score = 100
        
        assert game.get_score() == 100
    
    def test_is_game_over(self):
        """测试游戏结束检查"""
        game = BeghouledGame()
        
        assert game.is_game_over() is False
        
        game.running = False
        
        assert game.is_game_over() is True
