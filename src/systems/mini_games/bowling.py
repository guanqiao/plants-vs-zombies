"""
坚果保龄球小游戏

滚动坚果击倒僵尸
"""

import pygame
import random
import math
from typing import List
from dataclasses import dataclass
from .base_game import BaseMiniGame


@dataclass
class BowlingNut:
    """保龄球坚果"""
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 20
    is_active: bool = True
    
    def update(self, dt: float):
        """更新坚果位置"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 边界检查
        if self.x < 0 or self.x > 900:
            self.is_active = False
    
    def render(self, screen: pygame.Surface):
        """渲染坚果"""
        pygame.draw.circle(screen, (139, 69, 19), (int(self.x), int(self.y)), int(self.radius))


@dataclass
class BowlingZombie:
    """保龄球僵尸"""
    x: float
    y: float
    is_alive: bool = True
    
    def update(self, dt: float):
        """更新僵尸"""
        self.x -= 50 * dt  # 向左移动
    
    def render(self, screen: pygame.Surface):
        """渲染僵尸"""
        if self.is_alive:
            pygame.draw.rect(screen, (100, 100, 100), (int(self.x) - 15, int(self.y) - 30, 30, 60))


class WallnutBowling(BaseMiniGame):
    """坚果保龄球小游戏"""
    
    def __init__(self):
        super().__init__()
        self.nuts: List[BowlingNut] = []
        self.zombies: List[BowlingZombie] = []
        self.nuts_remaining = 10
        self.zombies_killed = 0
        self.spawn_timer = 0.0
        self.game_time = 0.0
        self.max_time = 120.0  # 2分钟
    
    def update(self, dt: float):
        """更新游戏状态"""
        self.game_time += dt
        
        # 生成僵尸
        self.spawn_timer += dt
        if self.spawn_timer >= 3.0:
            self._spawn_zombie()
            self.spawn_timer = 0.0
        
        # 更新坚果
        for nut in self.nuts:
            nut.update(dt)
        
        # 更新僵尸
        for zombie in self.zombies:
            zombie.update(dt)
        
        # 碰撞检测
        self._check_collisions()
        
        # 清理不活跃的坚果和僵尸
        self.nuts = [n for n in self.nuts if n.is_active]
        self.zombies = [z for z in self.zombies if z.is_alive and z.x > -50]
        
        # 检查游戏结束
        if self.game_time >= self.max_time or self.nuts_remaining == 0:
            self.running = False
    
    def _spawn_zombie(self):
        """生成僵尸"""
        y = random.randint(100, 500)
        self.zombies.append(BowlingZombie(900, y))
    
    def _check_collisions(self):
        """检测碰撞"""
        for nut in self.nuts:
            if not nut.is_active:
                continue
            
            for zombie in self.zombies:
                if not zombie.is_alive:
                    continue
                
                # 简单的圆形碰撞检测
                dx = nut.x - zombie.x
                dy = nut.y - zombie.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < nut.radius + 20:
                    zombie.is_alive = False
                    self.zombies_killed += 1
                    self.score += 100
    
    def render(self, screen: pygame.Surface):
        """渲染游戏画面"""
        screen.fill((100, 150, 100))
        
        # 绘制车道
        for i in range(5):
            y = 100 + i * 100
            pygame.draw.line(screen, (150, 200, 150), (0, y), (900, y), 2)
        
        # 绘制坚果
        for nut in self.nuts:
            nut.render(screen)
        
        # 绘制僵尸
        for zombie in self.zombies:
            zombie.render(screen)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        nuts_text = font.render(f"Nuts: {self.nuts_remaining}", True, (139, 69, 19))
        screen.blit(nuts_text, (20, 20))
        
        killed_text = font.render(f"Killed: {self.zombies_killed}", True, (255, 255, 255))
        screen.blit(killed_text, (200, 20))
        
        time_left = max(0, self.max_time - self.game_time)
        time_text = font.render(f"Time: {int(time_left)}s", True, (255, 255, 255))
        screen.blit(time_text, (400, 20))
    
    def handle_click(self, x: int, y: int) -> bool:
        """处理鼠标点击"""
        if self.nuts_remaining > 0:
            # 在左侧发射坚果
            nut = BowlingNut(50, y, 300, 0)
            self.nuts.append(nut)
            self.nuts_remaining -= 1
            return True
        
        return False
