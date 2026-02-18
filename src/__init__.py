# ECS + Arcade 架构统一入口
from src.ecs import World, Entity, Component, System
from src.ecs.components import (
    TransformComponent, SpriteComponent, HealthComponent,
    VelocityComponent, GridPositionComponent, PlantComponent,
    PlantTypeComponent, PlantType, ZombieComponent,
    ZombieTypeComponent, ZombieType, ProjectileComponent,
    ProjectileTypeComponent, ProjectileType, CollisionComponent,
    AttackComponent, SunProducerComponent
)
from src.ecs.systems import (
    MovementSystem, CollisionSystem, ProjectileSystem,
    HealthSystem, ZombieBehaviorSystem, PlantBehaviorSystem,
    SunSystem, WaveSystem, RenderSystem
)

__all__ = [
    # ECS Core
    'World', 'Entity', 'Component', 'System',
    # Components
    'TransformComponent', 'SpriteComponent', 'HealthComponent',
    'VelocityComponent', 'GridPositionComponent', 'PlantComponent',
    'PlantTypeComponent', 'PlantType', 'ZombieComponent',
    'ZombieTypeComponent', 'ZombieType', 'ProjectileComponent',
    'ProjectileTypeComponent', 'ProjectileType', 'CollisionComponent',
    'AttackComponent', 'SunProducerComponent',
    # Systems
    'MovementSystem', 'CollisionSystem', 'ProjectileSystem',
    'HealthSystem', 'ZombieBehaviorSystem', 'PlantBehaviorSystem',
    'SunSystem', 'WaveSystem', 'RenderSystem',
]
