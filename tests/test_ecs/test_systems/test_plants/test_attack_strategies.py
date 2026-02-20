"""
测试攻击策略模式
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.ecs.systems.plants.attack_strategies import (
    AttackStrategyRegistry,
    ShooterStrategy,
    SnowPeaStrategy,
    RepeaterStrategy,
    ThreepeaterStrategy,
    MelonPultStrategy,
    WinterMelonStrategy,
)
from src.ecs.components import PlantType, ProjectileType


class TestAttackStrategies:
    """测试攻击策略"""
    
    def test_shooter_strategy(self):
        """测试豌豆射手策略"""
        strategy = ShooterStrategy()
        
        # 创建mock对象
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2
        entity_factory = Mock()
        component_manager = Mock()
        
        # 执行策略
        result = strategy.execute(1, plant, transform, grid_pos, 
                                 entity_factory, component_manager)
        
        # 验证
        assert result is True
        entity_factory.create_projectile.assert_called_once_with(
            ProjectileType.PEA, 130, 200, 2
        )
    
    def test_snow_pea_strategy(self):
        """测试寒冰射手策略"""
        strategy = SnowPeaStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        entity_factory.create_projectile.assert_called_once_with(
            ProjectileType.FROZEN_PEA, 130, 200, 2
        )
    
    def test_repeater_strategy(self):
        """测试双发射手策略"""
        strategy = RepeaterStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        # 应该创建两个投射物
        assert entity_factory.create_projectile.call_count == 2
    
    def test_threepeater_strategy(self):
        """测试三线射手策略"""
        strategy = ThreepeaterStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2  # 中间行
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        # 应该创建三个投射物（当前行、上一行、下一行）
        assert entity_factory.create_projectile.call_count == 3
    
    def test_threepeater_strategy_edge_row(self):
        """测试三线射手在边缘行"""
        strategy = ThreepeaterStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 0  # 第一行，没有上一行
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        # 应该只创建两个投射物（当前行、下一行）
        assert entity_factory.create_projectile.call_count == 2
    
    def test_melon_pult_strategy(self):
        """测试西瓜投手策略"""
        strategy = MelonPultStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        entity_factory.create_projectile.assert_called_once_with(
            ProjectileType.MELON, 130, 200, 2
        )
    
    def test_winter_melon_strategy(self):
        """测试冰西瓜策略"""
        strategy = WinterMelonStrategy()
        
        plant = Mock()
        transform = Mock()
        transform.x = 100
        transform.y = 200
        grid_pos = Mock()
        grid_pos.row = 2
        entity_factory = Mock()
        component_manager = Mock()
        
        result = strategy.execute(1, plant, transform, grid_pos,
                                 entity_factory, component_manager)
        
        assert result is True
        entity_factory.create_projectile.assert_called_once_with(
            ProjectileType.WINTER_MELON, 130, 200, 2
        )


class TestAttackStrategyRegistry:
    """测试攻击策略注册表"""
    
    def test_register_and_get_strategy(self):
        """测试注册和获取策略"""
        strategy = ShooterStrategy()
        
        # 注册策略
        AttackStrategyRegistry.register(PlantType.PEASHOOTER, strategy)
        
        # 获取策略
        retrieved = AttackStrategyRegistry.get_strategy(PlantType.PEASHOOTER)
        
        assert retrieved is strategy
    
    def test_get_default_strategy(self):
        """测试获取默认策略"""
        # 获取未注册的策略应该返回默认策略
        strategy = AttackStrategyRegistry.get_strategy(PlantType.SUNFLOWER)
        
        assert isinstance(strategy, ShooterStrategy)
    
    def test_has_strategy(self):
        """测试检查是否有策略"""
        # 已注册的策略
        assert AttackStrategyRegistry.has_strategy(PlantType.PEASHOOTER) is True
        
        # 未注册的策略
        assert AttackStrategyRegistry.has_strategy(PlantType.SUNFLOWER) is False
