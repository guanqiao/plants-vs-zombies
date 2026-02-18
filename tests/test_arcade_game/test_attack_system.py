"""
测试攻击系统
"""

import pytest
from src.ecs import World
from src.arcade_game.entity_factory import EntityFactory
from src.ecs.systems import PlantBehaviorSystem, ProjectileSystem
from src.ecs.components import (
    PlantType, ZombieType, ProjectileType,
    TransformComponent, PlantComponent, ZombieComponent,
    ProjectileComponent, HealthComponent, GridPositionComponent,
    VelocityComponent
)


class TestPlantBehaviorSystem:
    """测试植物行为系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.plant_system = PlantBehaviorSystem(self.entity_factory, priority=40)
    
    def test_shooter_plant_attacks_when_zombie_in_row(self):
        """测试射手植物在僵尸进入行时攻击"""
        # 创建植物（第2行）
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=2
        )
        
        # 创建僵尸（同一行）
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=600, y=150, row=1
        )
        
        # 更新植物系统
        self.plant_system.update(0.1, self.world._component_manager)
        
        # 检查是否生成了投射物
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) > 0
    
    def test_shooter_plant_no_attack_when_no_zombie(self):
        """测试没有僵尸时植物不攻击"""
        # 创建植物（第2行）
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=2
        )
        
        # 不创建僵尸
        
        # 更新植物系统
        self.plant_system.update(0.1, self.world._component_manager)
        
        # 检查是否没有投射物
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) == 0
    
    def test_plant_attack_cooldown(self):
        """测试植物攻击冷却"""
        # 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=2
        )
        
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=600, y=150, row=1
        )
        
        # 第一次更新，应该攻击
        self.plant_system.update(0.1, self.world._component_manager)
        projectiles1 = len(self.world.query_entities(
            TransformComponent, ProjectileComponent
        ))
        assert projectiles1 > 0
        
        # 立即再次更新，不应该产生新投射物（冷却中）
        self.plant_system.update(0.1, self.world._component_manager)
        projectiles2 = len(self.world.query_entities(
            TransformComponent, ProjectileComponent
        ))
        assert projectiles2 == projectiles1  # 数量不变


class TestProjectileSystem:
    """测试投射物系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.projectile_system = ProjectileSystem(
            self.world._entity_manager, priority=35
        )
    
    def test_projectile_hits_zombie(self):
        """测试投射物击中僵尸"""
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=300, y=150, row=1
        )
        zombie_health = self.world.get_component(zombie, HealthComponent)
        initial_health = zombie_health.current
        
        # 创建投射物（在僵尸位置）
        projectile = self.entity_factory.create_projectile(
            ProjectileType.PEA, x=300, y=150, row=1
        )
        
        # 更新投射物系统
        self.projectile_system.update(0.1, self.world._component_manager)
        
        # 检查僵尸受到伤害
        zombie_health = self.world.get_component(zombie, HealthComponent)
        assert zombie_health.current < initial_health
    
    def test_projectile_moves_forward(self):
        """测试投射物向前移动"""
        # 创建投射物
        projectile = self.entity_factory.create_projectile(
            ProjectileType.PEA, x=200, y=150, row=1
        )
        
        transform = self.world.get_component(projectile, TransformComponent)
        initial_x = transform.x
        
        # 手动移动投射物（模拟移动系统）
        velocity = self.world.get_component(projectile, VelocityComponent)
        transform.x += velocity.vx * velocity.base_speed * 1.0  # dt=1.0
        
        # 检查投射物向前移动
        assert transform.x > initial_x
    
    def test_frozen_pea_applies_slow(self):
        """测试冰冻豌豆施加减速效果"""
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=300, y=150, row=1
        )
        
        # 创建冰冻投射物
        projectile = self.entity_factory.create_projectile(
            ProjectileType.FROZEN_PEA, x=300, y=150, row=1
        )
        
        # 更新投射物系统
        self.projectile_system.update(0.1, self.world._component_manager)
        
        # 检查僵尸被减速
        zombie_comp = self.world.get_component(zombie, ZombieComponent)
        assert zombie_comp.slow_factor < 1.0
    
    def test_projectile_removed_when_hits_zombie(self):
        """测试投射物击中僵尸后被移除"""
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=300, y=150, row=1
        )
        
        # 创建投射物（在僵尸位置）
        projectile = self.entity_factory.create_projectile(
            ProjectileType.PEA, x=300, y=150, row=1
        )
        
        # 检查投射物存在
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) == 1
        
        # 更新投射物系统，击中僵尸
        self.projectile_system.update(0.1, self.world._component_manager)
        
        # 检查投射物被移除
        self.world.update(0.1)  # 触发实体销毁
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) == 0


class TestAttackSystemIntegration:
    """测试攻击系统集成"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.plant_system = PlantBehaviorSystem(self.entity_factory, priority=40)
        self.projectile_system = ProjectileSystem(
            self.world._entity_manager, priority=35
        )
    
    def test_full_attack_workflow(self):
        """测试完整攻击流程"""
        # 1. 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=2
        )
        
        # 2. 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=400, y=150, row=1
        )
        zombie_health = self.world.get_component(zombie, HealthComponent)
        initial_health = zombie_health.current
        
        # 3. 植物攻击，产生投射物
        self.plant_system.update(0.1, self.world._component_manager)
        
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) > 0
        
        # 4. 移动投射物到僵尸位置
        from src.ecs import Entity
        projectile_entity = Entity()
        projectile_entity.id = projectiles[0]
        transform = self.world.get_component(projectile_entity, TransformComponent)
        transform.x = 400  # 直接设置到僵尸位置
        
        # 5. 投射物击中僵尸
        self.projectile_system.update(0.1, self.world._component_manager)
        
        # 6. 检查僵尸受伤
        zombie_health = self.world.get_component(zombie, HealthComponent)
        assert zombie_health.current < initial_health
    
    def test_multiple_shooters_attack_same_zombie(self):
        """测试多个射手攻击同一个僵尸"""
        # 创建两个豌豆射手
        plant1 = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=1
        )
        plant2 = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=200, y=150, row=1, col=2
        )
        
        # 创建一个僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=600, y=150, row=1
        )
        
        # 更新多次，让两个植物都攻击
        for _ in range(5):
            self.plant_system.update(0.5, self.world._component_manager)
        
        # 检查产生了多个投射物
        projectiles = self.world.query_entities(
            TransformComponent, ProjectileComponent
        )
        assert len(projectiles) >= 2
