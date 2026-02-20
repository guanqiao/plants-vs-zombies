"""
植物卡片冷却系统测试 - TDD方式开发
"""
import pytest
from unittest.mock import MagicMock, patch


class TestCooldownComponent:
    """测试冷却组件"""

    def test_cooldown_component_initialization(self):
        """测试冷却组件初始化"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(
            cooldown_time=5.0,
            plant_type="PEASHOOTER"
        )
        
        assert cooldown.cooldown_time == 5.0
        assert cooldown.current_cooldown == 0.0
        assert cooldown.plant_type == "PEASHOOTER"
        assert cooldown.is_ready() is True

    def test_cooldown_component_start_cooldown(self):
        """测试开始冷却"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown.start_cooldown()
        
        assert cooldown.current_cooldown == 5.0
        assert cooldown.is_ready() is False

    def test_cooldown_component_update(self):
        """测试冷却更新"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown.start_cooldown()
        
        # 更新2秒
        cooldown.update(2.0)
        
        assert cooldown.current_cooldown == 3.0
        assert cooldown.is_ready() is False

    def test_cooldown_component_complete(self):
        """测试冷却完成"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown.start_cooldown()
        
        # 更新5秒
        cooldown.update(5.0)
        
        assert cooldown.current_cooldown == 0.0
        assert cooldown.is_ready() is True

    def test_cooldown_component_over_cooldown(self):
        """测试超过冷却时间"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown.start_cooldown()
        
        # 更新10秒（超过冷却时间）
        cooldown.update(10.0)
        
        assert cooldown.current_cooldown == 0.0
        assert cooldown.is_ready() is True

    def test_cooldown_component_progress(self):
        """测试冷却进度"""
        from src.ecs.components.cooldown import CooldownComponent
        
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        
        # 未开始冷却时进度为1.0
        assert cooldown.get_progress() == 1.0
        
        cooldown.start_cooldown()
        assert cooldown.get_progress() == 0.0
        
        cooldown.update(2.5)
        assert cooldown.get_progress() == 0.5


class TestCooldownSystem:
    """测试冷却系统"""

    def test_cooldown_system_initialization(self):
        """测试冷却系统初始化"""
        from src.ecs.systems.cooldown_system import CooldownSystem
        
        system = CooldownSystem(priority=50)
        
        assert system is not None
        assert system.priority == 50

    def test_cooldown_system_updates_all_cooldowns(self):
        """测试系统更新所有冷却组件"""
        from src.ecs.systems.cooldown_system import CooldownSystem
        from src.ecs.components.cooldown import CooldownComponent
        from src.ecs.component import ComponentManager
        
        component_manager = ComponentManager()
        system = CooldownSystem(priority=50)
        
        # 创建带冷却组件的实体
        entity1 = 1
        cooldown1 = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown1.start_cooldown()
        component_manager.add_component(entity1, cooldown1)
        
        entity2 = 2
        cooldown2 = CooldownComponent(cooldown_time=3.0, plant_type="SUNFLOWER")
        cooldown2.start_cooldown()
        component_manager.add_component(entity2, cooldown2)
        
        # 更新系统
        system.update(1.0, component_manager)
        
        # 验证冷却已更新
        assert cooldown1.current_cooldown == 4.0
        assert cooldown2.current_cooldown == 2.0

    def test_cooldown_system_only_updates_active(self):
        """测试系统只更新激活的冷却"""
        from src.ecs.systems.cooldown_system import CooldownSystem
        from src.ecs.components.cooldown import CooldownComponent
        from src.ecs.component import ComponentManager
        
        component_manager = ComponentManager()
        system = CooldownSystem(priority=50)
        
        # 创建已完成的冷却
        entity = 1
        cooldown = CooldownComponent(cooldown_time=5.0, plant_type="PEASHOOTER")
        cooldown.current_cooldown = 0.0  # 已完成
        component_manager.add_component(entity, cooldown)
        
        # 更新系统
        system.update(1.0, component_manager)
        
        # 验证冷却保持为0
        assert cooldown.current_cooldown == 0.0


class TestCooldownIntegration:
    """测试冷却系统集成"""

    def test_cooldown_with_planting_system(self):
        """测试冷却与种植系统集成"""
        from src.arcade_game.planting_system import PlantingSystem, PlantCard
        from src.ecs.world import World
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.components.plant import PlantType
        
        world = World()
        factory = EntityFactory(world)
        planting_system = PlantingSystem(world, factory)
        
        # 清除默认卡片，创建测试用的卡片
        planting_system.cards.clear()
        
        # 创建测试卡片
        card = PlantCard(PlantType.PEASHOOTER, 150, 550)
        card.cost = 100
        card.cooldown_duration = 5.0
        planting_system.cards.append(card)
        
        # 初始状态可以种植（先更新卡片状态）
        planting_system.update(0, 1000)  # 更新卡片状态，提供足够阳光
        assert planting_system.can_plant("PEASHOOTER") is True
        
        # 种植后进入冷却
        result = planting_system.plant("PEASHOOTER", 4, 8)
        
        # 验证种植成功
        assert result is not None, "种植应该成功"
        
        # 种植后应该进入冷却（再次更新卡片状态）
        planting_system.update(0, 1000)
        assert planting_system.can_plant("PEASHOOTER") is False
        
        # 更新5秒后冷却完成（提供足够的阳光）
        planting_system.update(5.0, 1000)
        assert planting_system.can_plant("PEASHOOTER") is True
