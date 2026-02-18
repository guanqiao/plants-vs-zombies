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
        
        # 播放爆炸音效和粒子效果
        if game_manager.sound_manager:
            game_manager.sound_manager.play_sound('explosion')
        if game_manager.particle_system:
            game_manager.particle_system.create_explosion(self.x, self.y, intensity=30)
        
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
        # 播放爆炸音效和粒子效果
        if game_manager.sound_manager:
            game_manager.sound_manager.play_sound('explosion')
        if game_manager.particle_system:
            game_manager.particle_system.create_explosion(self.x, self.y, intensity=20)
        
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


class Threepeater(Plant):
    """三线射手 - 同时攻击三行"""
    
    FIRE_INTERVAL = 1.5
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.THREEPEATER, x, y)
        self.fire_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新三线射手行为"""
        rows_to_check = [self.row - 1, self.row, self.row + 1]
        has_zombie = False
        
        for row in rows_to_check:
            if row < 0 or row >= 5:
                continue
            for zombie in game_manager.zombies:
                if zombie.row == row and zombie.x > self.x:
                    has_zombie = True
                    break
            if has_zombie:
                break
        
        if has_zombie:
            self.fire_timer += dt
            
            if self.fire_timer >= self.FIRE_INTERVAL:
                self._fire(game_manager)
                self.fire_timer = 0.0
    
    def _fire(self, game_manager: 'GameManager'):
        """发射三行豌豆"""
        rows = [self.row - 1, self.row, self.row + 1]
        for row in rows:
            if 0 <= row < 5:
                projectile = Projectile(
                    ProjectileType.PEA,
                    self.x + self.width // 2,
                    self.y + (row - self.row) * 80,
                    row
                )
                game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染三线射手细节"""
        pygame.draw.circle(screen, (0, 150, 0), (int(self.x), int(self.y - 10)), 15)
        
        for i, offset in enumerate([-15, 0, 15]):
            pygame.draw.ellipse(screen, (0, 180, 0), 
                               (int(self.x + 5), int(self.y - 20 + offset), 20, 10))


class MelonPult(Plant):
    """西瓜投手 - 投掷西瓜造成范围伤害"""
    
    FIRE_INTERVAL = 3.0
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.MELON_PULT, x, y)
        self.fire_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新西瓜投手行为"""
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
        """发射西瓜"""
        target_zombie = None
        for zombie in game_manager.zombies:
            if zombie.row == self.row and zombie.x > self.x:
                if target_zombie is None or zombie.x < target_zombie.x:
                    target_zombie = zombie
        
        if target_zombie:
            projectile = Projectile(
                ProjectileType.MELON,
                self.x + self.width // 2,
                self.y,
                self.row
            )
            game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染西瓜投手细节"""
        pygame.draw.rect(screen, (0, 120, 0), 
                        (int(self.x - 10), int(self.y), 20, 30))
        
        pygame.draw.ellipse(screen, (0, 150, 0), 
                           (int(self.x - 15), int(self.y - 25), 30, 25))
        
        pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y - 15)), 12)
        pygame.draw.circle(screen, (0, 100, 0), (int(self.x - 4), int(self.y - 18)), 3)
        pygame.draw.circle(screen, (0, 100, 0), (int(self.x + 4), int(self.y - 12)), 3)


class WinterMelon(Plant):
    """冰西瓜 - 西瓜+减速效果"""
    
    FIRE_INTERVAL = 3.0
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.WINTER_MELON, x, y)
        self.fire_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新冰西瓜行为"""
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
        """发射冰冻西瓜"""
        target_zombie = None
        for zombie in game_manager.zombies:
            if zombie.row == self.row and zombie.x > self.x:
                if target_zombie is None or zombie.x < target_zombie.x:
                    target_zombie = zombie
        
        if target_zombie:
            projectile = Projectile(
                ProjectileType.FROZEN_MELON,
                self.x + self.width // 2,
                self.y,
                self.row
            )
            game_manager.add_projectile(projectile)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染冰西瓜细节"""
        pygame.draw.rect(screen, (100, 150, 200), 
                        (int(self.x - 10), int(self.y), 20, 30))
        
        pygame.draw.ellipse(screen, (135, 206, 250), 
                           (int(self.x - 15), int(self.y - 25), 30, 25))
        
        pygame.draw.circle(screen, (255, 100, 0), (int(self.x), int(self.y - 15)), 12)
        pygame.draw.circle(screen, (200, 230, 255), (int(self.x), int(self.y - 15)), 8)
        pygame.draw.circle(screen, (0, 100, 0), (int(self.x - 4), int(self.y - 18)), 3)
        pygame.draw.circle(screen, (0, 100, 0), (int(self.x + 4), int(self.y - 12)), 3)


class TallNut(Plant):
    """高坚果 - 双倍血量防御"""
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.TALL_NUT, x, y)
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """高坚果不主动行为"""
        pass
    
    def _render_details(self, screen: pygame.Surface):
        """渲染高坚果细节"""
        health_ratio = self.health / 800
        
        if health_ratio > 0.66:
            color = (210, 180, 140)
        elif health_ratio > 0.33:
            color = (180, 140, 100)
        else:
            color = (139, 90, 43)
        
        rect = self.get_rect()
        pygame.draw.rect(screen, color, rect)
        
        eye_y = int(self.y - 20)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - 10), eye_y), 5)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 10), eye_y), 5)
        
        mouth_y = int(self.y + 10)
        pygame.draw.arc(screen, (0, 0, 0), 
                       (int(self.x - 10), mouth_y - 5, 20, 15), 
                       3.14, 0, 2)


class Spikeweed(Plant):
    """地刺 - 对踩上的僵尸造成持续伤害"""
    
    DAMAGE_INTERVAL = 0.5
    DAMAGE = 20
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.SPIKEWEED, x, y)
        self.damage_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新地刺行为"""
        self.damage_timer += dt
        
        if self.damage_timer >= self.DAMAGE_INTERVAL:
            for zombie in game_manager.zombies[:]:
                if zombie.row == self.row:
                    dist = abs(zombie.x - self.x)
                    if dist <= 40:
                        zombie.take_damage(self.DAMAGE)
                        
                        if hasattr(zombie, 'zombie_type') and 'ZOMBONI' in zombie.zombie_type.name:
                            self.health = 0
            
            self.damage_timer = 0.0
    
    def _render_details(self, screen: pygame.Surface):
        """渲染地刺细节"""
        import math
        center_y = int(self.y + 10)
        
        for i in range(5):
            x_offset = (i - 2) * 10
            pygame.draw.polygon(screen, (150, 150, 150), [
                (int(self.x + x_offset), center_y),
                (int(self.x + x_offset - 5), center_y + 15),
                (int(self.x + x_offset + 5), center_y + 15)
            ])


class MagnetShroom(Plant):
    """磁力菇 - 吸走僵尸的金属防具"""
    
    MAGNET_INTERVAL = 8.0
    MAGNET_RANGE = 150
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.MAGNET_SHROOM, x, y)
        self.magnet_timer = 0.0
        self.has_item = False
        self.item_timer = 0.0
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新磁力菇行为"""
        if self.has_item:
            self.item_timer += dt
            if self.item_timer >= 5.0:
                self.has_item = False
                self.item_timer = 0.0
            return
        
        self.magnet_timer += dt
        
        if self.magnet_timer >= self.MAGNET_INTERVAL:
            for zombie in game_manager.zombies:
                dist = ((zombie.x - self.x) ** 2 + (zombie.y - self.y) ** 2) ** 0.5
                if dist <= self.MAGNET_RANGE:
                    if self._try_remove_metal(zombie):
                        self.has_item = True
                        self.item_timer = 0.0
                        self.magnet_timer = 0.0
                        break
    
    def _try_remove_metal(self, zombie) -> bool:
        """尝试移除僵尸的金属防具"""
        metal_types = ['BUCKET', 'FOOTBALL', 'SCREEN_DOOR', 'JACK_IN_THE_BOX']
        
        if hasattr(zombie, 'zombie_type'):
            ztype = zombie.zombie_type.name
            for metal in metal_types:
                if metal in ztype:
                    zombie.take_damage(0)
                    if hasattr(zombie, 'remove_armor'):
                        zombie.remove_armor()
                    return True
        return False
    
    def _render_details(self, screen: pygame.Surface):
        """渲染磁力菇细节"""
        if self.has_item:
            color = (200, 100, 200)
        else:
            color = (128, 0, 128)
        
        pygame.draw.ellipse(screen, color, 
                           (int(self.x - 15), int(self.y - 10), 30, 25))
        
        pygame.draw.ellipse(screen, (200, 150, 200), 
                           (int(self.x - 8), int(self.y - 20), 16, 12))
        
        if self.has_item:
            pygame.draw.rect(screen, (100, 100, 100), 
                           (int(self.x - 8), int(self.y - 15), 16, 12))


class Pumpkin(Plant):
    """南瓜头 - 套在其他植物上提供额外防御"""
    
    def __init__(self, x: float, y: float):
        super().__init__(PlantType.PUMPKIN, x, y)
        self.host_plant = None
    
    def _update_behavior(self, dt: float, game_manager: 'GameManager'):
        """南瓜头不主动行为"""
        pass
    
    def _render_details(self, screen: pygame.Surface):
        """渲染南瓜头细节"""
        health_ratio = self.health / 400
        
        if health_ratio > 0.66:
            color = (255, 140, 0)
        elif health_ratio > 0.33:
            color = (220, 120, 0)
        else:
            color = (180, 100, 0)
        
        rect = self.get_rect()
        pygame.draw.ellipse(screen, color, rect)
        
        pygame.draw.ellipse(screen, (200, 100, 0), 
                           (int(self.x - 15), int(self.y - 10), 30, 20))
        
        eye_y = int(self.y - 5)
        pygame.draw.ellipse(screen, (50, 30, 0), 
                           (int(self.x - 12), eye_y, 8, 12))
        pygame.draw.ellipse(screen, (50, 30, 0), 
                           (int(self.x + 4), eye_y, 8, 12))
        
        mouth_y = int(self.y + 5)
        pygame.draw.arc(screen, (50, 30, 0), 
                       (int(self.x - 10), mouth_y - 3, 20, 12), 
                       3.14, 0, 2)
