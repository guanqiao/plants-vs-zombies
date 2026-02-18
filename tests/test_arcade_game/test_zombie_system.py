"""
测试僵尸系统
"""

import pytest
from src.ecs import World
from src.arcade_game.entity_factory import EntityFactory
from src.arcade_game.zombie_spawner import ZombieSpawner
from src.ecs.systems import ZombieBehaviorSystem
from src.ecs.components import (
    ZombieType, PlantType,
    TransformComponent, ZombieComponent, PlantComponent,
    HealthComponent, GridPositionComponent, VelocityComponent
)


class TestZombieSpawner:
    """测试僵尸生成器"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.spawner = ZombieSpawner(self.world, self.entity_factory)
    
    def test_init_wave_configs(self):
        """测试波次配置初始化"""
        assert len(self.spawner.wave_configs) == 7  # 7个关卡
        assert 1 in self.spawner.wave_configs
        assert 7 in self.spawner.wave_configs
    
    def test_set_level(self):
        """测试设置关卡"""
        self.spawner.set_level(2)
        assert self.spawner.current_level == 2
        assert self.spawner.wave_index == 0
        assert self.spawner.wave_timer == 0.0
    
    def test_wave_start(self):
        """测试波次开始"""
        self.spawner.set_level(1)
        
        # 初始状态：没有僵尸队列
        assert len(self.spawner.zombie_queue) == 0
        
        # 直接设置波次计时器超过延迟时间
        self.spawner.wave_timer = 6.0
        self.spawner._check_wave_start()
        
        # 检查僵尸队列被填充
        assert len(self.spawner.zombie_queue) > 0
    
    def test_zombie_spawn(self):
        """测试僵尸生成"""
        self.spawner.set_level(1)
        
        # 直接填充僵尸队列
        self.spawner.zombie_queue = [(ZombieType.NORMAL, 3)]
        
        # 更新生成僵尸（超过生成间隔）
        spawned = self.spawner.update(3.0)
        
        # 检查生成了僵尸
        assert spawned is not None
        assert len(spawned) > 0
        
        # 检查僵尸组件
        zombie_comp = self.world.get_component(spawned[0], ZombieComponent)
        assert zombie_comp is not None
    
    def test_is_wave_complete(self):
        """测试波次完成检查"""
        self.spawner.set_level(1)
        
        # 初始状态：未完成
        assert not self.spawner.is_wave_complete()
        
        # 模拟完成所有波次
        self.spawner.wave_index = 10  # 超过波次数量
        self.spawner.zombie_queue.clear()
        
        assert self.spawner.is_wave_complete()
    
    def test_get_wave_info(self):
        """测试获取波次信息"""
        self.spawner.set_level(1)
        
        info = self.spawner.get_wave_info()
        assert "波次" in info
        
        # 完成所有波次
        self.spawner.wave_index = 10
        info = self.spawner.get_wave_info()
        assert "最后一波" in info
    
    def test_get_zombies_remaining(self):
        """测试获取剩余僵尸数量"""
        self.spawner.set_level(1)
        self.spawner.zombie_queue = [(ZombieType.NORMAL, 3), (ZombieType.CONEHEAD, 2)]
        
        assert self.spawner.get_zombies_remaining() == 5
    
    def test_reset(self):
        """测试重置"""
        self.spawner.set_level(2)
        self.spawner.wave_index = 3
        self.spawner.wave_timer = 100.0
        self.spawner.zombie_queue = [(ZombieType.NORMAL, 1)]
        
        self.spawner.reset()
        
        assert self.spawner.wave_index == 0
        assert self.spawner.wave_timer == 0.0
        assert len(self.spawner.zombie_queue) == 0


class TestZombieBehaviorSystem:
    """测试僵尸行为系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.behavior_system = ZombieBehaviorSystem(priority=45)
        self.death_callbacks = []
        self.behavior_system.register_death_callback(self._on_death)
    
    def _on_death(self, zombie_id, score):
        """死亡回调"""
        self.death_callbacks.append((zombie_id, score))
    
    def test_zombie_moves_left(self):
        """测试僵尸向左移动"""
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=500, y=150, row=1
        )
        
        transform = self.world.get_component(zombie, TransformComponent)
        velocity = self.world.get_component(zombie, VelocityComponent)
        initial_x = transform.x
        
        # 更新行为系统
        self.behavior_system.update(0.1, self.world._component_manager)
        
        # 检查速度设置（向左）
        assert velocity.vx < 0
    
    def test_zombie_attacks_plant(self):
        """测试僵尸攻击植物"""
        # 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=400, y=150, row=1, col=2
        )
        plant_health = self.world.get_component(plant, HealthComponent)
        initial_health = plant_health.current
        
        # 创建僵尸（在植物右侧，攻击范围内）
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=430, y=150, row=1
        )
        
        # 更新行为系统
        self.behavior_system.update(0.1, self.world._component_manager)
        
        # 检查植物受到伤害
        plant_health = self.world.get_component(plant, HealthComponent)
        assert plant_health.current < initial_health
    
    def test_zombie_stops_when_attacking(self):
        """测试僵尸攻击时停止移动"""
        # 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=400, y=150, row=1, col=2
        )
        
        # 创建僵尸（在植物右侧，攻击范围内）
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=430, y=150, row=1
        )
        
        velocity = self.world.get_component(zombie, VelocityComponent)
        
        # 更新行为系统
        self.behavior_system.update(0.1, self.world._component_manager)
        
        # 检查僵尸停止移动
        assert velocity.vx == 0
    
    def test_zombie_death_callback(self):
        """测试僵尸死亡回调"""
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=400, y=150, row=1
        )
        
        # 杀死僵尸
        health = self.world.get_component(zombie, HealthComponent)
        health.take_damage(1000)  # 造成致命伤害
        
        # 更新行为系统
        self.behavior_system.update(0.1, self.world._component_manager)
        
        # 检查死亡回调被触发
        assert len(self.death_callbacks) == 1
        assert self.death_callbacks[0][0] == zombie.id
        assert self.death_callbacks[0][1] > 0  # 分数
    
    def test_zombie_attack_cooldown(self):
        """测试僵尸攻击冷却"""
        # 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=400, y=150, row=1, col=2
        )
        plant_health = self.world.get_component(plant, HealthComponent)
        
        # 创建僵尸
        zombie = self.entity_factory.create_zombie(
            ZombieType.NORMAL, x=430, y=150, row=1
        )
        zombie_comp = self.world.get_component(zombie, ZombieComponent)
        
        # 第一次攻击
        self.behavior_system.update(0.1, self.world._component_manager)
        health_after_first = plant_health.current
        
        # 立即再次更新（冷却中，不应该攻击）
        self.behavior_system.update(0.1, self.world._component_manager)
        health_after_second = plant_health.current
        
        # 检查冷却期间没有额外伤害
        assert health_after_first == health_after_second


class TestZombieSystemIntegration:
    """测试僵尸系统集成"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.spawner = ZombieSpawner(self.world, self.entity_factory)
        self.behavior_system = ZombieBehaviorSystem(priority=45)
    
    def test_full_zombie_workflow(self):
        """测试完整僵尸流程"""
        # 1. 设置关卡
        self.spawner.set_level(1)
        
        # 2. 直接填充僵尸队列并生成
        self.spawner.zombie_queue = [(ZombieType.NORMAL, 1)]
        spawned = self.spawner.update(3.0)
        assert spawned is not None
        zombie = spawned[0]
        
        # 3. 获取僵尸所在行
        zombie_grid = self.world.get_component(zombie, GridPositionComponent)
        zombie_row = zombie_grid.row
        
        # 4. 在相同行创建植物
        y = 50 + zombie_row * 100 + 50  # 根据行计算Y坐标
        plant = self.entity_factory.create_plant(
            PlantType.PEASHOOTER, x=400, y=y, row=zombie_row, col=2
        )
        
        # 5. 移动僵尸到植物位置
        transform = self.world.get_component(zombie, TransformComponent)
        transform.x = 430
        
        # 6. 僵尸攻击植物
        plant_health = self.world.get_component(plant, HealthComponent)
        initial_health = plant_health.current
        
        # 更新多次，确保僵尸攻击
        for _ in range(5):
            self.behavior_system.update(0.5, self.world._component_manager)
        
        # 7. 检查植物受伤
        plant_health = self.world.get_component(plant, HealthComponent)
        assert plant_health.current < initial_health
    
    def test_multiple_zombies_attack(self):
        """测试多个僵尸攻击"""
        # 创建植物
        plant = self.entity_factory.create_plant(
            PlantType.WALLNUT, x=400, y=150, row=1, col=2
        )
        
        # 创建多个僵尸
        zombies = []
        for i in range(3):
            zombie = self.entity_factory.create_zombie(
                ZombieType.NORMAL, x=430 + i * 5, y=150, row=1
            )
            zombies.append(zombie)
        
        # 更新行为系统
        for _ in range(5):
            self.behavior_system.update(0.5, self.world._component_manager)
        
        # 检查植物受到多次伤害
        plant_health = self.world.get_component(plant, HealthComponent)
        assert plant_health.current < plant_health.max_health
