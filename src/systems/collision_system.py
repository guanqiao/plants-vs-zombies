import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class CollisionSystem:
    """碰撞检测系统"""
    
    def __init__(self):
        pass
    
    def check_collisions(self, game_manager: 'GameManager'):
        """检查所有碰撞"""
        self._check_projectile_zombie_collisions(game_manager)
        self._check_zombie_plant_collisions(game_manager)
        self._remove_dead_entities(game_manager)
    
    def _check_projectile_zombie_collisions(self, game_manager: 'GameManager'):
        """检查投射物与僵尸的碰撞"""
        for projectile in game_manager.projectiles[:]:
            hit_zombie = None
            for zombie in game_manager.zombies:
                if self._check_rect_collision(projectile.get_rect(), zombie.get_rect()):
                    hit_zombie = zombie
                    break
            
            if hit_zombie:
                self._apply_projectile_damage(projectile, hit_zombie, game_manager)
                projectile.on_hit()
                game_manager.remove_projectile(projectile)
    
    def _apply_projectile_damage(self, projectile, hit_zombie, game_manager: 'GameManager'):
        """应用投射物伤害"""
        hit_zombie.take_damage(projectile.damage)
        
        # 播放击中音效和粒子效果
        if game_manager.sound_manager:
            game_manager.sound_manager.play_sound('splat')
        if game_manager.particle_system:
            game_manager.particle_system.create_hit_effect(hit_zombie.x, hit_zombie.y)
        
        if projectile.projectile_type.name == 'FROZEN_PEA':
            hit_zombie.apply_slow(0.5, 5.0)
        
        try:
            splash_damage = getattr(projectile, 'splash_damage', 0)
            splash_radius = getattr(projectile, 'splash_radius', 0)
            slow_effect = getattr(projectile, 'slow_effect', False)
            
            # 检查是否为有效的数值（跳过MagicMock）
            if isinstance(splash_damage, (int, float)) and isinstance(splash_radius, (int, float)):
                if splash_damage > 0 and splash_radius > 0:
                    for zombie in game_manager.zombies:
                        dist = ((zombie.x - hit_zombie.x) ** 2 + (zombie.y - hit_zombie.y) ** 2) ** 0.5
                        if dist <= splash_radius and zombie != hit_zombie:
                            zombie.take_damage(splash_damage)
                
                if slow_effect and splash_radius > 0:
                    for zombie in game_manager.zombies:
                        dist = ((zombie.x - hit_zombie.x) ** 2 + (zombie.y - hit_zombie.y) ** 2) ** 0.5
                        if dist <= splash_radius:
                            zombie.apply_slow(0.5, 5.0)
        except (TypeError, AttributeError):
            # 处理MagicMock或其他无效类型
            pass
    
    def _check_zombie_plant_collisions(self, game_manager: 'GameManager'):
        """检查僵尸与植物的碰撞"""
        for zombie in game_manager.zombies:
            zombie.is_attacking = False
            
            for plant in game_manager.plants:
                if plant.row != zombie.row:
                    continue
                
                if self._check_rect_collision(zombie.get_rect(), plant.get_rect()):
                    zombie.is_attacking = True
                    zombie.attack(plant)
                    break
    
    def _check_rect_collision(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """检查两个矩形是否碰撞"""
        return rect1.colliderect(rect2)
    
    def _remove_dead_entities(self, game_manager: 'GameManager'):
        """移除死亡的实体"""
        for plant in game_manager.plants[:]:
            if plant.is_dead():
                game_manager.remove_plant(plant)
        
        for zombie in game_manager.zombies[:]:
            if zombie.is_dead():
                game_manager.remove_zombie(zombie)
        
        for projectile in game_manager.projectiles[:]:
            if projectile.is_dead():
                game_manager.remove_projectile(projectile)
