import tomllib
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器 - 加载和管理游戏配置"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config_dir = Path(__file__).parent.parent.parent / 'config'
        self._plants_config: Dict[str, Any] = {}
        self._zombies_config: Dict[str, Any] = {}
        self._levels_config: Dict[str, Any] = {}
        self._game_config: Dict[str, Any] = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        self._load_game_config()
        self._load_plants_config()
        self._load_zombies_config()
        self._load_levels_config()
    
    def _load_game_config(self):
        """加载游戏配置"""
        config_path = self._config_dir / 'game_config.toml'
        if config_path.exists():
            with open(config_path, 'rb') as f:
                data = tomllib.load(f)
                self._game_config = data.get('game', {})
                self._plants_config = data.get('plants', {})
    
    def _load_plants_config(self):
        """加载植物配置（已在game_config中）"""
        pass
    
    def _load_zombies_config(self):
        """加载僵尸配置"""
        config_path = self._config_dir / 'zombies_config.toml'
        if config_path.exists():
            with open(config_path, 'rb') as f:
                data = tomllib.load(f)
                self._zombies_config = data.get('zombies', {})
    
    def _load_levels_config(self):
        """加载关卡配置"""
        config_path = self._config_dir / 'levels_config.toml'
        if config_path.exists():
            with open(config_path, 'rb') as f:
                data = tomllib.load(f)
                self._levels_config = data.get('levels', {})
    
    def get_plant_config(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """获取植物配置"""
        return self._plants_config.get(plant_name)
    
    def get_zombie_config(self, zombie_name: str) -> Optional[Dict[str, Any]]:
        """获取僵尸配置"""
        return self._zombies_config.get(zombie_name)
    
    def get_all_plants(self) -> Dict[str, Any]:
        """获取所有植物配置"""
        return self._plants_config.copy()
    
    def get_all_zombies(self) -> Dict[str, Any]:
        """获取所有僵尸配置"""
        return self._zombies_config.copy()
    
    def get_game_config(self) -> Dict[str, Any]:
        """获取游戏配置"""
        return self._game_config.copy()
    
    def get_level_config(self, level: int) -> Optional[Dict[str, Any]]:
        """获取关卡配置"""
        return self._levels_config.get(str(level))
    
    def get_all_levels(self) -> Dict[str, Any]:
        """获取所有关卡配置"""
        return self._levels_config.copy()
    
    def reload(self):
        """重新加载配置"""
        self._plants_config.clear()
        self._zombies_config.clear()
        self._levels_config.clear()
        self._game_config.clear()
        self._load_configs()
    
    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
