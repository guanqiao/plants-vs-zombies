"""
ECS (Entity-Component-System) 模块

提供高性能、可扩展的游戏架构支持
"""

from .world import World
from .entity import Entity, EntityManager
from .component import Component, ComponentManager
from .system import System, SystemManager

__all__ = [
    'World',
    'Entity',
    'EntityManager',
    'Component',
    'ComponentManager',
    'System',
    'SystemManager',
]