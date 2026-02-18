import pytest
from unittest.mock import MagicMock


class TestZombie:
    """僵尸基类测试"""

    def test_zombie_type_enum_exists(self):
        """测试僵尸类型枚举存在"""
        from src.entities.zombie import ZombieType
        
        assert hasattr(ZombieType, 'NORMAL')
        assert hasattr(ZombieType, 'CONEHEAD')
        assert hasattr(ZombieType, 'BUCKETHEAD')
        assert hasattr(ZombieType, 'RUNNER')
        assert hasattr(ZombieType, 'GARGANTUAR')

    def test_zombie_initialization(self):
        """测试僵尸初始化"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        
        assert zombie.zombie_type == ZombieType.NORMAL
        assert zombie.x == 800
        assert zombie.y == 150
        assert zombie.health > 0
        assert zombie.speed < 0

    def test_zombie_take_damage(self):
        """测试僵尸受到伤害"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        initial_health = zombie.health
        
        zombie.take_damage(20)
        assert zombie.health == initial_health - 20

    def test_zombie_take_fatal_damage(self):
        """测试僵尸受到致命伤害"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        zombie.health = 10
        
        zombie.take_damage(20)
        assert zombie.health <= 0
        assert zombie.is_dead() == True

    def test_zombie_is_dead(self):
        """测试僵尸是否死亡"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        assert zombie.is_dead() == False
        
        zombie.health = 0
        assert zombie.is_dead() == True

    def test_zombie_move(self):
        """测试僵尸移动"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        initial_x = zombie.x
        
        zombie.update(1.0, MagicMock())
        assert zombie.x < initial_x

    def test_zombie_get_rect(self):
        """测试僵尸获取碰撞矩形"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        rect = zombie.get_rect()
        
        assert rect.x == 800 - zombie.width // 2
        assert rect.y == 150 - zombie.height // 2
        assert rect.width == zombie.width
        assert rect.height == zombie.height

    def test_zombie_attack_plant(self):
        """测试僵尸攻击植物"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        zombie.is_attacking = True
        zombie.attack_cooldown = 0
        
        plant = MagicMock()
        plant.health = 100
        
        zombie.attack(plant)
        assert plant.take_damage.called or plant.health < 100

    def test_zombie_different_types_health(self):
        """测试不同类型僵尸血量"""
        from src.entities.zombie import Zombie, ZombieType
        
        normal = Zombie(ZombieType.NORMAL, 800, 150)
        conehead = Zombie(ZombieType.CONEHEAD, 800, 150)
        buckethead = Zombie(ZombieType.BUCKETHEAD, 800, 150)
        
        assert conehead.health > normal.health
        assert buckethead.health > conehead.health

    def test_zombie_score_value(self):
        """测试僵尸分值"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        assert zombie.score_value > 0

    def test_zombie_slow_down(self):
        """测试僵尸减速"""
        from src.entities.zombie import Zombie, ZombieType
        
        zombie = Zombie(ZombieType.NORMAL, 800, 150)
        normal_speed = zombie.speed
        
        zombie.apply_slow(0.5, 3.0)
        assert abs(zombie.speed) < abs(normal_speed)
        
        zombie.remove_slow()
        assert zombie.speed == normal_speed
