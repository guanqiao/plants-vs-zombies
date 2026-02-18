"""
测试实体工厂
"""

import pytest
from src.ecs import World
from src.arcade_game import EntityFactory
from src.ecs.components import (
    PlantType, ZombieType, ProjectileType,
    TransformComponent, SpriteComponent, HealthComponent,
    VelocityComponent, PlantComponent, ZombieComponent,
    ProjectileComponent, GridPositionComponent
)


class TestEntityFactory:
    """测试实体工厂"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.factory = EntityFactory(self.world)
    
    def test_create_plant(self):
        """测试创建植物"""
        entity = self.factory.create_plant(
            PlantType.PEASHOOTER,
            x=200, y=150,
            row=1, col=2
        )
        
        # 验证组件
        assert self.world.has_component(entity, TransformComponent)
        assert self.world.has_component(entity, SpriteComponent)
        assert self.world.has_component(entity, HealthComponent)
        assert self.world.has_component(entity, PlantComponent)
        assert self.world.has_component(entity, GridPositionComponent)
        
        # 验证属性
        transform = self.world.get_component(entity, TransformComponent)
        assert transform.x == 200
        assert transform.y == 150
        
        plant = self.world.get_component(entity, PlantComponent)
        assert plant.cost == 100
        assert plant.attack_damage == 20
        
        grid_pos = self.world.get_component(entity, GridPositionComponent)
        assert grid_pos.row == 1
        assert grid_pos.col == 2
    
    def test_create_zombie(self):
        """测试创建僵尸"""
        entity = self.factory.create_zombie(
            ZombieType.NORMAL,
            x=800, y=150,
            row=1
        )
        
        # 验证组件
        assert self.world.has_component(entity, TransformComponent)
        assert self.world.has_component(entity, SpriteComponent)
        assert self.world.has_component(entity, HealthComponent)
        assert self.world.has_component(entity, VelocityComponent)
        assert self.world.has_component(entity, ZombieComponent)
        
        # 验证属性
        transform = self.world.get_component(entity, TransformComponent)
        assert transform.x == 800
        
        velocity = self.world.get_component(entity, VelocityComponent)
        assert velocity.vx == -1.0  # 向左移动
        
        zombie = self.world.get_component(entity, ZombieComponent)
        assert zombie.damage == 20
    
    def test_create_projectile(self):
        """测试创建投射物"""
        entity = self.factory.create_projectile(
            ProjectileType.PEA,
            x=250, y=150,
            row=1
        )
        
        # 验证组件
        assert self.world.has_component(entity, TransformComponent)
        assert self.world.has_component(entity, SpriteComponent)
        assert self.world.has_component(entity, VelocityComponent)
        assert self.world.has_component(entity, ProjectileComponent)
        
        # 验证属性
        velocity = self.world.get_component(entity, VelocityComponent)
        assert velocity.vx == 1.0  # 向右移动
        
        projectile = self.world.get_component(entity, ProjectileComponent)
        assert projectile.damage == 20
    
    def test_create_sun(self):
        """测试创建阳光"""
        entity = self.factory.create_sun(
            x=300, y=400,
            amount=25,
            is_auto=False
        )
        
        # 验证组件
        assert self.world.has_component(entity, TransformComponent)
        assert self.world.has_component(entity, SpriteComponent)
        
        # 验证下落速度
        velocity = self.world.get_component(entity, VelocityComponent)
        assert velocity is not None
        assert velocity.vy == -1.0
    
    def test_different_plant_types(self):
        """测试不同类型的植物"""
        sunflower = self.factory.create_plant(
            PlantType.SUNFLOWER, x=100, y=100, row=0, col=0
        )
        wallnut = self.factory.create_plant(
            PlantType.WALLNUT, x=200, y=100, row=0, col=1
        )
        
        # 向日葵应该有阳光生产组件
        from src.ecs.components import SunProducerComponent
        assert self.world.has_component(sunflower, SunProducerComponent)
        
        # 验证不同生命值
        sunflower_health = self.world.get_component(sunflower, HealthComponent)
        wallnut_health = self.world.get_component(wallnut, HealthComponent)
        
        assert sunflower_health.max_health == 100
        assert wallnut_health.max_health == 400  # 坚果墙生命值更高
    
    def test_different_zombie_types(self):
        """测试不同类型的僵尸"""
        normal = self.factory.create_zombie(
            ZombieType.NORMAL, x=800, y=100, row=0
        )
        buckethead = self.factory.create_zombie(
            ZombieType.BUCKETHEAD, x=800, y=200, row=1
        )
        
        # 验证不同生命值
        normal_health = self.world.get_component(normal, HealthComponent)
        buckethead_health = self.world.get_component(buckethead, HealthComponent)
        
        assert normal_health.max_health == 100
        assert buckethead_health.max_health == 400  # 铁桶僵尸生命值更高
        
        # 验证护甲
        normal_zombie = self.world.get_component(normal, ZombieComponent)
        buckethead_zombie = self.world.get_component(buckethead, ZombieComponent)
        
        assert not normal_zombie.has_armor
        assert buckethead_zombie.has_armor
        assert buckethead_zombie.armor_health == 300