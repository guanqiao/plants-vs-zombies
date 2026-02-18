import pygame
from enum import Enum, auto
from typing import Dict, List, Callable, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class AchievementType(Enum):
    """成就类型枚举"""
    COMPLETE_ADVENTURE = auto()
    RICH = auto()
    GARDENER = auto()
    ZOMBIE_HUNTER = auto()
    PLANT_COLLECTOR = auto()
    EXPLOSION_EXPERT = auto()
    PEA_MASTER = auto()
    SUNFLOWER_LOVER = auto()
    WALLNUT_LOVER = auto()
    SPEED_KILLER = auto()
    IRON_ROOSTER = auto()
    SURVIVAL_EXPERT = auto()


@dataclass
class Achievement:
    """成就数据类"""
    achievement_type: AchievementType
    name: str
    description: str
    icon_color: tuple
    condition: Callable[['GameManager'], bool]
    unlocked: bool = False
    progress: int = 0
    target: int = 1


class AchievementSystem:
    """成就系统 - 管理游戏成就"""
    
    def __init__(self):
        self.achievements: Dict[AchievementType, Achievement] = {}
        self._init_achievements()
        
        # 统计数据
        self.stats = {
            'zombies_killed': 0,
            'zombies_killed_by_cherry': 0,
            'zombies_killed_by_pea': 0,
            'sunflowers_planted': 0,
            'wallnuts_planted': 0,
            'sun_collected_total': 0,
            'sun_spent_total': 0,
            'speed_kills': 0,
            'last_speed_kill_time': 0.0,
            'speed_kill_count': 0,
            'plants_unlocked': set(),
            'zombies_encountered': set(),
            'levels_completed': set(),
            'survival_waves': 0,
        }
        
        self.new_unlocks: List[Achievement] = []
    
    def _init_achievements(self):
        """初始化所有成就"""
        self.achievements = {
            AchievementType.COMPLETE_ADVENTURE: Achievement(
                AchievementType.COMPLETE_ADVENTURE,
                "庭院无忧",
                "完成冒险模式",
                (255, 215, 0),
                lambda gm: len(self.stats['levels_completed']) >= 7,
                target=7
            ),
            AchievementType.RICH: Achievement(
                AchievementType.RICH,
                "富可敌国",
                "累计获得80000金币",
                (255, 223, 0),
                lambda gm: self.stats['sun_collected_total'] >= 80000,
                target=80000
            ),
            AchievementType.GARDENER: Achievement(
                AchievementType.GARDENER,
                "宇宙之花",
                "填满禅境花园",
                (0, 255, 127),
                lambda gm: False,
                target=32
            ),
            AchievementType.ZOMBIE_HUNTER: Achievement(
                AchievementType.ZOMBIE_HUNTER,
                "僵尸猎手",
                "击败全部13种僵尸",
                (220, 20, 60),
                lambda gm: len(self.stats['zombies_encountered']) >= 13,
                target=13
            ),
            AchievementType.PLANT_COLLECTOR: Achievement(
                AchievementType.PLANT_COLLECTOR,
                "植物收藏家",
                "解锁全部15种植物",
                (0, 200, 0),
                lambda gm: len(self.stats['plants_unlocked']) >= 15,
                target=15
            ),
            AchievementType.EXPLOSION_EXPERT: Achievement(
                AchievementType.EXPLOSION_EXPERT,
                "爆破专家",
                "用樱桃炸弹炸死20只僵尸",
                (255, 69, 0),
                lambda gm: self.stats['zombies_killed_by_cherry'] >= 20,
                target=20
            ),
            AchievementType.PEA_MASTER: Achievement(
                AchievementType.PEA_MASTER,
                "豌豆先生",
                "用豌豆射手击杀50只僵尸",
                (0, 255, 0),
                lambda gm: self.stats['zombies_killed_by_pea'] >= 50,
                target=50
            ),
            AchievementType.SUNFLOWER_LOVER: Achievement(
                AchievementType.SUNFLOWER_LOVER,
                "向日葵爱好者",
                "单局种植5株向日葵",
                (255, 255, 0),
                lambda gm: self.stats['sunflowers_planted'] >= 5,
                target=5
            ),
            AchievementType.WALLNUT_LOVER: Achievement(
                AchievementType.WALLNUT_LOVER,
                "坚果墙爱好者",
                "单局种植5个坚果墙",
                (139, 69, 19),
                lambda gm: self.stats['wallnuts_planted'] >= 5,
                target=5
            ),
            AchievementType.SPEED_KILLER: Achievement(
                AchievementType.SPEED_KILLER,
                "极速者",
                "在3秒内击杀5只僵尸",
                (255, 0, 255),
                lambda gm: self.stats['speed_kills'] >= 1,
                target=1
            ),
            AchievementType.IRON_ROOSTER: Achievement(
                AchievementType.IRON_ROOSTER,
                "铁公鸡",
                "单局不花费阳光通关",
                (192, 192, 192),
                lambda gm: False,
                target=1
            ),
            AchievementType.SURVIVAL_EXPERT: Achievement(
                AchievementType.SURVIVAL_EXPERT,
                "生存专家",
                "生存模式坚持20波",
                (255, 140, 0),
                lambda gm: self.stats['survival_waves'] >= 20,
                target=20
            ),
        }
    
    def update_stat(self, stat_name: str, value: int = 1):
        """更新统计数据"""
        if stat_name in self.stats:
            if isinstance(self.stats[stat_name], int):
                self.stats[stat_name] += value
