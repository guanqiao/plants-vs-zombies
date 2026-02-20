"""
僵尸水族馆小游戏

管理僵尸、喂食、金币收集
"""

import pygame
import random
import math
from dataclasses import dataclass
from typing import List
from .base_game import BaseMiniGame


@dataclass
class AquariumZombie:
    """水族馆僵尸"""
    x: float
    y: float
    size: float = 30
    hunger: float = 0.0
    gold_timer: float = 0.0
    is_alive: bool = True
    
    def update(self, dt: float):
        """更新僵尸状态"""
        self.hunger += dt * 5
        self.gold_timer += dt
        
        # 随机游动
        self.x += random.uniform(-20, 20) * dt
        self.y += random.uniform(-20, 20) * dt
        
        # 边界限制
        self.x = max(50, min(850, self.x))
        self.y = max(100, min(550, self.y))
    
    def feed(self):
        """喂食"""
        self.hunger = max(0, self.hunger - 30)
    
    def can_produce_gold(self) -> bool:
        """是否可以产生金币"""
        return self.hunger < 50 and self.gold_timer >= 10.0
    
    def collect_gold(self):
        """收集金币"""
        self.gold_timer = 0.0
        return random.choice([10, 25, 50])
    
    def render(self, screen: pygame.Surface):
        """渲染僵尸"""
        # 身体
        pygame.draw.ellipse(screen, (100, 150, 100), 
                           (int(self.x - self.size), int(self.y - self.size//2), 
                            int(self.size*2), int(self.size)))
        # 眼睛
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - 8), int(self.y - 5)), 4)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x + 8), int(self.y - 5)), 4)
        
        # 饥饿指示器
        if self.hunger > 50:
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(self.x), int(self.y - 25)), 5)


class ZombieAquarium(BaseMiniGame):
    """僵尸水族馆小游戏"""
    
    def __init__(self):
        super().__init__()
        self.zombies: List[AquariumZombie] = []
        self.food_count = 3
        self.food_timer = 0.0
        self.gold = 0
        self.max_zombies = 10
        self.game_time = 0.0
        self.max_time = 180.0  # 3分钟
        
    def add_zombie(self, x: float, y: float):
        """添加僵尸"""
        if len(self.zombies) < self.max_zombies:
            self.zombies.append(AquariumZombie(x, y))
    
    def feed_zombie(self, x: int, y: int) -> bool:
        """喂食僵尸"""
        if self.food_count <= 0:
            return False
        
        for zombie in self.zombies:
            dist = math.sqrt((zombie.x - x)**2 + (zombie.y - y)**2)
            if dist < zombie.size and zombie.hunger > 30:
                zombie.feed()
                self.food_count -= 1
                return True
        
        return False
    
    def collect_gold(self, x: int, y: int) -> int:
        """收集金币"""
        for zombie in self.zombies:
            dist = math.sqrt((zombie.x - x)**2 + (zombie.y - y)**2)
            if dist < zombie.size and zombie.can_produce_gold():
                gold = zombie.collect_gold()
                self.gold += gold
                self.score += gold
                return gold
        
        return 0
    
    def update(self, dt: float):
        """更新游戏状态"""
        self.game_time += dt
        
        # 食物恢复
        self.food_timer += dt
        if self.food_timer >= 5.0 and self.food_count < 3:
            self.food_count += 1
            self.food_timer = 0.0
        
        # 更新僵尸
        for zombie in self.zombies:
            zombie.update(dt)
            
            # 饿死
            if zombie.hunger >= 100:
                zombie.is_alive = False
        
        # 移除死亡僵尸
        self.zombies = [z for z in self.zombies if z.is_alive]
        
        # 检查游戏结束
        if self.game_time >= self.max_time or len(self.zombies) == 0:
            self.running = False
    
    def render(self, screen: pygame.Surface):
        """渲染游戏画面"""
        # 背景
        screen.fill((0, 50, 100))
        
        # 绘制水族馆边框
        pygame.draw.rect(screen, (139, 69, 19), (20, 80, 860, 500), 10)
        
        # 绘制僵尸
        for zombie in self.zombies:
            zombie.render(screen)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        # 金币
        gold_text = font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (20, 20))
        
        # 食物
        food_text = font.render(f"Food: {self.food_count}", True, (139, 69, 19))
        screen.blit(food_text, (200, 20))
        
        # 僵尸数量
        zombie_text = font.render(f"Zombies: {len(self.zombies)}/{self.max_zombies}", True, (255, 255, 255))
        screen.blit(zombie_text, (350, 20))
        
        # 时间
        time_left = max(0, self.max_time - self.game_time)
        time_text = font.render(f"Time: {int(time_left)}s", True, (255, 255, 255))
        screen.blit(time_text, (600, 20))
        
        # 提示
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("Click hungry zombies to feed, click glowing zombies to collect gold", 
                                     True, (200, 200, 200))
        screen.blit(hint_text, (200, 60))
    
    def handle_click(self, x: int, y: int) -> bool:
        """处理鼠标点击"""
        # 先尝试收集金币
        if self.collect_gold(x, y) > 0:
            return True
        
        # 再尝试喂食
        if self.feed_zombie(x, y):
            return True
        
        return False
