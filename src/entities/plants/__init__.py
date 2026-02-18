import pygame
from src.entities.plant import Plant, PlantType
from src.entities.projectile import Projectile, ProjectileType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class Sunflower(Plant):
    """向日葵 - 产生阳光"""
    
    SUN_INTERVAL = 7.0
    SUN_VALUE = 25
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.SUNFLOWER, x, y)
        self.sun_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新向日葵行为 - 产生阳光"""
        self.sun_timer += dt
        
        if self.sun_timer >= self.SUN_INTERVAL:
            if game_manager.sun_system:
                game_manager.sun_system.add_sun_from_plant(self.x, self.y, self.SUN_VALUE)
            self.sun_timer = 0.0
    
    def _render_details(self, screen: pygame.Surface):
        """渲染向日葵细节"""
        center_x = int(self.x)
        center_y = int(self.y - 10)
        
        pygame.draw.circle(screen, (139, 69, 19), (center_x, center_y + 20), 8)
        
        for i in range(8):
            angle = i * 45 + self.animation_time * 30
            import math
            petal_x = center_x + int(15 * math.cos(math.radians(angle)))
            petal_y = center_y + int(15 * math.sin(math.radians(angle)))
            pygame.draw.circle(screen, (255, 200, 0), (petal_x, petal_y), 8)
        
        pygame.draw.circle(screen, (139, 69, 19), (center_x, center_y), 10)


class Peashooter(Plant):
    """豌豆射手 - 发射豌豆"""
    
    FIRE_INTERVAL = 1.5
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.PEASHOOTER, x, y)
        self.fire_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新豌豆射手行为 - 发射豌豆"""
        has_zombie_in_row = any(
            zombie.row == self.row and zombie.x > self.x
            for zombie in game_manager.zombies
        )
        
        if has_zombie_in_row:
            self.fire_timer += dt
            
            if self.fire_timer >= self.FIRE_INTERVAL:
                self._fire(game_manager)
                self.fire_timer = 0.0
    
    def _fire(self, game_manager: 'GameManager'):
        """发射豌豆"""
        projectile = Projectile(
            ProjectileType.PEA,
            self.x + self.width // 2,
            self.y,
            self.row
        )
        game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染豌豆射手细节"""
        pygame.draw.circle(screen, (0, 150, 0), (int(self.x), int(self.y - 10)), 15)
        
        pygame.draw.ellipse(screen, (0, 180, 0), 
                           (int(self.x + 5), int(self.y - 15), 20, 12))


class Repeater(Plant):
    """双发射手 - 发射两颗豌豆"""
    
    FIRE_INTERVAL = 1.5
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.REPEATER, x, y)
        self.fire_timer = 0.0
        self.second_shot = False
        self.second_shot_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新双发射手行为"""
        has_zombie_in_row = any(
            zombie.row == self.row and zombie.x > self.x
            for zombie in game_manager.zombies
        )
        
        if has_zombie_in_row:
            self.fire_timer += dt
            
            if self.fire_timer >= self.FIRE_INTERVAL:
                self._fire(game_manager)
                self.fire_timer = 0.0
                self.second_shot = True
                self.second_shot_timer = 0.0
        
        if self.second_shot:
            self.second_shot_timer += dt
            if self.second_shot_timer >= 0.1:
                self._fire(game_manager)
                self.second_shot = False
    
    def _fire(self, game_manager: 'GameManager'):
        """发射豌豆"""
        projectile = Projectile(
            ProjectileType.PEA,
            self.x + self.width // 2,
            self.y,
            self.row
        )
        game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染双发射手细节"""
        pygame.draw.circle(screen, (0, 120, 0), (int(self.x), int(self.y - 10)), 15)
        
        pygame.draw.ellipse(screen, (0, 180, 0), 
                           (int(self.x + 5), int(self.y - 20), 20, 12))
        pygame.draw.ellipse(screen, (0, 180, 0), 
                           (int(self.x + 5), int(self.y - 5), 20, 12))


class SnowPea(Plant):
    """寒冰射手 - 发射冰冻豌豆"""
    
    FIRE_INTERVAL = 1.5
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.SNOW_PEA, x, y)
        self.fire_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新寒冰射手行为"""
        has_zombie_in_row = any(
            zombie.row == self.row and zombie.x > self.x
            for zombie in game_manager.zombies
        )
        
        if has_zombie_in_row:
            self.fire_timer += dt
            
            if self.fire_timer >= self.FIRE_INTERVAL:
                self._fire(game_manager)
                self.fire_timer = 0.0
    
    def _fire(self, game_manager: 'GameManager'):
        """发射冰冻豌豆"""
        projectile = Projectile(
            ProjectileType.FROZEN_PEA,
            self.x + self.width // 2,
            self.y,
            self.row
        )
        game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染寒冰射手细节"""
        pygame.draw.circle(screen, (100, 150, 200), (int(self.x), int(self.y - 10)), 15)
        
        pygame.draw.ellipse(screen, (135, 206, 250), 
                           (int(self.x + 5), int(self.y - 15), 20, 12))


class WallNut(Plant):
    """坚果墙 - 高血量防御"""
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.WALLNUT, x, y)
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """坚果墙不主动行为"""
        pass
    
    def _render_details(self, screen: pygame.Surface):
        """渲染坚果墙细节"""
        health_ratio = self.health / 400
        
        if health_ratio > 0.66:
            color = (210, 180, 140)
        elif health_ratio > 0.33:
            color = (180, 140, 100)
        else:
            color = (139, 90, 43)
        
        pygame.draw.ellipse(screen, color, self.get_rect())
        
        eye_y = int(self.y - 10)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - 10), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 10), eye_y), 5)


class CherryBomb(Plant):
    """樱桃炸弹 - 范围爆炸"""
    
    EXPLOSION_DELAY = 1.0
    EXPLOSION_RADIUS = 100
    EXPLOSION_DAMAGE = 300
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.CHERRY_BOMB, x, y)
        self.timer = 0.0
        self.exploded = False
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新樱桃炸弹行为"""
        self.timer += dt
        
        if self.timer >= self.EXPLOSION_DELAY and not self.exploded:
            self._explode(game_manager)
    
    def _explode(self, game_manager: 'GameManager'):
        """爆炸"""
        self.exploded = True
        
        for zombie in game_manager.zombies[:]:
            dist = ((zombie.x - self.x) ** 2 + (zombie.y - self.y) ** 2) ** 0.5
            if dist <= self.EXPLOSION_RADIUS:
                zombie.take_damage(self.EXPLOSION_DAMAGE)
        
        self.health = 0
    
    def _render_details(self, screen: pygame.Surface):
        """渲染樱桃炸弹细节"""
        pygame.draw.circle(screen, (220, 20, 60), (int(self.x - 10), int(self.y)), 18)
        pygame.draw.circle(screen, (220, 20, 60), (int(self.x + 10), int(self.y)), 18)
        
        pygame.draw.line(screen, (0, 100, 0), 
                        (int(self.x - 5), int(self.y - 20)),
                        (int(self.x), int(self.y - 30)), 3)
        pygame.draw.line(screen, (0, 100, 0), 
                        (int(self.x + 5), int(self.y - 20)),
                        (int(self.x), int(self.y - 30)), 3)


class PotatoMine(Plant):
    """土豆地雷 - 埋地爆炸"""
    
    ARM_TIME = 14.0
    EXPLOSION_RADIUS = 50
    EXPLOSION_DAMAGE = 200
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.POTATO_MINE, x, y)
        self.armed = False
        self.timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新土豆地雷行为"""
        if not self.armed:
            self.timer += dt
            if self.timer >= self.ARM_TIME:
                self.armed = True
        else:
            for zombie in game_manager.zombies:
                if zombie.row == self.row:
                    dist = abs(zombie.x - self.x)
                    if dist <= self.EXPLOSION_RADIUS:
                        self._explode(game_manager)
                        break
    
    def _explode(self, game_manager: 'GameManager'):
        """爆炸"""
        for zombie in game_manager.zombies[:]:
            dist = ((zombie.x - self.x) ** 2 + (zombie.y - self.y) ** 2) ** 0.5
            if dist <= self.EXPLOSION_RADIUS:
                zombie.take_damage(self.EXPLOSION_DAMAGE)
        
        self.health = 0
    
    def _render_details(self, screen: pygame.Surface):
        """渲染土豆地雷细节"""
        if self.armed:
            pygame.draw.ellipse(screen, (160, 82, 45), 
                              (int(self.x - 20), int(self.y - 15), 40, 30))
            pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y - 20)), 5)
        else:
            pygame.draw.ellipse(screen, (139, 69, 19), 
                              (int(self.x - 15), int(self.y - 10), 30, 20))


class Chomper(Plant):
    """大嘴花 - 吞噬僵尸"""
    
    CHEW_TIME = 30.0
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.CHOMPER, x, y)
        self.chewing = False
        self.chew_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新大嘴花行为"""
        if self.chewing:
            self.chew_timer += dt
            if self.chew_timer >= self.CHEW_TIME:
                self.chewing = False
                self.chew_timer = 0.0
        else:
            for zombie in game_manager.zombies[:]:
                if zombie.row == self.row:
                    dist = abs(zombie.x - self.x)
                    if dist <= 50 and not zombie.zombie_type.name == 'GARGANTUAR':
                        self._eat_zombie(zombie, game_manager)
                        break
    
    def _eat_zombie(self, zombie, game_manager: 'GameManager'):
        """吞噬僵尸"""
        game_manager.remove_zombie(zombie)
        self.chewing = True
        self.chew_timer = 0.0
    
    def _render_details(self, screen: pygame.Surface):
        """渲染大嘴花细节"""
        pygame.draw.rect(screen, (0, 100, 0), 
                        (int(self.x - 5), int(self.y + 10), 10, 40))
        
        head_color = (128, 0, 128) if not self.chewing else (100, 0, 100)
        pygame.draw.circle(screen, head_color, (int(self.x), int(self.y - 10)), 25)
        
        pygame.draw.ellipse(screen, (200, 100, 200), 
                           (int(self.x - 20), int(self.y - 20), 15, 25))
        pygame.draw.ellipse(screen, (200, 100, 200), 
                           (int(self.x + 5), int(self.y - 20), 15, 25))
