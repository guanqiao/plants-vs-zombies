import pygame
import sys
from typing import List, Optional
from src.core.game_state import GameState, GameStateType
from src.core.grid import Grid
from src.core.sun_system import SunSystem
from src.entities.plant import Plant
from src.entities.zombie import Zombie
from src.entities.projectile import Projectile
from src.systems.collision_system import CollisionSystem
from src.systems.wave_system import WaveSystem
from src.systems.particle_system import ParticleSystem
from src.systems.sound_manager import SoundManager
from src.ui.renderer import Renderer
from src.ui.ui_manager import UIManager


class GameManager:
    """游戏管理器 - 管理游戏主循环和所有游戏对象"""
    
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 600
    FPS = 60
    
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("植物大战僵尸")
        
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.sun_count = 50
        
        self.game_state = GameState()
        self.grid: Optional[Grid] = None
        self.sun_system: Optional[SunSystem] = None
        self.collision_system: Optional[CollisionSystem] = None
        self.wave_system: Optional[WaveSystem] = None
        self.particle_system: Optional[ParticleSystem] = None
        self.sound_manager: Optional[SoundManager] = None
        
        self.renderer = Renderer()
        self.ui_manager = UIManager()
        
        self.plants: List[Plant] = []
        self.zombies: List[Zombie] = []
        self.projectiles: List[Projectile] = []
        
        self.current_level = 1
        self.score = 0
    
    def start_game(self, level: int = 1):
        """开始新游戏"""
        self.current_level = level
        self.sun_count = 50
        self.score = 0
        
        self.grid = Grid()
        self.sun_system = SunSystem()
        self.collision_system = CollisionSystem()
        self.wave_system = WaveSystem(level)
        self.particle_system = ParticleSystem()
        self.sound_manager = SoundManager()
        self.sound_manager.preload_game_sounds()
        
        self.plants.clear()
        self.zombies.clear()
        self.projectiles.clear()
        
        self.game_state.change_state(GameStateType.PLAYING)
    
    def add_sun(self, amount: int):
        """添加阳光"""
        self.sun_count += amount
    
    def spend_sun(self, amount: int) -> bool:
        """消耗阳光，返回是否成功"""
        if self.sun_count >= amount:
            self.sun_count -= amount
            return True
        return False
    
    def add_plant(self, plant: Plant):
        """添加植物"""
        self.plants.append(plant)
    
    def remove_plant(self, plant: Plant):
        """移除植物"""
        if plant in self.plants:
            self.plants.remove(plant)
    
    def add_zombie(self, zombie: Zombie):
        """添加僵尸"""
        self.zombies.append(zombie)
    
    def remove_zombie(self, zombie: Zombie):
        """移除僵尸"""
        if zombie in self.zombies:
            self.zombies.remove(zombie)
            self.score += zombie.score_value
            
            # 播放死亡音效和粒子效果
            if self.sound_manager:
                self.sound_manager.play_sound('zombie_die')
            if self.particle_system:
                self.particle_system.create_death_effect(zombie.x, zombie.y, zombie.color)
    
    def add_projectile(self, projectile: Projectile):
        """添加投射物"""
        self.projectiles.append(projectile)
    
    def remove_projectile(self, projectile: Projectile):
        """移除投射物"""
        if projectile in self.projectiles:
            self.projectiles.remove(projectile)
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event)
    
    def _handle_keydown(self, event):
        """处理键盘按下事件"""
        if event.key == pygame.K_ESCAPE:
            if self.game_state.is_playing():
                self.game_state.change_state(GameStateType.PAUSED)
            elif self.game_state.is_paused():
                self.game_state.change_state(GameStateType.PLAYING)
        
        if event.key == pygame.K_r:
            self.reset()
    
    def _handle_mouse_click(self, event):
        """处理鼠标点击事件"""
        pass
    
    def update(self, dt: float):
        """更新游戏状态"""
        if not self.game_state.is_playing():
            return
        
        if self.sun_system:
            self.sun_system.update(dt, self)
        
        if self.particle_system:
            self.particle_system.update(dt)
        
        for plant in self.plants[:]:
            plant.update(dt, self)
        
        for zombie in self.zombies[:]:
            zombie.update(dt, self)
        
        for projectile in self.projectiles[:]:
            projectile.update(dt, self)
        
        if self.collision_system:
            self.collision_system.check_collisions(self)
        
        if self.wave_system:
            self.wave_system.update(dt, self)
        
        self._check_game_over()
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        for zombie in self.zombies:
            if zombie.x <= 0:
                self.game_state.change_state(GameStateType.GAME_OVER)
                return
        
        if self.wave_system and self.wave_system.is_complete() and len(self.zombies) == 0:
            self.game_state.change_state(GameStateType.VICTORY)
    
    def render(self):
        """渲染游戏画面"""
        self.screen.fill((0, 100, 0))
        
        if self.grid:
            self.grid.render(self.screen)
        
        for plant in self.plants:
            plant.render(self.screen)
        
        for zombie in self.zombies:
            zombie.render(self.screen)
        
        for projectile in self.projectiles:
            projectile.render(self.screen)
        
        if self.particle_system:
            self.particle_system.render(self.screen)
        
        if self.sun_system:
            self.sun_system.render(self.screen)
        
        self._render_ui()
        
        pygame.display.flip()
    
    def _render_ui(self):
        """渲染UI"""
        font = pygame.font.Font(None, 36)
        sun_text = font.render(f"Sun: {self.sun_count}", True, (255, 255, 0))
        self.screen.blit(sun_text, (10, 10))
        
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 50))
    
    def reset(self):
        """重置游戏"""
        self.sun_count = 50
        self.score = 0
        self.game_state.change_state(GameStateType.MENU)
        self.plants.clear()
        self.zombies.clear()
        self.projectiles.clear()
    
    def quit(self):
        """退出游戏"""
        self.running = False
        pygame.quit()
        sys.exit()
    
    def run(self):
        """游戏主循环"""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
