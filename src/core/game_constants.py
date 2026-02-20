"""
游戏常量定义

集中管理所有游戏相关的常量，避免魔法数字分散在代码中
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GridConfig:
    """
    网格配置
    
    游戏主网格的配置参数
    """
    ROWS: int = 5
    COLS: int = 9
    CELL_WIDTH: float = 80.0
    CELL_HEIGHT: float = 100.0
    START_X: float = 100.0
    START_Y: float = 50.0
    
    @property
    def WIDTH(self) -> float:
        """网格总宽度"""
        return self.COLS * self.CELL_WIDTH
    
    @property
    def HEIGHT(self) -> float:
        """网格总高度"""
        return self.ROWS * self.CELL_HEIGHT


@dataclass(frozen=True)
class ScreenConfig:
    """
    屏幕配置
    
    游戏窗口和屏幕相关配置
    """
    WIDTH: int = 900
    HEIGHT: int = 600
    TITLE: str = "植物大战僵尸 - Python Arcade版"
    FPS: int = 60


@dataclass(frozen=True)
class GameConfig:
    """
    游戏玩法配置
    
    游戏核心玩法的配置参数
    """
    INITIAL_SUN: int = 50
    MAX_SUN: int = 9990
    MAX_LEVELS: int = 7
    ZOMBIE_WIN_X: float = 0.0  # 僵尸到达此X坐标游戏结束
    
    # 波次配置
    WAVES_PER_LEVEL: int = 5
    WAVE_DELAY: float = 5.0  # 波次间隔（秒）
    ZOMBIE_SPAWN_INTERVAL: float = 2.0  # 僵尸生成间隔（秒）


@dataclass(frozen=True)
class PlantConfig:
    """
    植物通用配置
    
    植物的通用属性配置
    """
    DEFAULT_WIDTH: float = 60.0
    DEFAULT_HEIGHT: float = 80.0
    DEFAULT_HEALTH: int = 100
    DEFAULT_ATTACK_COOLDOWN: float = 1.5
    DEFAULT_ATTACK_RANGE: float = 800.0
    
    # 射手类
    PROJECTILE_SPEED: float = 400.0
    PROJECTILE_DAMAGE: int = 20
    
    # 爆炸类
    EXPLOSION_RADIUS: float = 100.0
    EXPLOSION_DAMAGE: int = 1800
    
    # 阳光产生
    SUN_PRODUCTION_INTERVAL: float = 24.0
    SUN_AMOUNT: int = 25
    
    # 大嘴花
    CHOMPER_EAT_TIME: float = 0.5
    CHOMPER_CHEW_TIME: float = 42.0
    
    # 地刺
    SPIKEWEED_DAMAGE: int = 20
    SPIKEWEED_DAMAGE_INTERVAL: float = 0.5


@dataclass(frozen=True)
class ZombieConfig:
    """
    僵尸通用配置
    
    僵尸的通用属性配置
    """
    DEFAULT_WIDTH: float = 50.0
    DEFAULT_HEIGHT: float = 90.0
    DEFAULT_SPEED: float = 20.0
    DEFAULT_DAMAGE: int = 10
    DEFAULT_ATTACK_COOLDOWN: float = 1.0
    
    # 生成位置
    SPAWN_X: float = 850.0
    SPAWN_X_OFFSET: float = 100.0  # 随机偏移


@dataclass(frozen=True)
class ProjectileConfig:
    """
    投射物配置
    
    投射物的通用属性配置
    """
    DEFAULT_WIDTH: float = 20.0
    DEFAULT_HEIGHT: float = 20.0
    DEFAULT_SPEED: float = 400.0
    DEFAULT_DAMAGE: int = 20
    
    # 特殊效果
    SLOW_EFFECT: float = 0.5  # 减速比例
    SLOW_DURATION: float = 3.0  # 减速持续时间（秒）


@dataclass(frozen=True)
class SunConfig:
    """
    阳光配置
    
    阳光的生成和收集配置
    """
    AUTO_SPAWN_INTERVAL: float = 10.0  # 自动生成间隔（秒）
    FALL_SPEED: float = 50.0  # 下落速度
    SIZE: float = 40.0  # 阳光大小
    VALUE: int = 25  # 阳光价值
    LIFETIME: float = 8.0  # 停留时间（秒）
    COLOR: Tuple[int, int, int] = (255, 255, 0)  # 黄色


@dataclass(frozen=True)
class AudioConfig:
    """
    音频配置
    
    音效和音乐的配置
    """
    DEFAULT_MASTER_VOLUME: float = 1.0
    DEFAULT_SFX_VOLUME: float = 1.0
    DEFAULT_MUSIC_VOLUME: float = 0.5


@dataclass(frozen=True)
class SaveConfig:
    """
    存档配置
    
    游戏存档的配置
    """
    MAX_SLOTS: int = 5
    AUTO_SAVE_INTERVAL: float = 60.0  # 自动存档间隔（秒）
    VERSION: str = "1.0"


@dataclass(frozen=True)
class PerformanceConfig:
    """
    性能配置
    
    性能优化相关配置
    """
    SPATIAL_HASH_CELL_SIZE: float = 100.0
    MAX_ENTITIES_PER_CELL: int = 10
    MONITOR_HISTORY_SIZE: int = 60  # 性能监控历史记录大小


@dataclass(frozen=True)
class CombatConfig:
    """
    战斗配置
    
    战斗相关的数值配置
    """
    # 投射物
    PROJECTILE_SPAWN_OFFSET_X: float = 30.0
    PROJECTILE_HIT_DISTANCE: float = 30.0
    PROJECTILE_DESPAWN_X: float = 900.0
    
    # 僵尸攻击
    ZOMBIE_ATTACK_RANGE: float = 40.0
    ZOMBIE_WIN_X: float = 200.0
    ZOMBIE_WIN_SPAWN_X: float = 100.0
    
    # 撑杆跳
    POLE_VAULT_RANGE: float = 120.0
    POLE_VAULT_LANDING_OFFSET: float = 50.0
    POLE_VAULT_SPEED_BOOST: float = -30.0
    
    # 巨人僵尸
    GARGANTUAR_THROW_HEALTH_THRESHOLD: float = 0.5
    GARGANTUAR_SMASH_DAMAGE: int = 1000
    
    # 蹦极僵尸
    BUNGEE_STEAL_TIME: float = 3.0
    
    # 三线射手
    THREEPEATER_ROW_OFFSET: float = 100.0
    THREEPEATER_MIN_ROW: int = 0
    THREEPEATER_MAX_ROW: int = 4
    
    # 西瓜投手
    MELON_SPLASH_RADIUS: float = 50.0


@dataclass(frozen=True)
class DifficultyConfig:
    """
    难度配置
    
    不同难度等级影响阳光获取、僵尸强度等
    """
    # 难度等级名称
    name: str
    
    # 初始阳光
    initial_sun: int
    
    # 天空阳光生成间隔（秒）- 越小阳光越多
    auto_sun_spawn_interval: float
    
    # 每个阳光的价值
    sun_value: int
    
    # 向日葵产生阳光间隔（秒）- 越小产生越快
    sunflower_production_interval: float
    
    # 僵尸移动速度倍率
    zombie_speed_multiplier: float
    
    # 僵尸生命值倍率
    zombie_health_multiplier: float
    
    # 僵尸生成速度倍率
    zombie_spawn_rate_multiplier: float


# 定义三种难度
EASY = DifficultyConfig(
    name="简单",
    initial_sun=150,
    auto_sun_spawn_interval=5.0,      # 5秒一个天空阳光
    sun_value=50,                      # 每个阳光50
    sunflower_production_interval=12.0, # 向日葵12秒产生一次
    zombie_speed_multiplier=0.8,
    zombie_health_multiplier=0.8,
    zombie_spawn_rate_multiplier=0.7
)

NORMAL = DifficultyConfig(
    name="普通",
    initial_sun=100,
    auto_sun_spawn_interval=8.0,
    sun_value=25,
    sunflower_production_interval=24.0,
    zombie_speed_multiplier=1.0,
    zombie_health_multiplier=1.0,
    zombie_spawn_rate_multiplier=1.0
)

HARD = DifficultyConfig(
    name="困难",
    initial_sun=50,
    auto_sun_spawn_interval=12.0,
    sun_value=25,
    sunflower_production_interval=30.0,
    zombie_speed_multiplier=1.3,
    zombie_health_multiplier=1.5,
    zombie_spawn_rate_multiplier=1.3
)


# 导出所有配置实例
GRID = GridConfig()
SCREEN = ScreenConfig()
GAME = GameConfig()
PLANT = PlantConfig()
ZOMBIE = ZombieConfig()
PROJECTILE = ProjectileConfig()
SUN = SunConfig()
AUDIO = AudioConfig()
SAVE = SaveConfig()
PERFORMANCE = PerformanceConfig()
COMBAT = CombatConfig()
DIFFICULTY = NORMAL  # 默认普通难度
