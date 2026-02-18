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
            for zombie in game_manager.zombies:
                if self._check_rect_collision(projectile.get_rect(), zombie.get_rect()):
                    zombie.take_damage(projectile.damage)
                    
                    if projectile.projectile_type.name == 'FROZEN_PEA':
                        zombie.apply_slow(0.5, 5.0)
                    
                    projectile.on_hit()
                    game_manager.remove_projectile(projectile)
                    break
    
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
