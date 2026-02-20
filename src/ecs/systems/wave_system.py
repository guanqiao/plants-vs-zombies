"""
波次系统 - 管理僵尸波次的生成
"""

from ..system import System
from ..component import ComponentManager
from ..components import ZombieType


class WaveSystem(System):
    """
    波次系统
    
    管理僵尸波次的生成逻辑
    - 波次配置
    - 生成计时
    - 波次进度
    """
    
    # 关卡配置
    LEVEL_CONFIGS = {
        1: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 1)]},
                {'delay': 15.0, 'zombies': [(ZombieType.NORMAL, 2)]},
                {'delay': 25.0, 'zombies': [(ZombieType.NORMAL, 3)]},
                {'delay': 35.0, 'zombies': [(ZombieType.CONEHEAD, 1)]},
                {'delay': 45.0, 'zombies': [(ZombieType.NORMAL, 2), (ZombieType.CONEHEAD, 1)]},
            ]
        },
        2: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 2)]},
                {'delay': 12.0, 'zombies': [(ZombieType.CONEHEAD, 1)]},
                {'delay': 20.0, 'zombies': [(ZombieType.NORMAL, 3), (ZombieType.CONEHEAD, 1)]},
                {'delay': 30.0, 'zombies': [(ZombieType.BUCKETHEAD, 1)]},
                {'delay': 40.0, 'zombies': [(ZombieType.NORMAL, 2), (ZombieType.BUCKETHEAD, 1)]},
            ]
        },
        3: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 2), (ZombieType.CONEHEAD, 1)]},
                {'delay': 15.0, 'zombies': [(ZombieType.BUCKETHEAD, 1)]},
                {'delay': 25.0, 'zombies': [(ZombieType.NORMAL, 3), (ZombieType.CONEHEAD, 2)]},
                {'delay': 35.0, 'zombies': [(ZombieType.RUNNER, 2)]},
                {'delay': 45.0, 'zombies': [(ZombieType.NORMAL, 3), (ZombieType.BUCKETHEAD, 2)]},
            ]
        },
        4: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 3)]},
                {'delay': 12.0, 'zombies': [(ZombieType.CONEHEAD, 2)]},
                {'delay': 20.0, 'zombies': [(ZombieType.BUCKETHEAD, 2)]},
                {'delay': 30.0, 'zombies': [(ZombieType.POLE_VAULTER, 2)]},
                {'delay': 40.0, 'zombies': [(ZombieType.NORMAL, 4), (ZombieType.POLE_VAULTER, 2)]},
            ]
        },
        5: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 3), (ZombieType.CONEHEAD, 2)]},
                {'delay': 15.0, 'zombies': [(ZombieType.FOOTBALL, 1)]},
                {'delay': 25.0, 'zombies': [(ZombieType.BUCKETHEAD, 3)]},
                {'delay': 35.0, 'zombies': [(ZombieType.DANCER, 1)]},
                {'delay': 45.0, 'zombies': [(ZombieType.NORMAL, 5), (ZombieType.FOOTBALL, 2)]},
            ]
        },
        6: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 4), (ZombieType.CONEHEAD, 2)]},
                {'delay': 15.0, 'zombies': [(ZombieType.BALLOON, 2)]},
                {'delay': 25.0, 'zombies': [(ZombieType.MINER, 2)]},
                {'delay': 35.0, 'zombies': [(ZombieType.POGO, 2)]},
                {'delay': 45.0, 'zombies': [(ZombieType.NORMAL, 5), (ZombieType.BALLOON, 3)]},
            ]
        },
        7: {
            'waves': [
                {'delay': 5.0, 'zombies': [(ZombieType.NORMAL, 5), (ZombieType.CONEHEAD, 3)]},
                {'delay': 15.0, 'zombies': [(ZombieType.GARGANTUAR, 1)]},
                {'delay': 25.0, 'zombies': [(ZombieType.BUCKETHEAD, 4), (ZombieType.FOOTBALL, 2)]},
                {'delay': 35.0, 'zombies': [(ZombieType.DANCER, 2), (ZombieType.BALLOON, 3)]},
                {'delay': 45.0, 'zombies': [(ZombieType.GARGANTUAR, 2), (ZombieType.NORMAL, 5)]},
            ]
        },
    }
    
    def __init__(self, level: int = 1, priority: int = 50):
        super().__init__(priority)
        self.level = level
        self.wave_index = 0
        self.timer = 0.0
        self.waves = self.LEVEL_CONFIGS.get(level, {}).get('waves', [])
        self.complete = len(self.waves) == 0
        self.zombies_to_spawn = []
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新波次系统"""
        if self.complete or self.wave_index >= len(self.waves):
            self.complete = True
            return
        
        self.timer += dt
        
        # 检查当前波次是否应该开始
        current_wave = self.waves[self.wave_index]
        if self.timer >= current_wave['delay']:
            # 准备生成僵尸
            self.zombies_to_spawn = current_wave['zombies'].copy()
            self.wave_index += 1
    
    def get_next_zombie(self) -> tuple:
        """
        获取下一个要生成的僵尸
        
        Returns:
            (ZombieType, row) 或 None
        """
        if not self.zombies_to_spawn:
            return None
        
        zombie_type, count = self.zombies_to_spawn[0]
        
        if count <= 1:
            self.zombies_to_spawn.pop(0)
        else:
            self.zombies_to_spawn[0] = (zombie_type, count - 1)
        
        # 随机选择行（0-4）
        import random
        row = random.randint(0, 4)
        
        return (zombie_type, row)
    
    def has_zombies_to_spawn(self) -> bool:
        """检查是否还有待生成的僵尸"""
        return len(self.zombies_to_spawn) > 0
    
    def is_complete(self) -> bool:
        """检查是否完成所有波次"""
        return self.complete and not self.has_zombies_to_spawn()
    
    def get_wave_info(self) -> str:
        """获取波次信息"""
        if self.complete:
            return "最后一波！"
        return f"波次: {self.wave_index + 1}/{len(self.waves)}"