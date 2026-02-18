import random
from typing import List, Dict, TYPE_CHECKING
from src.entities.zombie import Zombie, ZombieType

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class WaveSystem:
    """僵尸波次系统"""
    
    LEVEL_CONFIGS = {
        1: {
            'total_waves': 3,
            'zombies_per_wave': [5, 8, 10],
            'spawn_interval': 8.0,
            'wave_interval': 30.0,
            'zombie_types': [ZombieType.NORMAL],
        },
        2: {
            'total_waves': 3,
            'zombies_per_wave': [8, 12, 15],
            'spawn_interval': 6.0,
            'wave_interval': 25.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD],
        },
        3: {
            'total_waves': 4,
            'zombies_per_wave': [10, 15, 18, 20],
            'spawn_interval': 5.0,
            'wave_interval': 25.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD, ZombieType.POLE_VAULTER],
        },
        4: {
            'total_waves': 4,
            'zombies_per_wave': [12, 18, 22, 25],
            'spawn_interval': 4.0,
            'wave_interval': 20.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD, ZombieType.RUNNER, 
                           ZombieType.SCREEN_DOOR, ZombieType.FOOTBALL],
        },
        5: {
            'total_waves': 5,
            'zombies_per_wave': [15, 20, 25, 30, 35],
            'spawn_interval': 3.5,
            'wave_interval': 20.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD, ZombieType.RUNNER, 
                           ZombieType.GARGANTUAR, ZombieType.DANCER, ZombieType.BALLOON, ZombieType.POGO],
        },
        6: {
            'total_waves': 5,
            'zombies_per_wave': [18, 25, 30, 35, 40],
            'spawn_interval': 3.0,
            'wave_interval': 18.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD, ZombieType.RUNNER, 
                           ZombieType.GARGANTUAR, ZombieType.POLE_VAULTER, ZombieType.FOOTBALL, ZombieType.DANCER,
                           ZombieType.BALLOON, ZombieType.MINER, ZombieType.POGO],
        },
        7: {
            'total_waves': 6,
            'zombies_per_wave': [20, 28, 35, 40, 45, 50],
            'spawn_interval': 2.5,
            'wave_interval': 15.0,
            'zombie_types': [ZombieType.NORMAL, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD, ZombieType.RUNNER, 
                           ZombieType.GARGANTUAR, ZombieType.POLE_VAULTER, ZombieType.SCREEN_DOOR, ZombieType.FOOTBALL,
                           ZombieType.DANCER, ZombieType.BALLOON, ZombieType.MINER, ZombieType.POGO, ZombieType.BUNGEE],
        },
    }
    
    def __init__(self, level: int = 1):
        self.level = level
        self.config = self.LEVEL_CONFIGS.get(level, self.LEVEL_CONFIGS[1])
        
        self.current_wave = 0
        self.zombies_spawned = 0
        self.zombies_in_wave = 0
        
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self.wave_started = False
        self.all_waves_complete = False
        
        self._start_wave()
    
    def _start_wave(self):
        """开始新波次"""
        if self.current_wave >= self.config['total_waves']:
            self.all_waves_complete = True
            return
        
        self.zombies_spawned = 0
        self.zombies_in_wave = self.config['zombies_per_wave'][self.current_wave]
        self.wave_started = True
        self.current_wave += 1
    
    def _spawn_zombie(self, game_manager: 'GameManager'):
        """生成僵尸"""
        zombie_types = self.config['zombie_types']
        
        if self.current_wave == self.config['total_waves'] and self.zombies_spawned == self.zombies_in_wave - 1:
            if ZombieType.GARGANTUAR in zombie_types:
                zombie_type = ZombieType.GARGANTUAR
            else:
                zombie_type = random.choice(zombie_types)
        else:
            zombie_type = random.choice(zombie_types)
        
        row = random.randint(0, 4)
        x = 900
        y = 100 + row * 100 + 50
        
        zombie = Zombie(zombie_type, x, y)
        zombie.row = row
        
        game_manager.add_zombie(zombie)
        self.zombies_spawned += 1
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新波次系统"""
        if self.all_waves_complete:
            return
        
        if not self.wave_started:
            self.wave_timer += dt
            if self.wave_timer >= self.config['wave_interval']:
                self.wave_timer = 0.0
                self._start_wave()
            return
        
        if self.zombies_spawned < self.zombies_in_wave:
            self.spawn_timer += dt
            if self.spawn_timer >= self.config['spawn_interval']:
                self._spawn_zombie(game_manager)
                self.spawn_timer = 0.0
        
        if self.zombies_spawned >= self.zombies_in_wave and len(game_manager.zombies) == 0:
            self.wave_started = False
    
    def is_complete(self) -> bool:
        """是否完成所有波次"""
        return self.all_waves_complete
    
    def get_wave_info(self) -> Dict:
        """获取当前波次信息"""
        return {
            'current_wave': self.current_wave,
            'total_waves': self.config['total_waves'],
            'zombies_remaining': self.zombies_in_wave - self.zombies_spawned,
        }
