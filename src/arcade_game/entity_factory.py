"""
实体工厂 - 创建游戏实体的工厂类
"""

from ..ecs import World, Entity
from ..ecs.components import (
    TransformComponent, SpriteComponent, HealthComponent,
    VelocityComponent, CollisionComponent, GridPositionComponent,
    PlantComponent, PlantTypeComponent, PlantType, PLANT_CONFIGS,
    ZombieComponent, ZombieTypeComponent, ZombieType, ZOMBIE_CONFIGS,
    ProjectileComponent, ProjectileTypeComponent, ProjectileType, PROJECTILE_CONFIGS,
    SunProducerComponent
)
from ..ecs.systems import CollisionSystem


class EntityFactory:
    """
    实体工厂
    
    提供创建各种游戏实体的便捷方法
    """
    
    def __init__(self, world: World):
        self.world = world
    
    def create_plant(self, plant_type: PlantType, x: float, y: float, 
                     row: int, col: int) -> Entity:
        """
        创建植物实体
        
        Args:
            plant_type: 植物类型
            x: X坐标
            y: Y坐标
            row: 网格行
            col: 网格列
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = PLANT_CONFIGS.get(plant_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (0, 200, 0)),
            width=config.get('width', 60),
            height=config.get('height', 80)
        )
        self.world.add_component(entity, sprite)
        
        # 生命值组件
        health = HealthComponent(
            current=config.get('health', 100),
            max_health=config.get('health', 100)
        )
        self.world.add_component(entity, health)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 60),
            height=config.get('height', 80),
            layer=CollisionSystem.LAYER_PLANT,
            collides_with={CollisionSystem.LAYER_ZOMBIE}
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=col, is_occupied=True)
        self.world.add_component(entity, grid_pos)
        
        # 植物类型组件
        plant_type_comp = PlantTypeComponent(plant_type=plant_type)
        self.world.add_component(entity, plant_type_comp)
        
        # 植物组件
        plant = PlantComponent(
            cost=config.get('cost', 100),
            attack_cooldown=config.get('attack_cooldown', 1.5),
            attack_damage=config.get('attack_damage', 20),
            is_armed=config.get('is_armed', True)
        )
        self.world.add_component(entity, plant)
        
        # 阳光生产组件（仅向日葵）
        if plant_type == PlantType.SUNFLOWER:
            sun_producer = SunProducerComponent(
                production_amount=25,
                production_interval=5.0,
                is_auto=True
            )
            self.world.add_component(entity, sun_producer)
        
        return entity
    
    def create_zombie(self, zombie_type: ZombieType, x: float, y: float,
                      row: int) -> Entity:
        """
        创建僵尸实体
        
        Args:
            zombie_type: 僵尸类型
            x: X坐标
            y: Y坐标
            row: 所在行
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = ZOMBIE_CONFIGS.get(zombie_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (128, 128, 128)),
            width=config.get('width', 50),
            height=config.get('height', 80)
        )
        self.world.add_component(entity, sprite)
        
        # 生命值组件
        health = HealthComponent(
            current=config.get('health', 100),
            max_health=config.get('health', 100)
        )
        self.world.add_component(entity, health)
        
        # 速度组件
        velocity = VelocityComponent(
            vx=-1.0,  # 向左移动
            vy=0.0,
            base_speed=abs(config.get('speed', 30))
        )
        self.world.add_component(entity, velocity)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 50),
            height=config.get('height', 80),
            layer=CollisionSystem.LAYER_ZOMBIE,
            collides_with={CollisionSystem.LAYER_PLANT, CollisionSystem.LAYER_PROJECTILE}
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=-1)
        self.world.add_component(entity, grid_pos)
        
        # 僵尸类型组件
        zombie_type_comp = ZombieTypeComponent(zombie_type=zombie_type)
        self.world.add_component(entity, zombie_type_comp)
        
        # 僵尸组件
        zombie = ZombieComponent(
            damage=config.get('damage', 20),
            score_value=config.get('score_value', 10),
            has_armor=config.get('has_armor', False),
            armor_health=config.get('armor_health', 0),
            has_pole=config.get('has_pole', False),
            is_flying=config.get('is_flying', False),
            is_pogoing=config.get('is_pogoing', False)
        )
        self.world.add_component(entity, zombie)
        
        return entity
    
    def create_projectile(self, projectile_type: ProjectileType, 
                          x: float, y: float, row: int) -> Entity:
        """
        创建投射物实体
        
        Args:
            projectile_type: 投射物类型
            x: X坐标
            y: Y坐标
            row: 所在行
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = PROJECTILE_CONFIGS.get(projectile_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (0, 255, 0)),
            width=config.get('width', 15),
            height=config.get('height', 15)
        )
        self.world.add_component(entity, sprite)
        
        # 速度组件
        velocity = VelocityComponent(
            vx=1.0,  # 向右移动
            vy=0.0,
            base_speed=config.get('speed', 300.0)
        )
        self.world.add_component(entity, velocity)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 15),
            height=config.get('height', 15),
            layer=CollisionSystem.LAYER_PROJECTILE,
            collides_with={CollisionSystem.LAYER_ZOMBIE},
            is_trigger=True
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=-1)
        self.world.add_component(entity, grid_pos)
        
        # 投射物类型组件
        projectile_type_comp = ProjectileTypeComponent(projectile_type=projectile_type)
        self.world.add_component(entity, projectile_type_comp)
        
        # 投射物组件
        projectile = ProjectileComponent(
            damage=config.get('damage', 20),
            speed=config.get('speed', 300.0),
            is_splash=config.get('is_splash', False),
            splash_radius=config.get('splash_radius', 50.0),
            applies_slow=config.get('applies_slow', False),
            slow_factor=config.get('slow_factor', 0.5),
            slow_duration=config.get('slow_duration', 3.0),
            lifetime=config.get('lifetime', 5.0)
        )
        self.world.add_component(entity, projectile)
        
        return entity
    
    def create_sun(self, x: float, y: float, amount: int = 25,
                   is_auto: bool = False) -> Entity:
        """
        创建阳光实体
        
        Args:
            x: X坐标
            y: Y坐标
            amount: 阳光数量
            is_auto: 是否自动产生
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件（黄色圆形）
        sprite = SpriteComponent(
            color=(255, 255, 0),
            width=40,
            height=40
        )
        self.world.add_component(entity, sprite)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=40,
            height=40,
            layer=CollisionSystem.LAYER_SUN,
            is_trigger=True
        )
        self.world.add_component(entity, collision)
        
        # 阳光生产组件
        sun_producer = SunProducerComponent(
            production_amount=amount,
            is_auto=is_auto,
            is_collectable=True
        )
        self.world.add_component(entity, sun_producer)
        
        # 速度组件（下落）
        if not is_auto:
            velocity = VelocityComponent(
                vx=0.0,
                vy=-1.0,
                base_speed=50.0
            )
            self.world.add_component(entity, velocity)
        
        return entity