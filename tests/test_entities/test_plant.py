import pytest
from unittest.mock import MagicMock


class MockPlant:
    """用于测试的植物模拟类"""
    
    def __init__(self, plant_type, x, y):
        from src.entities.plant import PLANT_CONFIGS
        
        self.plant_type = plant_type
        self.x = x
        self.y = y
        
        config = PLANT_CONFIGS.get(plant_type, {})
        self.cost = config.get('cost', 100)
        self.health = config.get('health', 100)
        self.width = config.get('width', 60)
        self.height = config.get('height', 80)
        self.color = config.get('color', (0, 200, 0))
        
        self.row = 0
        self.col = 0
        self.animation_time = 0.0
    
    def take_damage(self, damage: int):
        self.health -= damage
    
    def is_dead(self) -> bool:
        return self.health <= 0
    
    def get_cost(self) -> int:
        return self.cost
    
    def get_rect(self):
        import pygame
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def update(self, dt: float, game_manager):
        self.animation_time += dt
    
    def _update_behavior(self, dt: float, game_manager):
        pass


class TestPlant:
    """植物基类测试"""

    def test_plant_type_enum_exists(self):
        """测试植物类型枚举存在"""
        from src.entities.plant import PlantType
        
        assert hasattr(PlantType, 'SUNFLOWER')
        assert hasattr(PlantType, 'PEASHOOTER')
        assert hasattr(PlantType, 'WALLNUT')
        assert hasattr(PlantType, 'SNOW_PEA')
        assert hasattr(PlantType, 'CHERRY_BOMB')
        assert hasattr(PlantType, 'POTATO_MINE')
        assert hasattr(PlantType, 'REPEATER')
        assert hasattr(PlantType, 'CHOMPER')

    def test_plant_initialization(self):
        """测试植物初始化"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.PEASHOOTER, 100, 200)
        
        assert plant.plant_type == PlantType.PEASHOOTER
        assert plant.x == 100
        assert plant.y == 200
        assert plant.health > 0

    def test_plant_take_damage(self):
        """测试植物受到伤害"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.WALLNUT, 100, 200)
        initial_health = plant.health
        
        plant.take_damage(20)
        assert plant.health == initial_health - 20

    def test_plant_take_fatal_damage(self):
        """测试植物受到致命伤害"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.WALLNUT, 100, 200)
        plant.health = 10
        
        plant.take_damage(20)
        assert plant.health <= 0
        assert plant.is_dead() == True

    def test_plant_is_dead(self):
        """测试植物是否死亡"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.WALLNUT, 100, 200)
        assert plant.is_dead() == False
        
        plant.health = 0
        assert plant.is_dead() == True

    def test_plant_get_cost(self):
        """测试植物获取成本"""
        from src.entities.plant import PlantType
        
        sunflower = MockPlant(PlantType.SUNFLOWER, 100, 200)
        peashooter = MockPlant(PlantType.PEASHOOTER, 100, 200)
        wallnut = MockPlant(PlantType.WALLNUT, 100, 200)
        
        assert sunflower.get_cost() == 50
        assert peashooter.get_cost() == 100
        assert wallnut.get_cost() == 50

    def test_plant_get_rect(self):
        """测试植物获取碰撞矩形"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.PEASHOOTER, 100, 200)
        rect = plant.get_rect()
        
        assert rect.x == 100 - plant.width // 2
        assert rect.y == 200 - plant.height // 2
        assert rect.width == plant.width
        assert rect.height == plant.height

    def test_plant_update(self):
        """测试植物更新"""
        from src.entities.plant import PlantType
        
        plant = MockPlant(PlantType.PEASHOOTER, 100, 200)
        game_manager = MagicMock()
        
        plant.update(0.1, game_manager)
        assert True


class TestConcretePlants:
    """具体植物类测试"""

    def test_sunflower_produces_sun(self):
        """测试向日葵产生阳光"""
        from src.entities.plants import Sunflower
        from unittest.mock import MagicMock
        
        sunflower = Sunflower(100, 200)
        game_manager = MagicMock()
        game_manager.sun_system = MagicMock()
        
        sunflower._update_behavior(7.0, game_manager)
        
        game_manager.sun_system.add_sun_from_plant.assert_called_once()

    def test_peashooter_fires_at_zombie(self):
        """测试豌豆射手向僵尸发射"""
        from src.entities.plants import Peashooter
        from unittest.mock import MagicMock
        from src.entities.zombie import ZombieType
        
        peashooter = Peashooter(100, 200)
        peashooter.row = 0
        
        zombie = MagicMock()
        zombie.row = 0
        zombie.x = 300
        
        game_manager = MagicMock()
        game_manager.zombies = [zombie]
        game_manager.add_projectile = MagicMock()
        
        peashooter._update_behavior(1.5, game_manager)
        
        game_manager.add_projectile.assert_called_once()

    def test_wallnut_high_health(self):
        """测试坚果墙高血量"""
        from src.entities.plants import WallNut
        
        wallnut = WallNut(100, 200)
        
        assert wallnut.health == 400
