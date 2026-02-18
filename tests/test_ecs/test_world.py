"""
测试ECS World模块
"""

import pytest
from src.ecs import World
from src.ecs.components import (
    TransformComponent, SpriteComponent, HealthComponent,
    PlantComponent, PlantType, PlantTypeComponent
)


class TestWorld:
    """测试World类"""
    
    def test_create_entity(self):
        """测试创建实体"""
        world = World()
        entity = world.create_entity()
        
        assert entity is not None
        assert entity.id >= 0
        assert entity.active
    
    def test_add_component(self):
        """测试添加组件"""
        world = World()
        entity = world.create_entity()
        
        transform = TransformComponent(x=100, y=200)
        world.add_component(entity, transform)
        
        retrieved = world.get_component(entity, TransformComponent)
        assert retrieved is not None
        assert retrieved.x == 100
        assert retrieved.y == 200
    
    def test_remove_component(self):
        """测试移除组件"""
        world = World()
        entity = world.create_entity()
        
        transform = TransformComponent(x=100, y=200)
        world.add_component(entity, transform)
        
        assert world.has_component(entity, TransformComponent)
        
        world.remove_component(entity, TransformComponent)
        
        assert not world.has_component(entity, TransformComponent)
    
    def test_query_entities(self):
        """测试查询实体"""
        world = World()
        
        # 创建实体1：有Transform和Sprite
        entity1 = world.create_entity()
        world.add_component(entity1, TransformComponent(x=0, y=0))
        world.add_component(entity1, SpriteComponent(color=(255, 0, 0), width=50, height=50))
        
        # 创建实体2：只有Transform
        entity2 = world.create_entity()
        world.add_component(entity2, TransformComponent(x=100, y=100))
        
        # 查询同时拥有Transform和Sprite的实体
        result = world.query_entities(TransformComponent, SpriteComponent)
        
        assert len(result) == 1
        assert entity1.id in result
    
    def test_destroy_entity(self):
        """测试销毁实体"""
        world = World()
        entity = world.create_entity()
        
        world.add_component(entity, TransformComponent(x=0, y=0))
        world.add_component(entity, HealthComponent(current=100, max_health=100))
        
        world.destroy_entity(entity)
        world.update(0.016)  # 触发实体销毁处理
        
        assert not entity.active
    
    def test_multiple_components(self):
        """测试一个实体有多个组件"""
        world = World()
        entity = world.create_entity()
        
        world.add_component(entity, TransformComponent(x=100, y=200))
        world.add_component(entity, SpriteComponent(color=(0, 255, 0), width=60, height=80))
        world.add_component(entity, HealthComponent(current=100, max_health=100))
        
        assert world.has_component(entity, TransformComponent)
        assert world.has_component(entity, SpriteComponent)
        assert world.has_component(entity, HealthComponent)


class TestPlantComponents:
    """测试植物相关组件"""
    
    def test_plant_creation(self):
        """测试创建植物实体"""
        world = World()
        entity = world.create_entity()
        
        # 添加植物类型组件
        world.add_component(entity, PlantTypeComponent(plant_type=PlantType.PEASHOOTER))
        
        # 添加植物组件
        plant = PlantComponent(
            cost=100,
            attack_cooldown=1.5,
            attack_damage=20
        )
        world.add_component(entity, plant)
        
        # 添加其他必要组件
        world.add_component(entity, TransformComponent(x=200, y=150))
        world.add_component(entity, SpriteComponent(color=(0, 200, 0), width=60, height=80))
        world.add_component(entity, HealthComponent(current=100, max_health=100))
        
        # 验证
        plant_type_comp = world.get_component(entity, PlantTypeComponent)
        assert plant_type_comp.plant_type == PlantType.PEASHOOTER
        
        plant_comp = world.get_component(entity, PlantComponent)
        assert plant_comp.cost == 100
        assert plant_comp.attack_damage == 20
    
    def test_plant_attack_cooldown(self):
        """测试植物攻击冷却"""
        plant = PlantComponent(attack_cooldown=1.0)
        
        assert plant.can_attack()
        
        plant.start_cooldown()
        assert not plant.can_attack()
        
        # 模拟时间流逝
        plant.update_timer(0.5)
        assert not plant.can_attack()
        
        plant.update_timer(0.5)
        assert plant.can_attack()


class TestHealthComponent:
    """测试生命值组件"""
    
    def test_take_damage(self):
        """测试受到伤害"""
        health = HealthComponent(current=100, max_health=100)
        
        health.take_damage(30)
        assert health.current == 70
        assert not health.is_dead
        
        health.take_damage(70)
        assert health.current == 0
        assert health.is_dead
    
    def test_heal(self):
        """测试恢复生命"""
        health = HealthComponent(current=50, max_health=100)
        
        health.heal(30)
        assert health.current == 80
        
        health.heal(50)  # 超过最大值
        assert health.current == 100
    
    def test_health_percent(self):
        """测试生命值百分比"""
        health = HealthComponent(current=50, max_health=100)
        
        assert health.get_health_percent() == 0.5
        
        health.take_damage(50)
        assert health.get_health_percent() == 0.0


class TestTransformComponent:
    """测试变换组件"""
    
    def test_position(self):
        """测试位置设置"""
        transform = TransformComponent(x=100, y=200)
        
        assert transform.x == 100
        assert transform.y == 200
        
        transform.set_position(300, 400)
        assert transform.x == 300
        assert transform.y == 400
    
    def test_translate(self):
        """测试平移"""
        transform = TransformComponent(x=100, y=100)
        
        transform.translate(50, -30)
        assert transform.x == 150
        assert transform.y == 70