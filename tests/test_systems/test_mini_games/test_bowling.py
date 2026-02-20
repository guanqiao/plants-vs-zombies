"""
测试坚果保龄球小游戏
"""

import pytest
from src.systems.mini_games.bowling import BowlingNut, BowlingZombie, WallnutBowling


class TestBowlingNut:
    """测试保龄球坚果"""
    
    def test_initialization(self):
        """测试初始化"""
        nut = BowlingNut(x=50, y=100, vx=300, vy=0)
        
        assert nut.x == 50
        assert nut.y == 100
        assert nut.vx == 300
        assert nut.vy == 0
        assert nut.radius == 20
        assert nut.is_active is True
    
    def test_update(self):
        """测试更新位置"""
        nut = BowlingNut(x=50, y=100, vx=300, vy=0)
        
        nut.update(0.1)
        
        assert nut.x == 80  # 50 + 300 * 0.1
        assert nut.y == 100  # 没有垂直速度
    
    def test_deactivate_on_boundary(self):
        """测试边界外失活"""
        nut = BowlingNut(x=50, y=100, vx=300, vy=0)
        
        # 移动出边界
        nut.update(5.0)
        
        assert nut.is_active is False


class TestBowlingZombie:
    """测试保龄球僵尸"""
    
    def test_initialization(self):
        """测试初始化"""
        zombie = BowlingZombie(x=900, y=200)
        
        assert zombie.x == 900
        assert zombie.y == 200
        assert zombie.is_alive is True
    
    def test_update(self):
        """测试更新位置"""
        zombie = BowlingZombie(x=900, y=200)
        
        zombie.update(0.1)
        
        assert zombie.x == 895  # 900 - 50 * 0.1


class TestWallnutBowling:
    """测试坚果保龄球游戏"""
    
    def test_initialization(self):
        """测试初始化"""
        game = WallnutBowling()
        
        assert game.running is True
        assert game.score == 0
        assert len(game.nuts) == 0
        assert len(game.zombies) == 0
        assert game.nuts_remaining == 10
        assert game.zombies_killed == 0
    
    def test_spawn_zombie(self):
        """测试生成僵尸"""
        game = WallnutBowling()
        
        game._spawn_zombie()
        
        assert len(game.zombies) == 1
        assert game.zombies[0].x == 900
    
    def test_handle_click_launch_nut(self):
        """测试点击发射坚果"""
        game = WallnutBowling()
        
        result = game.handle_click(50, 200)
        
        assert result is True
        assert len(game.nuts) == 1
        assert game.nuts_remaining == 9
        assert game.nuts[0].x == 50
        assert game.nuts[0].y == 200
    
    def test_handle_click_no_nuts(self):
        """测试没有坚果时点击"""
        game = WallnutBowling()
        game.nuts_remaining = 0
        
        result = game.handle_click(50, 200)
        
        assert result is False
        assert len(game.nuts) == 0
    
    def test_collision_detection(self):
        """测试碰撞检测"""
        game = WallnutBowling()
        
        # 创建坚果和僵尸在相同位置
        nut = BowlingNut(x=100, y=200, vx=300, vy=0)
        zombie = BowlingZombie(x=100, y=200)
        
        game.nuts.append(nut)
        game.zombies.append(zombie)
        
        # 更新游戏（触发碰撞检测）
        game.update(0.1)
        
        # 僵尸应该被击倒
        assert zombie.is_alive is False
        assert game.zombies_killed == 1
        assert game.score == 100
    
    def test_game_over_by_time(self):
        """测试时间到游戏结束"""
        game = WallnutBowling()
        
        game.update(150.0)  # 超过最大时间
        
        assert game.running is False
    
    def test_game_over_by_no_nuts(self):
        """测试坚果用完游戏结束"""
        game = WallnutBowling()
        game.nuts_remaining = 0
        
        game.update(0.1)
        
        assert game.running is False
    
    def test_cleanup_inactive_nuts(self):
        """测试清理不活跃的坚果"""
        game = WallnutBowling()
        
        # 创建一个即将出边界的坚果
        nut = BowlingNut(x=850, y=200, vx=300, vy=0)
        game.nuts.append(nut)
        
        game.update(1.0)
        
        # 坚果应该被清理
        assert len(game.nuts) == 0
    
    def test_cleanup_dead_zombies(self):
        """测试清理死亡的僵尸"""
        game = WallnutBowling()
        
        # 创建一个死亡的僵尸
        zombie = BowlingZombie(x=-100, y=200)
        game.zombies.append(zombie)
        
        game.update(0.1)
        
        # 僵尸应该被清理
        assert len(game.zombies) == 0
    
    def test_get_score(self):
        """测试获取分数"""
        game = WallnutBowling()
        game.score = 500
        
        assert game.get_score() == 500
    
    def test_is_game_over(self):
        """测试游戏结束检查"""
        game = WallnutBowling()
        
        assert game.is_game_over() is False
        
        game.running = False
        
        assert game.is_game_over() is True
