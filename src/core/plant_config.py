"""
植物配置管理器

统一从TOML配置文件加载植物配置，替代硬编码配置字典
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import os
import sys

# 添加项目根目录到路径
if sys.path[0] not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ecs.components import PlantType


@dataclass(frozen=True)
class PlantConfig:
    """
    植物配置数据类
    
    存储单个植物的所有配置属性
    
    Attributes:
        name: 植物名称
        cost: 阳光成本
        health: 生命值
        width: 宽度（像素）
        height: 高度（像素）
        color: 颜色 (R, G, B)
        attack_cooldown: 攻击冷却时间（秒）
        attack_damage: 攻击力
        attack_range: 攻击范围（像素）
        fire_rate: 射击间隔（秒，射手类植物）
        projectile_damage: 投射物伤害
        projectile_speed: 投射物速度
        sun_production_interval: 产生阳光间隔（秒，向日葵类）
        sun_amount: 产生的阳光数量
        explosion_radius: 爆炸半径（樱桃炸弹等）
        explosion_damage: 爆炸伤害
        arm_time: 激活时间（土豆雷）
        slow_effect: 减速效果（0-1）
        slow_duration: 减速持续时间
        splash_radius: 溅射半径
        splash_damage: 溅射伤害
        is_shooter: 是否是射手类植物
        is_explosive: 是否是爆炸类植物
        is_sun_producer: 是否产生阳光
    """
    name: str = ""
    cost: int = 100
    health: int = 100
    width: float = 60.0
    height: float = 80.0
    color: Tuple[int, int, int] = (0, 200, 0)
    attack_cooldown: float = 1.5
    attack_damage: int = 20
    attack_range: float = 800.0
    fire_rate: float = 1.5
    projectile_damage: int = 20
    projectile_speed: float = 400.0
    sun_production_interval: float = 24.0
    sun_amount: int = 25
    explosion_radius: float = 0.0
    explosion_damage: int = 0
    arm_time: float = 0.0
    slow_effect: float = 0.0
    slow_duration: float = 0.0
    splash_radius: float = 0.0
    splash_damage: int = 0
    shots_per_fire: int = 1
    rows: int = 1
    is_shooter: bool = False
    is_explosive: bool = False
    is_sun_producer: bool = False
    is_instant_kill: bool = False


class PlantConfigManager:
    """
    植物配置管理器
    
    单例模式，统一管理所有植物配置
    从TOML配置文件加载，提供类型安全的配置访问
    """
    
    _instance: Optional['PlantConfigManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'PlantConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if PlantConfigManager._initialized:
            return
            
        self._configs: Dict[PlantType, PlantConfig] = {}
        self._load_configs()
        PlantConfigManager._initialized = True
    
    def _load_configs(self) -> None:
        """从TOML配置文件加载植物配置"""
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib
        
        # 获取配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'game_config.toml'
        )
        
        try:
            with open(config_path, 'rb') as f:
                data = tomllib.load(f)
            
            plants_data = data.get('plants', {})
            
            # 映射TOML配置到PlantType
            type_mapping = {
                'sunflower': PlantType.SUNFLOWER,
                'peashooter': PlantType.PEASHOOTER,
                'wallnut': PlantType.WALLNUT,
                'snow_pea': PlantType.SNOW_PEA,
                'cherry_bomb': PlantType.CHERRY_BOMB,
                'potato_mine': PlantType.POTATO_MINE,
                'repeater': PlantType.REPEATER,
                'chomper': PlantType.CHOMPER,
                'threepeater': PlantType.THREEPEATER,
                'melon_pult': PlantType.MELON_PULT,
                'winter_melon': PlantType.WINTER_MELON,
                'tall_nut': PlantType.TALL_NUT,
                'spikeweed': PlantType.SPIKEWEED,
                'magnet_shroom': PlantType.MAGNET_SHROOM,
                'pumpkin': PlantType.PUMPKIN,
            }
            
            for key, plant_type in type_mapping.items():
                if key in plants_data:
                    self._configs[plant_type] = self._parse_config(plants_data[key])
                else:
                    # 使用默认配置
                    self._configs[plant_type] = PlantConfig()
                    
        except FileNotFoundError:
            print(f"警告: 配置文件未找到: {config_path}")
            self._load_default_configs()
        except Exception as e:
            print(f"警告: 加载配置失败: {e}")
            self._load_default_configs()
    
    def _parse_config(self, data: Dict[str, Any]) -> PlantConfig:
        """解析配置数据为PlantConfig对象"""
        # 转换颜色列表为元组
        color = tuple(data.get('color', [0, 200, 0]))
        if len(color) != 3:
            color = (0, 200, 0)
        
        # 判断植物类型
        is_shooter = 'fire_rate' in data
        is_explosive = 'explosion_damage' in data and data['explosion_damage'] > 0
        is_sun_producer = 'sun_production_interval' in data
        
        return PlantConfig(
            name=data.get('name', ''),
            cost=data.get('cost', 100),
            health=data.get('health', 100),
            width=data.get('width', 60.0),
            height=data.get('height', 80.0),
            color=color,
            attack_cooldown=data.get('fire_rate', 1.5),
            attack_damage=data.get('projectile_damage', 20),
            fire_rate=data.get('fire_rate', 1.5),
            projectile_damage=data.get('projectile_damage', 20),
            projectile_speed=data.get('projectile_speed', 400.0),
            sun_production_interval=data.get('sun_production_interval', 24.0),
            sun_amount=data.get('sun_amount', 25),
            explosion_radius=data.get('explosion_radius', 0.0),
            explosion_damage=data.get('explosion_damage', 0),
            arm_time=data.get('arm_time', 0.0),
            slow_effect=data.get('slow_effect', 0.0),
            slow_duration=data.get('slow_duration', 0.0),
            splash_radius=data.get('splash_radius', 0.0),
            splash_damage=data.get('splash_damage', 0),
            shots_per_fire=data.get('shots_per_fire', 1),
            rows=data.get('rows', 1),
            is_shooter=is_shooter,
            is_explosive=is_explosive,
            is_sun_producer=is_sun_producer,
            is_instant_kill=data.get('instant_kill', False),
        )
    
    def _load_default_configs(self) -> None:
        """加载默认配置"""
        for plant_type in PlantType:
            self._configs[plant_type] = PlantConfig()
    
    def get_config(self, plant_type: PlantType) -> PlantConfig:
        """
        获取指定植物类型的配置
        
        Args:
            plant_type: 植物类型
            
        Returns:
            植物配置对象
        """
        return self._configs.get(plant_type, PlantConfig())
    
    def get_all_configs(self) -> Dict[PlantType, PlantConfig]:
        """
        获取所有植物配置
        
        Returns:
            植物类型到配置的映射字典
        """
        return self._configs.copy()
    
    def get_cost(self, plant_type: PlantType) -> int:
        """获取植物阳光成本"""
        return self._configs.get(plant_type, PlantConfig()).cost
    
    def get_health(self, plant_type: PlantType) -> int:
        """获取植物生命值"""
        return self._configs.get(plant_type, PlantConfig()).health
    
    def get_size(self, plant_type: PlantType) -> Tuple[float, float]:
        """获取植物尺寸 (width, height)"""
        config = self._configs.get(plant_type, PlantConfig())
        return (config.width, config.height)
    
    def get_color(self, plant_type: PlantType) -> Tuple[int, int, int]:
        """获取植物颜色"""
        return self._configs.get(plant_type, PlantConfig()).color
    
    def is_shooter(self, plant_type: PlantType) -> bool:
        """检查是否是射手类植物"""
        return self._configs.get(plant_type, PlantConfig()).is_shooter
    
    def is_explosive(self, plant_type: PlantType) -> bool:
        """检查是否是爆炸类植物"""
        return self._configs.get(plant_type, PlantConfig()).is_explosive
    
    def is_sun_producer(self, plant_type: PlantType) -> bool:
        """检查是否产生阳光"""
        return self._configs.get(plant_type, PlantConfig()).is_sun_producer
    
    def reload_configs(self) -> None:
        """重新加载配置（热更新）"""
        self._configs.clear()
        self._load_configs()


# 全局配置管理器实例
_plant_config_manager: Optional[PlantConfigManager] = None


def get_plant_config_manager() -> PlantConfigManager:
    """获取全局植物配置管理器实例"""
    global _plant_config_manager
    if _plant_config_manager is None:
        _plant_config_manager = PlantConfigManager()
    return _plant_config_manager


def get_plant_config(plant_type: PlantType) -> PlantConfig:
    """便捷函数：获取指定植物的配置"""
    return get_plant_config_manager().get_config(plant_type)
