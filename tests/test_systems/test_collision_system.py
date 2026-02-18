import pytest
from unittest.mock import MagicMock


class TestCollisionSystem:
    """碰撞系统测试"""

    def test_collision_system_initialization(self):
        """测试碰撞系统初始化"""
        from src.systems.collision_system import CollisionSystem
        
        system = CollisionSystem()
        assert system is not None

    def test_projectile_zombie_collision(self):
        """测试投射物与僵尸碰撞"""
        from src.systems.collision_system import CollisionSystem
        from src.entities.projectile import Projectile, ProjectileType
        from src.entities.zombie import Zombie, ZombieType
        from unittest.mock import MagicMock
        
        system = CollisionSystem()
        
        projectile = MagicMock()
        projectile.get_rect.return_value = MagicMock()
        projectile.get_rect.return_value.colliderect.return_value = True
        projectile.damage = 20
        projectile.projectile_type = MagicMock()
        projectile.projectile_type.name = 'PEA'
        
        zombie = MagicMock()
        zombie.get_rect.return_value = MagicMock()
        zombie.get_rect.return_value.colliderect.return_value = True
        zombie.health = 100
        
        game_manager = MagicMock()
        game_manager.projectiles = [projectile]
        game_manager.zombies = [zombie]
        
        system.check_collisions(game_manager)
        
        zombie.take_damage.assert_called()

    def test_zombie_plant_collision(self):
        """测试僵尸与植物碰撞"""
        from src.systems.collision_system import CollisionSystem
        from unittest.mock import MagicMock
        
        system = CollisionSystem()
        
        plant = MagicMock()
        plant.get_rect.return_value = MagicMock()
        plant.get_rect.return_value.colliderect.return_value = True
        plant.x = 200
        plant.row = 0
        
        zombie = MagicMock()
        zombie.get_rect.return_value = MagicMock()
        zombie.get_rect.return_value.colliderect.return_value = True
        zombie.x = 200
        zombie.row = 0
        zombie.is_attacking = False
        zombie.attack_cooldown = 0
        
        game_manager = MagicMock()
        game_manager.plants = [plant]
        game_manager.zombies = [zombie]
        game_manager.projectiles = []
        
        system.check_collisions(game_manager)
        
        zombie.attack.assert_called()

    def test_no_collision_when_far_apart(self):
        """测试距离远时无碰撞"""
        from src.systems.collision_system import CollisionSystem
        from unittest.mock import MagicMock
        
        system = CollisionSystem()
        
        plant = MagicMock()
        plant.get_rect.return_value = MagicMock()
        plant.get_rect.return_value.colliderect.return_value = False
        plant.row = 0
        
        zombie = MagicMock()
        zombie.get_rect.return_value = MagicMock()
        zombie.get_rect.return_value.colliderect.return_value = False
        zombie.is_attacking = False
        zombie.row = 1
        
        game_manager = MagicMock()
        game_manager.plants = [plant]
        game_manager.zombies = [zombie]
        game_manager.projectiles = []
        
        system.check_collisions(game_manager)
        
        zombie.attack.assert_not_called()

    def test_remove_dead_entities(self):
        """测试移除死亡实体"""
        from src.systems.collision_system import CollisionSystem
        from unittest.mock import MagicMock
        
        system = CollisionSystem()
        
        dead_plant = MagicMock()
        dead_plant.is_dead.return_value = True
        
        dead_zombie = MagicMock()
        dead_zombie.is_dead.return_value = True
        
        dead_projectile = MagicMock()
        dead_projectile.is_dead.return_value = True
        
        game_manager = MagicMock()
        game_manager.plants = [dead_plant]
        game_manager.zombies = [dead_zombie]
        game_manager.projectiles = [dead_projectile]
        
        system.check_collisions(game_manager)
        
        game_manager.remove_plant.assert_called_with(dead_plant)
        game_manager.remove_zombie.assert_called_with(dead_zombie)
        game_manager.remove_projectile.assert_called_with(dead_projectile)
