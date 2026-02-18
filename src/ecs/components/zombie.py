"""
僵尸相关组件
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List


class ZombieType(Enum):
    """僵尸类型枚举"""
    NORMAL = auto()
    CONEHEAD = auto()
    BUCKETHEAD = auto()
    RUNNER = auto()
    GARGANTUAR = auto()
    POLE_VAULTER = auto()
    SCREEN_DOOR = auto()
    FOOTBALL = auto()
    DANCER = auto()
    BACKUP_DANCER = auto()
    BALLOON = auto()
    MINER = auto()
    POGO = auto()
    BUNGEE = auto()


@dataclass
class ZombieTypeComponent:
    """僵尸类型组件"""
    zombie_type: ZombieType


@dataclass
class ZombieComponent:
    """
    僵尸组件
    
    存储僵尸特有的属性和状态
    
    Attributes:
        damage: 攻击力
        attack_cooldown: 攻击冷却时间
        attack_timer: 当前攻击计时器
        is_attacking: 是否正在攻击
        score_value: 击杀得分
        slow_duration: 减速效果剩余时间
        slow_factor: 减速倍率
        has_armor: 是否有护甲
        armor_health: 护甲生命值
        has_pole: 是否有撑杆
        has_jumped: 是否已经跳跃
        is_flying: 是否飞行
        is_underground: 是否地下
        has_dug: 是否已经挖掘
        is_pogoing: 是否使用跳跳杆
        can_jump: 是否可以跳跃
        dancer_spawned: 是否已经召唤伴舞
        backup_dancers: 伴舞僵尸列表
        bungee_timer: 蹦极僵尸计时器
        bungee_target: 蹦极目标
    """
    damage: int = 20
    attack_cooldown: float = 1.0
    attack_timer: float = 0.0
    is_attacking: bool = False
    score_value: int = 10
    
    # 状态效果
    slow_duration: float = 0.0
    slow_factor: float = 1.0
    
    # 特殊属性
    has_armor: bool = False
    armor_health: int = 0
    has_pole: bool = False
    has_jumped: bool = False
    is_flying: bool = False
    is_underground: bool = False
    has_dug: bool = False
    is_pogoing: bool = False
    can_jump: bool = True
    
    # 舞王僵尸
    dancer_spawned: bool = False
    backup_dancers: List[int] = field(default_factory=list)
    
    # 蹦极僵尸
    bungee_timer: float = 0.0
    bungee_target: Optional[int] = None
    
    def update_timer(self, dt: float) -> None:
        """更新攻击计时器"""
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.attack_timer = 0
                self.is_attacking = False
        
        # 更新减速效果
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.slow_duration = 0
                self.slow_factor = 1.0
    
    def start_attack(self) -> None:
        """开始攻击"""
        self.is_attacking = True
        self.attack_timer = self.attack_cooldown
    
    def apply_slow(self, factor: float, duration: float) -> None:
        """应用减速效果"""
        self.slow_factor = factor
        self.slow_duration = duration
    
    def take_armor_damage(self, damage: int) -> int:
        """
        对护甲造成伤害
        
        Returns:
            剩余伤害值（护甲被击破后）
        """
        if not self.has_armor or self.armor_health <= 0:
            return damage
        
        self.armor_health -= damage
        if self.armor_health <= 0:
            remaining = -self.armor_health
            self.has_armor = False
            self.armor_health = 0
            return remaining
        return 0


# 僵尸配置字典
ZOMBIE_CONFIGS = {
    ZombieType.NORMAL: {
        'health': 100,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 80,
        'color': (128, 128, 128),
        'score_value': 10,
    },
    ZombieType.CONEHEAD: {
        'health': 200,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (255, 140, 0),
        'score_value': 20,
        'has_armor': True,
        'armor_health': 100,
    },
    ZombieType.BUCKETHEAD: {
        'health': 400,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (169, 169, 169),
        'score_value': 30,
        'has_armor': True,
        'armor_health': 300,
    },
    ZombieType.RUNNER: {
        'health': 80,
        'speed': -60,
        'damage': 15,
        'width': 45,
        'height': 75,
        'color': (220, 220, 220),
        'score_value': 15,
    },
    ZombieType.GARGANTUAR: {
        'health': 1500,
        'speed': -15,
        'damage': 100,
        'width': 80,
        'height': 120,
        'color': (105, 105, 105),
        'score_value': 100,
    },
    ZombieType.POLE_VAULTER: {
        'health': 100,
        'speed': -40,
        'damage': 20,
        'width': 50,
        'height': 85,
        'color': (180, 180, 200),
        'score_value': 25,
        'has_pole': True,
    },
    ZombieType.SCREEN_DOOR: {
        'health': 300,
        'speed': -30,
        'damage': 20,
        'width': 55,
        'height': 85,
        'color': (100, 100, 120),
        'score_value': 25,
        'has_armor': True,
        'armor_health': 200,
    },
    ZombieType.FOOTBALL: {
        'health': 800,
        'speed': -50,
        'damage': 30,
        'width': 55,
        'height': 90,
        'color': (139, 69, 19),
        'score_value': 50,
        'has_armor': True,
        'armor_health': 600,
    },
    ZombieType.DANCER: {
        'health': 200,
        'speed': -25,
        'damage': 20,
        'width': 55,
        'height': 90,
        'color': (128, 0, 128),
        'score_value': 40,
    },
    ZombieType.BACKUP_DANCER: {
        'health': 100,
        'speed': -25,
        'damage': 15,
        'width': 50,
        'height': 85,
        'color': (150, 50, 150),
        'score_value': 15,
    },
    ZombieType.BALLOON: {
        'health': 50,
        'speed': -35,
        'damage': 20,
        'width': 45,
        'height': 110,
        'color': (255, 100, 100),
        'score_value': 20,
        'is_flying': True,
    },
    ZombieType.MINER: {
        'health': 150,
        'speed': -35,
        'damage': 20,
        'width': 50,
        'height': 85,
        'color': (100, 80, 60),
        'score_value': 30,
    },
    ZombieType.POGO: {
        'health': 200,
        'speed': -45,
        'damage': 20,
        'width': 50,
        'height': 100,
        'color': (200, 150, 100),
        'score_value': 30,
        'is_pogoing': True,
    },
    ZombieType.BUNGEE: {
        'health': 100,
        'speed': 0,
        'damage': 0,
        'width': 50,
        'height': 80,
        'color': (100, 100, 150),
        'score_value': 25,
    },
}