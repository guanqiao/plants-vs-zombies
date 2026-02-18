import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


class Renderer:
    """渲染器"""
    
    def __init__(self):
        self.font = None
    
    def init(self):
        """初始化渲染器"""
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
    
    def render_menu(self, screen: pygame.Surface):
        """渲染菜单"""
        screen.fill((34, 139, 34))
        
        title = self.title_font.render("Plants vs Zombies", True, (255, 255, 255))
        title_rect = title.get_rect(center=(450, 200))
        screen.blit(title, title_rect)
        
        start_text = self.font.render("Press SPACE to Start", True, (255, 255, 0))
        start_rect = start_text.get_rect(center=(450, 350))
        screen.blit(start_text, start_rect)
        
        level_text = self.font.render("Press 1-5 to Select Level", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(450, 400))
        screen.blit(level_text, level_rect)
    
    def render_game_over(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染游戏结束画面"""
        overlay = pygame.Surface((900, 600))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        game_over_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(450, 250))
        screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font.render(f"Score: {game_manager.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(450, 320))
        screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press R to Restart", True, (255, 255, 0))
        restart_rect = restart_text.get_rect(center=(450, 400))
        screen.blit(restart_text, restart_rect)
    
    def render_victory(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染胜利画面"""
        overlay = pygame.Surface((900, 600))
        overlay.fill((0, 100, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        victory_text = self.title_font.render("VICTORY!", True, (255, 255, 0))
        victory_rect = victory_text.get_rect(center=(450, 250))
        screen.blit(victory_text, victory_rect)
        
        score_text = self.font.render(f"Score: {game_manager.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(450, 320))
        screen.blit(score_text, score_rect)
        
        next_text = self.font.render("Press SPACE for Next Level or R to Restart", True, (255, 255, 0))
        next_rect = next_text.get_rect(center=(450, 400))
        screen.blit(next_text, next_rect)
    
    def render_paused(self, screen: pygame.Surface):
        """渲染暂停画面"""
        overlay = pygame.Surface((900, 600))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        paused_text = self.title_font.render("PAUSED", True, (255, 255, 255))
        paused_rect = paused_text.get_rect(center=(450, 280))
        screen.blit(paused_text, paused_rect)
        
        resume_text = self.font.render("Press ESC to Resume", True, (255, 255, 0))
        resume_rect = resume_text.get_rect(center=(450, 350))
        screen.blit(resume_text, resume_rect)
