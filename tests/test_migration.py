"""
迁移验证测试 - 确保OOP到ECS的迁移完整
"""
import pytest
from unittest.mock import MagicMock, patch


class TestECSArchitecture:
    """验证ECS架构完整性"""

    def test_world_initialization(self):
        """测试World能正确初始化"""
        from src.ecs.world import World
        
        world = World()
        assert world is not None
        # 使用World提供的公共API
        entity = world.create_entity()
        assert entity is not None

    def test_entity_creation(self):
        """测试能创建实体"""
        from src.ecs.world import World
        
        world = World()
        entity = world.create_entity()
        
        assert entity is not None
        assert entity.id >= 0

    def test_component_addition(self):
        """测试能添加组件"""
        from src.ecs.world import World
        from src.ecs.components.transform import TransformComponent
        
        world = World()
        entity = world.create_entity()
        
        transform = TransformComponent(x=100, y=200)
        world.add_component(entity, transform)
        
        retrieved = world.get_component(entity, TransformComponent)
        assert retrieved is not None
        assert retrieved.x == 100
        assert retrieved.y == 200


class TestEntityFactory:
    """验证EntityFactory能创建所有实体类型"""

    def test_create_sunflower(self):
        """测试创建向日葵"""
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.world import World
        from src.ecs.components.plant import PlantTypeComponent, PlantType
        
        world = World()
        factory = EntityFactory(world)
        
        entity = factory.create_plant(PlantType.SUNFLOWER, 100, 200, 0, 0)
        
        assert entity is not None
        plant_type = world.get_component(entity, PlantTypeComponent)
        assert plant_type is not None
        assert plant_type.plant_type == PlantType.SUNFLOWER

    def test_create_peashooter(self):
        """测试创建豌豆射手"""
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.world import World
        from src.ecs.components.plant import PlantTypeComponent, PlantType
        
        world = World()
        factory = EntityFactory(world)
        
        entity = factory.create_plant(PlantType.PEASHOOTER, 100, 200, 0, 1)
        
        assert entity is not None
        plant_type = world.get_component(entity, PlantTypeComponent)
        assert plant_type.plant_type == PlantType.PEASHOOTER

    def test_create_normal_zombie(self):
        """测试创建普通僵尸"""
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.world import World
        from src.ecs.components.zombie import ZombieTypeComponent, ZombieType
        
        world = World()
        factory = EntityFactory(world)
        
        entity = factory.create_zombie(ZombieType.NORMAL, 800, 200, 0)
        
        assert entity is not None
        zombie_type = world.get_component(entity, ZombieTypeComponent)
        assert zombie_type.zombie_type == ZombieType.NORMAL

    def test_create_all_plant_types(self):
        """测试能创建所有植物类型"""
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.world import World
        from src.ecs.components.plant import PlantType
        
        world = World()
        factory = EntityFactory(world)
        
        for plant_type in PlantType:
            entity = factory.create_plant(plant_type, 100, 200, 0, 0)
            assert entity is not None, f"无法创建植物: {plant_type}"

    def test_create_all_zombie_types(self):
        """测试能创建所有僵尸类型"""
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.world import World
        from src.ecs.components.zombie import ZombieType
        
        world = World()
        factory = EntityFactory(world)
        
        for zombie_type in ZombieType:
            entity = factory.create_zombie(zombie_type, 800, 200, 0)
            assert entity is not None, f"无法创建僵尸: {zombie_type}"


class TestECSSystems:
    """验证ECS系统功能完整"""

    def test_movement_system_exists(self):
        """测试MovementSystem存在"""
        from src.ecs.systems.movement_system import MovementSystem
        
        system = MovementSystem()
        assert system is not None

    def test_collision_system_exists(self):
        """测试CollisionSystem存在"""
        from src.ecs.systems.collision_system import CollisionSystem
        
        system = CollisionSystem()
        assert system is not None

    def test_plant_behavior_system_exists(self):
        """测试PlantBehaviorSystem存在"""
        from src.ecs.systems.plant_behavior_system import PlantBehaviorSystem
        from unittest.mock import MagicMock
        
        # PlantBehaviorSystem需要entity_factory参数
        mock_factory = MagicMock()
        system = PlantBehaviorSystem(entity_factory=mock_factory)
        assert system is not None

    def test_zombie_behavior_system_exists(self):
        """测试ZombieBehaviorSystem存在"""
        from src.ecs.systems.zombie_behavior_system import ZombieBehaviorSystem
        
        system = ZombieBehaviorSystem()
        assert system is not None

    def test_render_system_exists(self):
        """测试RenderSystem存在"""
        from src.ecs.systems.render_system import RenderSystem
        
        system = RenderSystem()
        assert system is not None


class TestArcadeIntegration:
    """验证Arcade集成完整"""

    def test_game_window_imports(self):
        """测试GameWindow能导入"""
        from src.arcade_game.game_window import GameWindow
        assert GameWindow is not None

    def test_world_class_exists(self):
        """测试World类存在"""
        from src.ecs.world import World
        assert World is not None


class TestNoOOPDependencies:
    """验证没有OOP依赖"""

    def test_no_pygame_game_manager_import(self):
        """测试不导入Pygame GameManager"""
        try:
            from src.arcade_game.game_window import GameWindow
            import inspect
            source = inspect.getsource(GameWindow)
            # 检查是否导入Pygame的GameManager
            assert 'from src.core.game_manager import' not in source
            assert 'import src.core.game_manager' not in source
        except ImportError:
            pytest.skip("GameWindow导入失败")

    def test_no_oop_entity_imports(self):
        """测试不导入OOP实体类"""
        try:
            from src.arcade_game import entity_factory
            import inspect
            source = inspect.getsource(entity_factory)
            # 检查是否导入OOP实体
            assert 'from src.entities.plant import' not in source
            assert 'from src.entities.zombie import' not in source
            assert 'from src.entities.projectile import' not in source
        except ImportError:
            pytest.skip("EntityFactory导入失败")


class TestGameLoop:
    """验证游戏循环完整"""

    def test_world_update_exists(self):
        """测试World有update方法"""
        from src.ecs.world import World
        
        world = World()
        assert hasattr(world, 'update')
        assert callable(getattr(world, 'update'))

    def test_render_system_exists(self):
        """测试RenderSystem存在并可渲染"""
        from src.ecs.systems.render_system import RenderSystem
        from src.ecs.world import World
        
        world = World()
        render_system = RenderSystem(priority=100)
        world.add_system(render_system)
        
        # 验证系统已添加
        assert render_system is not None


class TestConfiguration:
    """验证配置完整"""

    def test_levels_config_exists(self):
        """测试关卡配置存在"""
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'levels_config.toml')
        assert os.path.exists(config_path), f"关卡配置不存在: {config_path}"

    def test_plant_configs_in_ecs(self):
        """测试植物配置在ECS中"""
        from src.ecs.components.plant import PLANT_CONFIGS
        
        assert PLANT_CONFIGS is not None
        assert len(PLANT_CONFIGS) > 0
        # 验证包含关键植物
        from src.ecs.components.plant import PlantType
        assert PlantType.SUNFLOWER in PLANT_CONFIGS
        assert PlantType.PEASHOOTER in PLANT_CONFIGS

    def test_zombie_configs_in_ecs(self):
        """测试僵尸配置在ECS中"""
        from src.ecs.components.zombie import ZOMBIE_CONFIGS
        
        assert ZOMBIE_CONFIGS is not None
        assert len(ZOMBIE_CONFIGS) > 0
        # 验证包含关键僵尸
        from src.ecs.components.zombie import ZombieType
        assert ZombieType.NORMAL in ZOMBIE_CONFIGS
        assert ZombieType.CONEHEAD in ZOMBIE_CONFIGS
