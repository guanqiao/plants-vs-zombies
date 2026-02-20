"""
投射物系统 - 处理投射物的移动和碰撞效果
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, ProjectileComponent, GridPositionComponent,
    VelocityComponent, HealthComponent, ZombieComponent
)
from ...core.event_bus import EventBus, Event, EventType


class ProjectileSystem(System):
    """
    投射物系统
    
    处理投射物的生命周期和碰撞效果
    - 移动
    - 造成伤害
    - 溅射效果
    - 减速效果
    """
    
    def __init__(self, entity_manager, event_bus: EventBus = None, priority: int = 25):
        super().__init__(priority)
        self.entity_manager = entity_manager
        self.event_bus = event_bus
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新投射物"""
        # 获取所有投射物实体
        entities = component_manager.query(
            TransformComponent, ProjectileComponent
        )
        
        entities_to_remove = []
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            projectile = component_manager.get_component(entity_id, ProjectileComponent)
            grid_pos = component_manager.get_component(entity_id, GridPositionComponent)
            
            if not all([transform, projectile, grid_pos]):
                continue
            
            # 更新生命周期
            if not projectile.update_lifetime(dt):
                entities_to_remove.append(entity_id)
                continue
            
            # 检查碰撞
            if self._check_collision(entity_id, transform, projectile, grid_pos, component_manager):
                entities_to_remove.append(entity_id)
        
        # 移除过期的投射物
        for entity_id in entities_to_remove:
            self.entity_manager.destroy_entity(entity_id)
    
    def _check_collision(self, entity_id: int, transform, projectile, grid_pos,
                         component_manager: ComponentManager) -> bool:
        """检查投射物是否击中僵尸"""
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            
            if not zombie_transform or not zombie_grid:
                continue
            
            if zombie_grid.row != grid_pos.row:
                continue
            
            distance = abs(zombie_transform.x - transform.x)
            if distance < 30:
                self._apply_damage(zombie_id, projectile, zombie_transform, component_manager)
                return True
        
        if transform.x > 900:
            return True
        
        return False
    
    def _apply_damage(self, zombie_id: int, projectile, zombie_transform,
                      component_manager: ComponentManager) -> None:
        """应用伤害"""
        health = component_manager.get_component(zombie_id, HealthComponent)
        zombie = component_manager.get_component(zombie_id, ZombieComponent)
        
        if not health or not zombie:
            return
        
        damage = projectile.damage
        damage_type = "normal"
        
        if projectile.applies_slow:
            damage_type = "ice"
        
        if zombie.has_armor:
            damage = zombie.take_armor_damage(damage)
        
        if damage > 0:
            health.take_damage(damage)
        
        if projectile.applies_slow:
            zombie.apply_slow(projectile.slow_factor, projectile.slow_duration)
        
        if projectile.is_splash:
            self._apply_splash_damage(zombie_id, projectile, zombie_transform, component_manager)
        
        if self.event_bus and damage > 0:
            self.event_bus.publish(Event(
                EventType.DAMAGE_DEALT,
                {
                    'x': zombie_transform.x,
                    'y': zombie_transform.y,
                    'damage': damage,
                    'damage_type': damage_type,
                    'target_id': zombie_id
                }
            ))
    
    def _apply_splash_damage(self, target_id: int, projectile, target_transform,
                             component_manager: ComponentManager) -> None:
        """应用溅射伤害"""
        zombies = component_manager.query(TransformComponent, ZombieComponent, HealthComponent)
        
        for zombie_id in zombies:
            if zombie_id == target_id:
                continue
            
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            if not zombie_transform:
                continue
            
            distance = ((zombie_transform.x - target_transform.x) ** 2 + 
                       (zombie_transform.y - target_transform.y) ** 2) ** 0.5
            
            if distance <= projectile.splash_radius:
                zombie_health = component_manager.get_component(zombie_id, HealthComponent)
                if zombie_health:
                    splash_damage = int(projectile.damage * 0.5)
                    zombie_health.take_damage(splash_damage)
                    
                    if self.event_bus:
                        self.event_bus.publish(Event(
                            EventType.DAMAGE_DEALT,
                            {
                                'x': zombie_transform.x,
                                'y': zombie_transform.y,
                                'damage': splash_damage,
                                'damage_type': 'fire',
                                'target_id': zombie_id
                            }
                        ))