"""
小游戏模块

包含所有小游戏：
- ZombieAquarium: 僵尸水族馆
- BeghouledGame: 宝石迷阵
- WallnutBowling: 坚果保龄球
"""

from .types import MiniGameType
from .base_game import BaseMiniGame
from .aquarium import ZombieAquarium, AquariumZombie
from .beghouled import BeghouledGame
from .bowling import WallnutBowling
from .manager import MiniGameManager

__all__ = [
    'MiniGameType',
    'BaseMiniGame',
    'ZombieAquarium',
    'AquariumZombie',
    'BeghouledGame',
    'WallnutBowling',
    'MiniGameManager',
]
