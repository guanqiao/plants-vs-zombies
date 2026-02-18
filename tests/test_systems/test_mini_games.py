import pytest
from unittest.mock import MagicMock


class TestZombieAquarium:
    """僵尸水族馆测试"""

    def test_aquarium_initialization(self):
        """测试水族馆初始化"""
        from src.systems.mini_games import ZombieAquarium
        
        game = ZombieAquarium()
        assert game is not None
        assert len(game.zombies) == 0
        assert game.food_count == 3
        assert game.running
    
    def test_add_zombie(self):
        """测试添加僵尸"""
        from src.systems.mini_games import ZombieAquarium
        
        game = ZombieAquarium()
        game.add_zombie(400, 300)
        
        assert len(game.zombies) == 1
        assert game.zombies[0].x == 400
        assert game.zombies[0].y == 300
    
    def test_feed_zombie(self):
        """测试喂食僵尸"""
        from src.systems.mini_games import ZombieAquarium
        
        game = ZombieAquarium()
        game.add_zombie(400, 300)
        game.zombies[0].hunger = 80
        
        result = game.feed_zombie(400, 300)
        
        assert result
        assert game.zombies[0].hunger < 80
        assert game.food_count == 2
    
    def test_collect_gold(self):
        """测试收集金币"""
        from src.systems.mini_games import ZombieAquarium
        
        game = ZombieAquarium()
        game.add_zombie(400, 300)
        game.zombies[0].gold_timer = 15.0
        game.zombies[0].hunger = 30
        
        gold = game.collect_gold(400, 300)
        
        assert gold > 0
        assert game.zombies[0].gold_timer == 0.0
    
    def test_zombie_starvation(self):
        """测试僵尸饿死"""
        from src.systems.mini_games import ZombieAquarium
        
        game = ZombieAquarium()
        game.add_zombie(400, 300)
        game.zombies[0].hunger = 100
        
        game.update(0.1)
        
        assert len(game.zombies) == 0


class TestBeghouledGame:
    """宝石迷阵测试"""

    def test_beghouled_initialization(self):
        """测试宝石迷阵初始化"""
        from src.systems.mini_games import BeghouledGame
        
        game = BeghouledGame()
        assert game is not None
        assert len(game.grid) == 8
        assert len(game.grid[0]) == 8
    
    def test_find_matches_horizontal(self):
        """测试查找水平匹配"""
        from src.systems.mini_games import BeghouledGame
        
        game = BeghouledGame()
        # 创建水平匹配
        game.grid[0][0] = 1
        game.grid[0][1] = 1
        game.grid[0][2] = 1
        
        matches = game._find_matches()
        
        assert (0, 0) in matches
        assert (0, 1) in matches
        assert (0, 2) in matches
    
    def test_find_matches_vertical(self):
        """测试查找垂直匹配"""
        from src.systems.mini_games import BeghouledGame
        
        game = BeghouledGame()
        # 创建垂直匹配
        game.grid[0][0] = 2
        game.grid[1][0] = 2
        game.grid[2][0] = 2
        
        matches = game._find_matches()
        
        assert (0, 0) in matches
        assert (1, 0) in matches
        assert (2, 0) in matches
    
    def test_handle_click_select(self):
        """测试点击选择"""
        from src.systems.mini_games import BeghouledGame
        
        game = BeghouledGame()
        # 点击第一个单元格
        result = game.handle_click(240, 90)
        
        assert result
        assert game.selected_cell == (0, 0)


class TestWallnutBowling:
    """坚果保龄球测试"""

    def test_bowling_initialization(self):
        """测试保龄球初始化"""
        from src.systems.mini_games import WallnutBowling
        
        game = WallnutBowling()
        assert game is not None
        assert game.wallnuts_left == 10
        assert len(game.wallnuts) == 0
    
    def test_launch_wallnut(self):
        """测试发射坚果"""
        from src.systems.mini_games import WallnutBowling
        
        game = WallnutBowling()
        game.launch_wallnut(2)
        
        assert len(game.wallnuts) == 1
        assert game.wallnuts[0]['row'] == 2
        assert game.wallnuts_left == 9
    
    def test_wallnut_zombie_collision(self):
        """测试坚果与僵尸碰撞"""
        from src.systems.mini_games import WallnutBowling
        
        game = WallnutBowling()
        game.launch_wallnut(0)
        game.wallnuts[0]['x'] = 400
        game.wallnuts[0]['y'] = 150
        
        game.zombies.append({
            'x': 400,
            'y': 150,
            'vx': -40,
            'health': 100,
            'radius': 25
        })
        
        game.update(0.1)
        
        assert game.zombies[0]['health'] < 100


class TestMiniGameManager:
    """小游戏管理器测试"""

    def test_manager_initialization(self):
        """测试管理器初始化"""
        from src.systems.mini_games import MiniGameManager
        
        manager = MiniGameManager()
        assert manager is not None
        assert manager.current_game is None
    
    def test_start_zombie_aquarium(self):
        """测试启动僵尸水族馆"""
        from src.systems.mini_games import MiniGameManager, MiniGameType
        
        manager = MiniGameManager()
        manager.start_game(MiniGameType.ZOMBIE_AQUARIUM)
        
        assert manager.current_game is not None
        assert manager.game_type == MiniGameType.ZOMBIE_AQUARIUM
    
    def test_start_beghouled(self):
        """测试启动宝石迷阵"""
        from src.systems.mini_games import MiniGameManager, MiniGameType
        
        manager = MiniGameManager()
        manager.start_game(MiniGameType.BEGHOULED)
        
        assert manager.current_game is not None
        assert manager.game_type == MiniGameType.BEGHOULED
    
    def test_start_wallnut_bowling(self):
        """测试启动坚果保龄球"""
        from src.systems.mini_games import MiniGameManager, MiniGameType
        
        manager = MiniGameManager()
        manager.start_game(MiniGameType.WALLNUT_BOWLING)
        
        assert manager.current_game is not None
        assert manager.game_type == MiniGameType.WALLNUT_BOWLING
    
    def test_is_game_running(self):
        """测试游戏运行状态"""
        from src.systems.mini_games import MiniGameManager, MiniGameType
        
        manager = MiniGameManager()
        assert not manager.is_game_running()
        
        manager.start_game(MiniGameType.ZOMBIE_AQUARIUM)
        assert manager.is_game_running()
