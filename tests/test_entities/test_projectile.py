import pytest
from unittest.mock import MagicMock


class TestProjectile:
    """投射物测试"""

    def test_projectile_type_enum_exists(self):
        """测试投射物类型枚举存在"""
        from src.entities.projectile import ProjectileType
        
        assert hasattr(ProjectileType, 'PEA')
        assert hasattr(ProjectileType, 'FROZEN_PEA')
        assert hasattr(ProjectileType, 'CHERRY_BOMB')

    def test_projectile_initialization(self):
        """测试投射物初始化"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.PEA, 100, 200, 1)
        
        assert projectile.projectile_type == ProjectileType.PEA
        assert projectile.x == 100
        assert projectile.y == 200
        assert projectile.damage > 0
        assert projectile.speed > 0

    def test_projectile_move(self):
        """测试投射物移动"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.PEA, 100, 200, 1)
        initial_x = projectile.x
        
        projectile.update(1.0, MagicMock())
        assert projectile.x > initial_x

    def test_projectile_get_rect(self):
        """测试投射物获取碰撞矩形"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.PEA, 100, 200, 1)
        rect = projectile.get_rect()
        
        assert rect.centerx == 100
        assert rect.centery == 200

    def test_projectile_on_hit(self):
        """测试投射物命中"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.PEA, 100, 200, 1)
        assert projectile.is_dead() == False
        
        projectile.on_hit()
        assert projectile.is_dead() == True

    def test_projectile_out_of_bounds(self):
        """测试投射物超出边界"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.PEA, 950, 200, 1)
        
        projectile.update(1.0, MagicMock())
        assert projectile.is_dead() == True

    def test_frozen_pea_damage(self):
        """测试冰冻豌豆伤害"""
        from src.entities.projectile import Projectile, ProjectileType
        
        projectile = Projectile(ProjectileType.FROZEN_PEA, 100, 200, 1)
        
        assert projectile.damage > 0
        assert projectile.projectile_type == ProjectileType.FROZEN_PEA
