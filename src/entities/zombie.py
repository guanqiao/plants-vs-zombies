import pygame
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class ZombieType(Enum):
    """僵尸类型枚举"""
    NORMAL = auto()
    CONEHEAD = auto()
    BUCKETHEAD = auto()
    RUNNER = auto()
    GARGANTUAR = auto()
    POLE_VAULTER = auto()
    SCREEN_DOOR = auto()
    FOOTBALL = auto()
    DANCER = auto()
    BACKUP_DANCER = auto()
    BALLOON = auto()
    MINER = auto()
    POGO = auto()
    BUNGEE = auto()


ZOMBIE_CONFIGS = {
    ZombieType.NORMAL: {
        'health': 100,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 80,
        'color': (128, 128, 128),
        'score_value': 10,
    },
    ZombieType.CONEHEAD: {
        'health': 200,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (255, 140, 0),
        'score_value': 20,
    },
    ZombieType.BUCKETHEAD: {
        'health': 400,
        'speed': -30,
        'damage': 20,
        'width': 50,
        'height': 90,
        'color': (169, 169, 169),
        'score_value': 30,
    },
    ZombieType.RUNNER: {
        'health': 80,
        'speed': -60,
        'damage': 15,
        'width': 45,
        'height': 75,
        'color': (220, 220, 220),
        'score_value': 15,
    },
    ZombieType.GARGANTUAR: {
        'health': 1500,
        'speed': -15,
        'damage': 100,
        'width': 80,
        'height': 120,
        'color': (105, 105, 105),
        'score_value': 100,
    },
    ZombieType.POLE_VAULTER: {
        'health': 100,
        'speed': -40,
        'damage': 20,
        'width': 50,
        'height': 85,
        'color': (180, 180, 200),
        'score_value': 25,
    },
    ZombieType.SCREEN_DOOR: {
        'health': 300,
        'speed': -30,
        'damage': 20,
        'width': 55,
        'height': 85,
        'color': (100, 100, 120),
        'score_value': 25,
    },
    ZombieType.FOOTBALL: {
        'health': 800,
        'speed': -50,
        'damage': 30,
        'width': 55,
        'height': 90,
        'color': (139, 69, 19),
        'score_value': 50,
    },
    ZombieType.DANCER: {
        'health': 200,
        'speed': -25,
        'damage': 20,
        'width': 55,
        'height': 90,
        'color': (128, 0, 128),
        'score_value': 40,
    },
    ZombieType.BACKUP_DANCER: {
        'health': 100,
        'speed': -25,
        'damage': 15,
        'width': 50,
        'height': 85,
        'color': (150, 50, 150),
        'score_value': 15,
    },
    ZombieType.BALLOON: {
        'health': 50,
        'speed': -35,
        'damage': 20,
        'width': 45,
        'height': 110,
        'color': (255, 100, 100),
        'score_value': 20,
    },
    ZombieType.MINER: {
        'health': 150,
        'speed': -35,
        'damage': 20,
        'width': 50,
        'height': 85,
        'color': (100, 80, 60),
        'score_value': 30,
    },
    ZombieType.POGO: {
        'health': 200,
        'speed': -45,
        'damage': 20,
        'width': 50,
        'height': 100,
        'color': (200, 150, 100),
        'score_value': 30,
    },
    ZombieType.BUNGEE: {
        'health': 100,
        'speed': 0,
        'damage': 0,
        'width': 50,
        'height': 80,
        'color': (100, 100, 150),
        'score_value': 25,
    },
}


class Zombie:
    """僵尸基类"""
    
    def __init__(self, zombie_type: ZombieType, x: float, y: float):
        self.zombie_type = zombie_type
        self.x = x
        self.y = y
        
        config = ZOMBIE_CONFIGS.get(zombie_type, {})
        self.health = config.get('health', 100)
        self.base_speed = config.get('speed', -30)
        self.speed = self.base_speed
        self.damage = config.get('damage', 20)
        self.width = config.get('width', 50)
        self.height = config.get('height', 80)
        self.color = config.get('color', (128, 128, 128))
        self.score_value = config.get('score_value', 10)
        
        self.row: int = 0
        self.is_attacking = False
        self.attack_cooldown = 0.0
        self.attack_interval = 1.0
        
        self.slow_factor = 1.0
        self.slow_duration = 0.0
        
        self.animation_time = 0.0
        
        # 特殊僵尸状态
        self.has_armor = zombie_type in [ZombieType.BUCKETHEAD, ZombieType.SCREEN_DOOR, ZombieType.FOOTBALL]
        self.armor_health = self._get_armor_health()
        self.has_pole = zombie_type == ZombieType.POLE_VAULTER
        self.has_jumped = False
        self.is_flying = zombie_type == ZombieType.BALLOON
        self.is_underground = False
        self.has_dug = False
        self.is_pogoing = zombie_type == ZombieType.POGO
        self.can_jump = True
        self.dancer_spawned = False
        self.backup_dancers: list = []
        self.bungee_target = None
        self.bungee_timer = 0.0
    
    def _get_armor_health(self) -> int:
        """获取护甲血量"""
        if self.zombie_type == ZombieType.BUCKETHEAD:
            return 300
        elif self.zombie_type == ZombieType.SCREEN_DOOR:
            return 200
        elif self.zombie_type == ZombieType.FOOTBALL:
            return 600
        return 0
    
    def remove_armor(self):
        """移除护甲"""
        self.has_armor = False
        self.armor_health = 0
    
    def take_damage(self, damage: int):
        """受到伤害"""
        if self.has_armor and self.armor_health > 0:
            self.armor_health -= damage
            if self.armor_health <= 0:
                self.has_armor = False
        else:
            self.health -= damage
    
    def is_dead(self) -> bool:
        """是否死亡"""
        return self.health <= 0
    
    def get_rect(self) -> pygame.Rect:
        """获取碰撞矩形"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
    
    def apply_slow(self, factor: float, duration: float):
        """应用减速效果"""
        self.slow_factor = factor
        self.slow_duration = duration
        self.speed = self.base_speed * factor
    
    def remove_slow(self):
        """移除减速效果"""
        self.slow_factor = 1.0
        self.slow_duration = 0.0
        self.speed = self.base_speed
    
    def attack(self, plant):
        """攻击植物"""
        if self.attack_cooldown <= 0:
            plant.take_damage(self.damage)
            self.attack_cooldown = self.attack_interval
    
    def update(self, dt: float, game_manager: 'GameManager'):
        """更新僵尸状态"""
        self.animation_time += dt
        
        if self.slow_duration > 0:
            self.slow_duration -= dt
            if self.slow_duration <= 0:
                self.remove_slow()
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # 更新特殊僵尸行为
        self._update_special_behavior(dt, game_manager)
        
        if not self.is_attacking and not self.is_underground:
            self.x += self.speed * dt
        
        if self.is_dead():
            game_manager.remove_zombie(self)
    
    def _update_special_behavior(self, dt: float, game_manager: 'GameManager'):
        """更新特殊僵尸行为"""
        # 撑杆僵尸跳跃
        if self.has_pole and not self.has_jumped:
            for plant in game_manager.plants:
                if plant.row == self.row:
                    dist = abs(plant.x - self.x)
                    if 30 < dist < 80:
                        self.x -= 120
                        self.has_jumped = True
                        self.speed = -30
                        break
        
        # 舞王僵尸召唤伴舞
        if self.zombie_type == ZombieType.DANCER and not self.dancer_spawned:
            if self.x < 800:
                self._spawn_backup_dancers(game_manager)
                self.dancer_spawned = True
        
        # 矿工僵尸挖掘
        if self.zombie_type == ZombieType.MINER:
            if not self.has_dug and self.x < 200:
                self.is_underground = True
                self.x = 100
                self.has_dug = True
                self.is_underground = False
        
        # 蹦极僵尸偷植物
        if self.zombie_type == ZombieType.BUNGEE:
            self.bungee_timer += dt
            if self.bungee_timer >= 3.0 and self.bungee_target is None:
                self._steal_plant(game_manager)
    
    def _spawn_backup_dancers(self, game_manager: 'GameManager'):
        """舞王僵尸召唤伴舞"""
        from src.entities.zombie import Zombie, ZombieType
        
        positions = [
            (self.row - 1, self.x - 60),
            (self.row - 1, self.x + 60),
            (self.row + 1, self.x - 60),
            (self.row + 1, self.x + 60),
        ]
        
        for row, x in positions:
            if 0 <= row < 5:
                dancer = Zombie(ZombieType.BACKUP_DANCER, x, 100 + row * 100 + 50)
                dancer.row = row
                game_manager.add_zombie(dancer)
                self.backup_dancers.append(dancer)
    
    def _steal_plant(self, game_manager: 'GameManager'):
        """蹦极僵尸偷植物"""
        for plant in game_manager.plants[:]:
            if plant.row == self.row:
                dist = abs(plant.x - self.x)
                if dist < 100:
                    game_manager.remove_plant(plant)
                    self.health = 0
                    break
    
    def render(self, screen: pygame.Surface):
        """渲染僵尸"""
        rect = self.get_rect()
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        
        self._render_details(screen)
    
    def _render_details(self, screen: pygame.Surface):
        """渲染僵尸细节"""
        eye_y = self.y - self.height // 4
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - 10), int(eye_y)), 5)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x + 10), int(eye_y)), 5)
        
        if self.slow_duration > 0:
            pygame.draw.rect(screen, (0, 100, 255), self.get_rect(), 3)
        
        # 渲染护甲
        if self.has_armor:
            armor_color = (169, 169, 169) if self.zombie_type == ZombieType.BUCKETHEAD else \
                         (100, 100, 120) if self.zombie_type == ZombieType.SCREEN_DOOR else \
                         (139, 69, 19)
            pygame.draw.rect(screen, armor_color, 
                           (int(self.x - 15), int(self.y - 30), 30, 20))
        
        # 渲染撑杆
        if self.has_pole and not self.has_jumped:
            pygame.draw.line(screen, (139, 69, 19), 
                           (int(self.x), int(self.y - 20)),
                           (int(self.x + 30), int(self.y - 40)), 4)
        
        # 渲染气球
        if self.is_flying:
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(self.x), int(self.y - 50)), 20)
            pygame.draw.line(screen, (100, 100, 100), 
                           (int(self.x), int(self.y - 30)),
                           (int(self.x), int(self.y - 10)), 2)
        
        # 渲染跳跳杆
        if self.is_pogoing:
            pygame.draw.line(screen, (150, 75, 0), 
                           (int(self.x - 10), int(self.y + 20)),
                           (int(self.x - 10), int(self.y + 50)), 4)
            pygame.draw.line(screen, (150, 75, 0), 
                           (int(self.x + 10), int(self.y + 20)),
                           (int(self.x + 10), int(self.y + 50)), 4)
        
        # 渲染舞王特效
        if self.zombie_type == ZombieType.DANCER:
            pygame.draw.circle(screen, (255, 0, 255), 
                             (int(self.x), int(self.y - 35)), 8)
        
        # 渲染蹦极绳
        if self.zombie_type == ZombieType.BUNGEE:
            pygame.draw.line(screen, (100, 100, 100), 
                           (int(self.x), int(self.y - 100)),
                           (int(self.x), int(self.y - 30)), 3)
