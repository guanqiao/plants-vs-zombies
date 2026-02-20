"""
测试僵尸水族馆小游戏
"""

import pytest
from src.systems.mini_games.aquarium import AquariumZombie, ZombieAquarium


class TestAquariumZombie:
    """测试水族馆僵尸"""
    
    def test_initialization(self):
        """测试初始化"""
        zombie = AquariumZombie(x=100, y=200)
        
        assert zombie.x == 100
        assert zombie.y == 200
        assert zombie.size == 30
        assert zombie.hunger == 0.0
        assert zombie.is_alive is True
    
    def test_update(self):
        """测试更新"""
        zombie = AquariumZombie(x=100, y=200)
        
        initial_x = zombie.x
        zombie.update(0.1)
        
        # 饥饿度增加
        assert zombie.hunger > 0
        # 位置变化（随机游动）
        assert zombie.x != initial_x
    
    def test_feed(self):
        """测试喂食"""
        zombie = AquariumZombie(x=100, y=200)
        zombie.hunger = 50
        
        zombie.feed()
        
        assert zombie.hunger == 20  # 50 - 30
    
    def test_can_produce_gold(self):
        """测试金币产生"""
        zombie = AquariumZombie(x=100, y=200)
        
        # 初始状态不能产生金币
        assert not zombie.can_produce_gold()
        
        # 设置可以产生金币的条件
        zombie.hunger = 40
        zombie.gold_timer = 10.0
        
        assert zombie.can_produce_gold()
    
    def test_collect_gold(self):
        """测试收集金币"""
        zombie = AquariumZombie(x=100, y=200)
        zombie.gold_timer = 10.0
        
        gold = zombie.collect_gold()
        
        assert gold in [10, 25, 50]
        assert zombie.gold_timer == 0.0


class TestZombieAquarium:
    """测试僵尸水族馆游戏"""
    
    def test_initialization(self):
        """测试初始化"""
        game = ZombieAquarium()
        
        assert game.running is True
        assert game.score == 0
        assert len(game.zombies) == 0
        assert game.food_count == 3
        assert game.gold == 0
    
    def test_add_zombie(self):
        """测试添加僵尸"""
        game = ZombieAquarium()
        
        game.add_zombie(100, 200)
        
        assert len(game.zombies) == 1
    
    def test_add_zombie_max_limit(self):
        """测试添加僵尸达到上限"""
        game = ZombieAquarium()
        
        # 添加超过上限的僵尸
        for i in range(15):
            game.add_zombie(100 + i, 200)
        
        assert len(game.zombies) == game.max_zombies
    
    def test_feed_zombie(self):
        """测试喂食僵尸"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        game.zombies[0].hunger = 50
        
        result = game.feed_zombie(100, 200)
        
        assert result is True
        assert game.food_count == 2
        assert game.zombies[0].hunger == 20
    
    def test_feed_zombie_no_food(self):
        """测试没有食物时喂食"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        game.food_count = 0
        
        result = game.feed_zombie(100, 200)
        
        assert result is False
    
    def test_collect_gold(self):
        """测试收集金币"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        game.zombies[0].hunger = 40
        game.zombies[0].gold_timer = 10.0
        
        gold = game.collect_gold(100, 200)
        
        assert gold > 0
        assert game.gold >= gold
        assert game.score >= gold
    
    def test_game_over_by_time(self):
        """测试时间到游戏结束"""
        game = ZombieAquarium()
        
        game.update(200.0)  # 超过最大时间
        
        assert game.running is False
    
    def test_game_over_by_starvation(self):
        """测试僵尸饿死游戏结束"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        
        # 让僵尸饿死
        for _ in range(100):
            game.update(1.0)
        
        assert len(game.zombies) == 0
        assert game.running is False
    
    def test_handle_click_feed(self):
        """测试点击喂食"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        game.zombies[0].hunger = 50
        
        result = game.handle_click(100, 200)
        
        assert result is True
        assert game.food_count == 2
    
    def test_handle_click_collect_gold(self):
        """测试点击收集金币"""
        game = ZombieAquarium()
        game.add_zombie(100, 200)
        game.zombies[0].hunger = 40
        game.zombies[0].gold_timer = 10.0
        
        result = game.handle_click(100, 200)
        
        assert result is True
        assert game.gold > 0
    
    def test_get_score(self):
        """测试获取分数"""
        game = ZombieAquarium()
        game.score = 100
        
        assert game.get_score() == 100
    
    def test_is_game_over(self):
        """测试游戏结束检查"""
        game = ZombieAquarium()
        
        assert game.is_game_over() is False
        
        game.running = False
        
        assert game.is_game_over() is True
