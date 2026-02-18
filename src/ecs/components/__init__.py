"""
ECS组件定义模块

包含游戏中使用的所有组件类型
组件是纯数据容器，用于描述实体特性
"""

from .transform import TransformComponent
from .sprite import SpriteComponent
from .health import HealthComponent
from .velocity import VelocityComponent
from .grid import GridPositionComponent
from .plant import PlantComponent, PlantTypeComponent, PlantType, PLANT_CONFIGS
from .zombie import ZombieComponent, ZombieTypeComponent, ZombieType, ZOMBIE_CONFIGS
from .projectile import ProjectileComponent, ProjectileTypeComponent, ProjectileType, PROJECTILE_CONFIGS
from .collision import CollisionComponent
from .attack import AttackComponent
from .sun import SunProducerComponent

__all__ = [
    'TransformComponent',
    'SpriteComponent',
    'HealthComponent',
    'VelocityComponent',
    'GridPositionComponent',
    'PlantComponent',
    'PlantTypeComponent',
    'PlantType',
    'PLANT_CONFIGS',
    'ZombieComponent',
    'ZombieTypeComponent',
    'ZombieType',
    'ZOMBIE_CONFIGS',
    'ProjectileComponent',
    'ProjectileTypeComponent',
    'ProjectileType',
    'PROJECTILE_CONFIGS',
    'CollisionComponent',
    'AttackComponent',
    'SunProducerComponent',
]