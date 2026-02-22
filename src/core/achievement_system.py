"""
成就系统 - 管理游戏成就

包括：
- 成就定义和存储
- 进度追踪
- 解锁通知
- 成就持久化
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json
import os
from .logger import get_module_logger


logger = get_module_logger(__name__)


class AchievementType(Enum):
    """成就类型枚举"""
    # 游戏进度类
    FIRST_WIN = auto()           # 首次通关
    COMPLETE_LEVEL_5 = auto()    # 完成第5关
    COMPLETE_ALL_LEVELS = auto() # 完成所有关卡
    
    # 战斗类
    KILL_100_ZOMBIES = auto()    # 击杀100个僵尸
    KILL_1000_ZOMBIES = auto()   # 击杀1000个僵尸
    KILL_GARGANTUAR = auto()     # 击杀巨人僵尸
    
    # 收集类
    COLLECT_1000_SUN = auto()    # 收集1000阳光
    COLLECT_10000_SUN = auto()   # 收集10000阳光
    
    # 策略类
    NO_SUN_PLANT_WIN = auto()    # 不使用向日葵通关
    ONLY_SHOOTERS_WIN = auto()   # 只使用射手通关
    PERFECT_DEFENSE = auto()     # 完美防御（无僵尸通过）
    
    # 特殊类
    FIRST_PLANT = auto()         # 首次种植
    FIRST_ZOMBIE_KILL = auto()   # 首次击杀僵尸
    USE_CHERRY_BOMB = auto()     # 使用樱桃炸弹
    USE_POTATO_MINE = auto()     # 使用土豆雷


@dataclass
class Achievement:
    """
    成就数据类
    
    Attributes:
        achievement_type: 成就类型
        name: 成就名称
        description: 成就描述
        icon: 成就图标路径
        is_unlocked: 是否已解锁
        unlock_time: 解锁时间
        progress: 当前进度
        max_progress: 最大进度（0表示无进度要求）
        is_hidden: 是否是隐藏成就
    """
    achievement_type: AchievementType
    name: str = ""
    description: str = ""
    icon: str = ""
    is_unlocked: bool = False
    unlock_time: Optional[str] = None
    progress: int = 0
    max_progress: int = 0
    is_hidden: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'achievement_type': self.achievement_type.name,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'is_unlocked': self.is_unlocked,
            'unlock_time': self.unlock_time,
            'progress': self.progress,
            'max_progress': self.max_progress,
            'is_hidden': self.is_hidden
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        """从字典创建"""
        return cls(
            achievement_type=AchievementType[data['achievement_type']],
            name=data.get('name', ''),
            description=data.get('description', ''),
            icon=data.get('icon', ''),
            is_unlocked=data.get('is_unlocked', False),
            unlock_time=data.get('unlock_time'),
            progress=data.get('progress', 0),
            max_progress=data.get('max_progress', 0),
            is_hidden=data.get('is_hidden', False)
        )


# 成就定义配置
ACHIEVEMENT_DEFINITIONS: Dict[AchievementType, Dict[str, Any]] = {
    AchievementType.FIRST_WIN: {
        'name': '初次胜利',
        'description': '完成第一关',
        'icon': 'achievements/first_win.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.COMPLETE_LEVEL_5: {
        'name': '进阶玩家',
        'description': '完成第5关',
        'icon': 'achievements/level_5.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.COMPLETE_ALL_LEVELS: {
        'name': '通关大师',
        'description': '完成所有关卡',
        'icon': 'achievements/all_levels.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.KILL_100_ZOMBIES: {
        'name': '僵尸猎手',
        'description': '累计击杀100个僵尸',
        'icon': 'achievements/kill_100.png',
        'max_progress': 100,
        'is_hidden': False
    },
    AchievementType.KILL_1000_ZOMBIES: {
        'name': '僵尸杀手',
        'description': '累计击杀1000个僵尸',
        'icon': 'achievements/kill_1000.png',
        'max_progress': 1000,
        'is_hidden': False
    },
    AchievementType.KILL_GARGANTUAR: {
        'name': '巨人克星',
        'description': '击杀一个巨人僵尸',
        'icon': 'achievements/kill_gargantuar.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.COLLECT_1000_SUN: {
        'name': '阳光收集者',
        'description': '累计收集1000阳光',
        'icon': 'achievements/sun_1000.png',
        'max_progress': 1000,
        'is_hidden': False
    },
    AchievementType.COLLECT_10000_SUN: {
        'name': '阳光富翁',
        'description': '累计收集10000阳光',
        'icon': 'achievements/sun_10000.png',
        'max_progress': 10000,
        'is_hidden': False
    },
    AchievementType.NO_SUN_PLANT_WIN: {
        'name': '无阳光挑战',
        'description': '不使用向日葵完成一关',
        'icon': 'achievements/no_sunflower.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.ONLY_SHOOTERS_WIN: {
        'name': '射手专精',
        'description': '只使用射手类植物完成一关',
        'icon': 'achievements/only_shooters.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.PERFECT_DEFENSE: {
        'name': '完美防御',
        'description': '不让任何僵尸通过防线',
        'icon': 'achievements/perfect_defense.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.FIRST_PLANT: {
        'name': '初次种植',
        'description': '种植第一个植物',
        'icon': 'achievements/first_plant.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.FIRST_ZOMBIE_KILL: {
        'name': '初次击杀',
        'description': '击杀第一个僵尸',
        'icon': 'achievements/first_kill.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.USE_CHERRY_BOMB: {
        'name': '爆破专家',
        'description': '使用樱桃炸弹',
        'icon': 'achievements/cherry_bomb.png',
        'max_progress': 1,
        'is_hidden': False
    },
    AchievementType.USE_POTATO_MINE: {
        'name': '地雷专家',
        'description': '使用土豆雷',
        'icon': 'achievements/potato_mine.png',
        'max_progress': 1,
        'is_hidden': False
    }
}


class AchievementManager:
    """
    成就管理器
    
    管理所有成就的解锁和进度追踪
    
    Attributes:
        achievements: 成就字典
        on_unlock_callback: 解锁回调函数
    """
    
    def __init__(self, save_dir: str = "saves"):
        """
        初始化成就管理器
        
        Args:
            save_dir: 存档目录
        """
        self.save_dir = save_dir
        self.achievements: Dict[AchievementType, Achievement] = {}
        self.on_unlock_callbacks: List[Callable[[Achievement], None]] = []
        
        # 初始化成就
        self._init_achievements()
        
        # 加载已保存的成就进度
        self._load_progress()
    
    def _init_achievements(self) -> None:
        """初始化所有成就"""
        for achievement_type, config in ACHIEVEMENT_DEFINITIONS.items():
            self.achievements[achievement_type] = Achievement(
                achievement_type=achievement_type,
                name=config['name'],
                description=config['description'],
                icon=config['icon'],
                max_progress=config['max_progress'],
                is_hidden=config['is_hidden']
            )
    
    def _get_save_path(self) -> str:
        """获取成就存档路径"""
        return os.path.join(self.save_dir, "achievements.json")
    
    def _load_progress(self) -> None:
        """加载成就进度"""
        save_path = self._get_save_path()
        
        if not os.path.exists(save_path):
            return
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for achievement_data in data.get('achievements', []):
                try:
                    achievement_type = AchievementType[achievement_data['achievement_type']]
                    if achievement_type in self.achievements:
                        # 更新成就数据
                        existing = self.achievements[achievement_type]
                        existing.is_unlocked = achievement_data.get('is_unlocked', False)
                        existing.unlock_time = achievement_data.get('unlock_time')
                        existing.progress = achievement_data.get('progress', 0)
                except KeyError:
                    continue
            
            logger.info("成就进度已加载")
            
        except Exception as e:
            logger.error(f"加载成就进度失败: {e}")
    
    def save_progress(self) -> bool:
        """
        保存成就进度
        
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            
            data = {
                'achievements': [
                    achievement.to_dict()
                    for achievement in self.achievements.values()
                ]
            }
            
            save_path = self._get_save_path()
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info("成就进度已保存")
            return True
            
        except Exception as e:
            logger.error(f"保存成就进度失败: {e}")
            return False
    
    def unlock(self, achievement_type: AchievementType) -> bool:
        """
        解锁成就
        
        Args:
            achievement_type: 成就类型
            
        Returns:
            是否成功解锁（如果已解锁则返回False）
        """
        if achievement_type not in self.achievements:
            logger.warning(f"未知成就类型: {achievement_type}")
            return False
        
        achievement = self.achievements[achievement_type]
        
        if achievement.is_unlocked:
            return False
        
        # 解锁成就
        achievement.is_unlocked = True
        achievement.unlock_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        achievement.progress = achievement.max_progress
        
        logger.info(f"成就解锁: {achievement.name}")
        
        # 触发回调
        for callback in self.on_unlock_callbacks:
            callback(achievement)
        
        # 自动保存
        self.save_progress()
        
        return True
    
    def update_progress(self, achievement_type: AchievementType, progress: int) -> bool:
        """
        更新成就进度
        
        Args:
            achievement_type: 成就类型
            progress: 当前进度值
            
        Returns:
            是否解锁了新成就
        """
        if achievement_type not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_type]
        
        if achievement.is_unlocked:
            return False
        
        # 更新进度
        achievement.progress = min(progress, achievement.max_progress)
        
        # 检查是否达成
        if achievement.progress >= achievement.max_progress:
            return self.unlock(achievement_type)
        
        return False
    
    def add_progress(self, achievement_type: AchievementType, amount: int = 1) -> bool:
        """
        增加成就进度
        
        Args:
            achievement_type: 成就类型
            amount: 增加的数量
            
        Returns:
            是否解锁了新成就
        """
        if achievement_type not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_type]
        return self.update_progress(achievement_type, achievement.progress + amount)
    
    def is_unlocked(self, achievement_type: AchievementType) -> bool:
        """
        检查成就是否已解锁
        
        Args:
            achievement_type: 成就类型
            
        Returns:
            是否已解锁
        """
        if achievement_type not in self.achievements:
            return False
        
        return self.achievements[achievement_type].is_unlocked
    
    def get_progress(self, achievement_type: AchievementType) -> int:
        """
        获取成就进度
        
        Args:
            achievement_type: 成就类型
            
        Returns:
            当前进度
        """
        if achievement_type not in self.achievements:
            return 0
        
        return self.achievements[achievement_type].progress
    
    def get_achievement(self, achievement_type: AchievementType) -> Optional[Achievement]:
        """
        获取成就信息
        
        Args:
            achievement_type: 成就类型
            
        Returns:
            成就对象，如果不存在则返回None
        """
        return self.achievements.get(achievement_type)
    
    def get_all_achievements(self) -> List[Achievement]:
        """
        获取所有成就
        
        Returns:
            成就列表
        """
        return list(self.achievements.values())
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """
        获取已解锁的成就
        
        Returns:
            已解锁成就列表
        """
        return [a for a in self.achievements.values() if a.is_unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """
        获取未解锁的成就
        
        Returns:
            未解锁成就列表
        """
        return [a for a in self.achievements.values() if not a.is_unlocked]
    
    def get_unlock_count(self) -> int:
        """
        获取已解锁成就数量
        
        Returns:
            已解锁成就数
        """
        return sum(1 for a in self.achievements.values() if a.is_unlocked)
    
    def get_total_count(self) -> int:
        """
        获取总成就数量
        
        Returns:
            总成就数
        """
        return len(self.achievements)
    
    def get_completion_percentage(self) -> float:
        """
        获取完成百分比
        
        Returns:
            完成百分比 (0.0 - 100.0)
        """
        if not self.achievements:
            return 0.0
        
        return (self.get_unlock_count() / self.get_total_count()) * 100
    
    def register_unlock_callback(self, callback: Callable[[Achievement], None]) -> None:
        """
        注册解锁回调函数
        
        Args:
            callback: 回调函数，接收Achievement参数
        """
        self.on_unlock_callbacks.append(callback)
    
    def unregister_unlock_callback(self, callback: Callable[[Achievement], None]) -> None:
        """
        注销解锁回调函数
        
        Args:
            callback: 要注销的回调函数
        """
        if callback in self.on_unlock_callbacks:
            self.on_unlock_callbacks.remove(callback)
    
    def reset_all(self) -> None:
        """重置所有成就"""
        for achievement in self.achievements.values():
            achievement.is_unlocked = False
            achievement.unlock_time = None
            achievement.progress = 0
        
        self.save_progress()
        logger.info("所有成就已重置")
    
    def reset_progress(self, achievement_type: AchievementType) -> bool:
        """
        重置特定成就的进度
        
        Args:
            achievement_type: 成就类型
            
        Returns:
            是否成功重置
        """
        if achievement_type not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_type]
        achievement.is_unlocked = False
        achievement.unlock_time = None
        achievement.progress = 0
        
        self.save_progress()
        return True


# 全局成就管理器实例
_achievement_manager: Optional[AchievementManager] = None


def get_achievement_manager(save_dir: str = "saves") -> AchievementManager:
    """获取全局成就管理器实例"""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager(save_dir)
    return _achievement_manager


def init_achievement_manager(save_dir: str = "saves") -> AchievementManager:
    """初始化成就管理器"""
    global _achievement_manager
    _achievement_manager = AchievementManager(save_dir)
    return _achievement_manager
