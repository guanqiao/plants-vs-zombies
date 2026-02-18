"""
僵尸生成器 - 管理僵尸的生成和波次控制
"""

import random
from typing import Optional, List, Tuple
from ..ecs import World
from ..ecs.components import ZombieType
from .entity_factory import EntityFactory


class ZombieSpawner:
    """
    僵尸生成器
    
    管理僵尸的生成时机和位置
    """
    
    # 屏幕配置
    SCREEN_WIDTH = 900
    GRID_START_Y = 50
    CELL_HEIGHT = 100
    
    # 僵尸起始X坐标（屏幕右侧外）
    SPAWN_X = 850
    
    def __init__(self, world: World, entity_factory: EntityFactory):
        self.world = world
        self.entity_factory = entity_factory
        
        # 波次配置
        self.current_level = 1
        self.wave_index = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0  # 僵尸生成间隔（秒）
        
        # 当前波次待生成的僵尸队列
        self.zombie_queue: List[Tuple[ZombieType, int]] = []
        
        # 波次配置
        self.wave_configs = self._init_wave_configs()
    
    def _init_wave_configs(self) -> dict:
        """初始化波次配置"""
        return {
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
    
    def set_level(self, level: int) -> None:
        """设置当前关卡"""
        self.current_level = level
        self.wave_index = 0
        self.wave_timer = 0.0
        self.zombie_queue.clear()
    
    def update(self, dt: float) -> Optional[List]:
        """
        更新生成器
        
        Returns:
            新生成的僵尸实体列表，如果没有则返回None
        """
        spawned_zombies = []
        
        # 更新波次计时器
        self.wave_timer += dt
        self.spawn_timer += dt
        
        # 检查是否需要开始新波次
        self._check_wave_start()
        
        # 检查是否需要生成僵尸
        if self.spawn_timer >= self.spawn_interval and self.zombie_queue:
            self.spawn_timer = 0.0
            zombie = self._spawn_next_zombie()
            if zombie:
                spawned_zombies.append(zombie)
        
        return spawned_zombies if spawned_zombies else None
    
    def _check_wave_start(self) -> None:
        """检查是否应该开始新波次"""
        config = self.wave_configs.get(self.current_level)
        if not config:
            return
        
        waves = config['waves']
        if self.wave_index >= len(waves):
            return
        
        current_wave = waves[self.wave_index]
        if self.wave_timer >= current_wave['delay']:
            # 开始新波次，填充僵尸队列
            self.zombie_queue = current_wave['zombies'].copy()
            self.wave_index += 1
    
    def _spawn_next_zombie(self) -> Optional:
        """生成队列中的下一个僵尸"""
        if not self.zombie_queue:
            return None
        
        # 获取下一个僵尸类型
        zombie_type, count = self.zombie_queue[0]
        
        # 减少计数
        if count <= 1:
            self.zombie_queue.pop(0)
        else:
            self.zombie_queue[0] = (zombie_type, count - 1)
        
        # 随机选择行（0-4）
        row = random.randint(0, 4)
        
        # 计算Y坐标
        y = self.GRID_START_Y + row * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
        
        # 创建僵尸
        return self.entity_factory.create_zombie(
            zombie_type,
            self.SPAWN_X,
            y,
            row
        )
    
    def is_wave_complete(self) -> bool:
        """检查当前波次是否完成"""
        config = self.wave_configs.get(self.current_level)
        if not config:
            return True
        
        # 所有波次都已开始且队列为空
        return (self.wave_index >= len(config['waves']) and 
                not self.zombie_queue)
    
    def is_level_complete(self) -> bool:
        """检查关卡是否完成（所有波次完成且无僵尸）"""
        if not self.is_wave_complete():
            return False
        
        # 检查是否还有僵尸存活
        from ..ecs.components import ZombieComponent
        zombies = self.world.query_entities(ZombieComponent)
        return len(zombies) == 0
    
    def get_wave_info(self) -> str:
        """获取波次信息"""
        config = self.wave_configs.get(self.current_level)
        if not config:
            return "无波次配置"
        
        total_waves = len(config['waves'])
        
        if self.wave_index >= total_waves:
            return "最后一波！"
        
        return f"波次: {self.wave_index + 1}/{total_waves}"
    
    def get_zombies_remaining(self) -> int:
        """获取剩余僵尸数量"""
        count = 0
        for _, num in self.zombie_queue:
            count += num
        return count
    
    def reset(self) -> None:
        """重置生成器"""
        self.wave_index = 0
        self.wave_timer = 0.0
        self.spawn_timer = 0.0
        self.zombie_queue.clear()