"""
僵尸行为系统 - 处理僵尸的移动和攻击
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, VelocityComponent, ZombieComponent,
    GridPositionComponent, HealthComponent, PlantComponent
)


class ZombieBehaviorSystem(System):
    """
    僵尸行为系统
    
    处理僵尸的移动、攻击和特殊行为
    - 正常移动
    - 攻击植物
    - 特殊僵尸能力（跳跃、飞行等）
    """
    
    # 攻击距离阈值
    ATTACK_RANGE = 40.0
    
    def __init__(self, priority: int = 45):
        super().__init__(priority)
        self.on_zombie_death_callbacks = []
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新僵尸行为"""
        # 获取所有僵尸实体
        entities = component_manager.query(
            TransformComponent, VelocityComponent, ZombieComponent
        )
        
        zombies_to_remove = []
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            velocity = component_manager.get_component(entity_id, VelocityComponent)
            zombie = component_manager.get_component(entity_id, ZombieComponent)
            
            if not all([transform, velocity, zombie]):
                continue
            
            # 检查僵尸是否死亡
            health = component_manager.get_component(entity_id, HealthComponent)
            if health and health.is_dead:
                zombies_to_remove.append(entity_id)
                continue
            
            # 更新计时器
            zombie.update_timer(dt)
            
            # 检查是否可以攻击植物
            target_plant = self._find_target_plant(entity_id, transform, component_manager)
            
            if target_plant:
                # 停止移动并攻击
                velocity.vx = 0
                self._attack_plant(target_plant, zombie, component_manager, dt)
            else:
                # 继续移动
                velocity.vx = -1.0  # 向左移动
                velocity.apply_multiplier(zombie.slow_factor)
            
            # 处理特殊行为
            self._handle_special_behavior(entity_id, transform, zombie, component_manager, dt)
        
        # 处理死亡的僵尸
        for zombie_id in zombies_to_remove:
            self._handle_zombie_death(zombie_id, component_manager)
    
    def _find_target_plant(self, zombie_id: int, zombie_transform, 
                           component_manager: ComponentManager) -> int:
        """
        寻找攻击目标（同行最左侧的植物）
        
        Returns:
            目标植物实体ID，如果没有则返回None
        """
        zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
        if not zombie_grid:
            return None
        
        # 获取同行的所有植物
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        closest_plant = None
        closest_distance = float('inf')
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 计算距离（只考虑X轴）
            distance = zombie_transform.x - plant_transform.x
            
            # 植物必须在僵尸左侧且在攻击范围内
            if 0 < distance < self.ATTACK_RANGE:
                if distance < closest_distance:
                    closest_distance = distance
                    closest_plant = plant_id
        
        return closest_plant
    
    def _attack_plant(self, plant_id: int, zombie, 
                      component_manager: ComponentManager, dt: float) -> None:
        """攻击植物"""
        # 检查攻击冷却
        if zombie.attack_timer > 0:
            return
        
        # 获取植物生命值
        plant_health = component_manager.get_component(plant_id, HealthComponent)
        if not plant_health:
            return
        
        # 造成伤害
        plant_health.take_damage(zombie.damage)
        
        # 开始攻击冷却
        zombie.start_attack()
    
    def _handle_special_behavior(self, entity_id: int, transform, zombie, 
                                  component_manager: ComponentManager, dt: float) -> None:
        """处理特殊僵尸行为"""
        from ..components import ZombieType, ZombieTypeComponent
        
        zombie_type_comp = component_manager.get_component(entity_id, ZombieTypeComponent)
        if not zombie_type_comp:
            return
        
        zombie_type = zombie_type_comp.zombie_type
        
        # 撑杆僵尸跳跃
        if zombie.has_pole and not zombie.has_jumped:
            self._check_pole_vault(entity_id, transform, zombie, component_manager)
        
        # 舞王僵尸召唤伴舞
        if zombie_type == ZombieType.DANCER and not zombie.dancer_spawned:
            if transform.x < 800:
                self._spawn_backup_dancers(entity_id, transform, zombie, component_manager)
        
        # 矿工僵尸挖掘
        if zombie_type == ZombieType.MINER:
            if not zombie.has_dug and transform.x < 200:
                transform.x = 100
                zombie.has_dug = True
        
        # 蹦极僵尸偷植物
        if zombie_type == ZombieType.BUNGEE:
            zombie.bungee_timer += dt
            if zombie.bungee_timer >= 3.0 and zombie.bungee_target is None:
                self._steal_plant(entity_id, transform, zombie, component_manager)
    
    def _check_pole_vault(self, entity_id: int, transform, zombie, 
                          component_manager: ComponentManager) -> None:
        """检查撑杆僵尸是否应该跳跃"""
        # 检查前方是否有植物
        zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
        if not zombie_grid:
            return
        
        # 检查前方是否有植物
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 检查植物是否在跳跃范围内
            distance = plant_transform.x - transform.x
            if 0 < distance < 120:  # 跳跃范围
                # 跳跃过植物
                transform.x = plant_transform.x + 50
                zombie.has_jumped = True
                zombie.speed = -30
                break
    
    def _spawn_backup_dancers(self, entity_id: int, transform, zombie,
                               component_manager: ComponentManager) -> None:
        """舞王僵尸召唤伴舞"""
        # 标记已召唤
        zombie.dancer_spawned = True
        # 实际召唤逻辑由EntityFactory处理
    
    def _steal_plant(self, entity_id: int, transform, zombie,
                     component_manager: ComponentManager) -> None:
        """蹦极僵尸偷植物"""
        # 简化实现
        zombie.bungee_target = 0  # 标记已偷取
    
    def _handle_zombie_death(self, zombie_id: int, component_manager: ComponentManager) -> None:
        """处理僵尸死亡"""
        zombie = component_manager.get_component(zombie_id, ZombieComponent)
        if zombie:
            # 触发死亡回调
            for callback in self.on_zombie_death_callbacks:
                callback(zombie_id, zombie.score_value)
    
    def register_death_callback(self, callback) -> None:
        """注册僵尸死亡回调"""
        self.on_zombie_death_callbacks.append(callback)
    
    def unregister_death_callback(self, callback) -> None:
        """注销僵尸死亡回调"""
        if callback in self.on_zombie_death_callbacks:
            self.on_zombie_death_callbacks.remove(callback)