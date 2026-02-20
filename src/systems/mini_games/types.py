"""
小游戏类型定义
"""

from enum import Enum, auto


class MiniGameType(Enum):
    """小游戏类型枚举"""
    ZOMBIE_AQUARIUM = auto()
    BEGHOULED = auto()
    WALLNUT_BOWLING = auto()
