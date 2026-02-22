"""
Arcade游戏模块

使用Arcade引擎和ECS架构的游戏实现
"""

from .game_window import GameWindow
from .entity_factory import EntityFactory
from .zombie_animation_renderer import ZombieAnimationRenderer, ZombieBodyPart
from .zombie_visual_system import ZombieVisualSystem, DeathType
from .special_zombie_effects import SpecialZombieEffects
from .zombie_render_system import ZombieRenderSystem
from .zombie_effects import ZombieEffects, ZombieExpression, get_zombie_effects
from .zombie_render_integration import ZombieRenderIntegration, get_zombie_render_integration
from .zombie_lod_system import ZombieLODSystem, LODLevel, LODConfig, get_zombie_lod_system

__all__ = [
    'GameWindow',
    'EntityFactory',
    'ZombieAnimationRenderer',
    'ZombieBodyPart',
    'ZombieVisualSystem',
    'DeathType',
    'SpecialZombieEffects',
    'ZombieRenderSystem',
    'ZombieEffects',
    'ZombieExpression',
    'get_zombie_effects',
    'ZombieRenderIntegration',
    'get_zombie_render_integration',
    'ZombieLODSystem',
    'LODLevel',
    'LODConfig',
    'get_zombie_lod_system',
]