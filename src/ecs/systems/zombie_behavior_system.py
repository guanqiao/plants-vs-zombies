"""
僵尸行为系统 - 处理僵尸的移动和攻击
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, VelocityComponent, ZombieComponent,
    GridPositionComponent, HealthComponent
)


class ZombieBehaviorSystem(System):
    """
    僵尸行为系统
    
    处理僵尸的移动、攻击和特殊行为
    - 普通移动
    - 攻击植物
    - 特殊僵尸能力（跳跃、飞行等）
    """
    
    def __init__(self, priority: int = 35):
        super().__init__(priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新僵尸行为"""
        # 获取所有僵尸实体
        entities = component_manager.query(
            TransformComponent, VelocityComponent, ZombieComponent
        )
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            velocity = component_manager.get_component(entity_id, VelocityComponent)
            zombie = component_manager.get_component(entity_id, ZombieComponent)
            
            if not all([transform, velocity, zombie]):
                continue
            
            # 更新计时器
            zombie.update_timer(dt)
            
            # 应用速度倍率
            velocity.apply_multiplier(zombie.slow_factor)
            
            # 处理特殊行为
            self._handle_special_behavior(entity_id, transform, zombie, component_manager, dt)
    
    def _handle_special_behavior(self, entity_id: int, transform, zombie, 
                                  component_manager: ComponentManager, dt: float) -> None:
        """处理特殊僵尸行为"""
        from ..components import ZombieType
        
        # 撑杆僵尸跳跃
        if zombie.has_pole and not zombie.has_jumped:
            self._check_pole_vault(entity_id, transform, zombie, component_manager)
        
        # 舞王僵尸召唤伴舞
        if zombie.zombie_type == ZombieType.DANCER and not zombie.dancer_spawned:
            if transform.x < 800:
                self._spawn_backup_dancers(entity_id, transform, zombie, component_manager)
        
        # 矿工僵尸挖掘
        if zombie.zombie_type == ZombieType.MINER:
            if not zombie.has_dug and transform.x < 200:
                transform.x = 100
                zombie.has_dug = True
        
        # 蹦极僵尸偷植物
        if zombie.zombie_type == ZombieType.BUNGEE:
            zombie.bungee_timer += dt
            if zombie.bungee_timer >= 3.0 and zombie.bungee_target is None:
                self._steal_plant(entity_id, transform, zombie, component_manager)
    
    def _check_pole_vault(self, entity_id: int, transform, zombie, 
                          component_manager: ComponentManager) -> None:
        """检查撑杆僵尸是否应该跳跃"""
        # 检查前方是否有植物
        grid_pos = component_manager.get_component(entity_id, GridPositionComponent)
        if not grid_pos:
            return
        
        # 简化实现：直接跳跃
        # 实际应该检查前方植物距离
        transform.x -= 120
        zombie.has_jumped = True
        zombie.speed = -30
    
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