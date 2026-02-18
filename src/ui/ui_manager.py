import pygame
from typing import List, Dict, TYPE_CHECKING
from src.entities.plant import PlantType
from src.entities.plants import (
    Sunflower, Peashooter, Repeater, SnowPea, WallNut, CherryBomb, PotatoMine, Chomper,
    Threepeater, MelonPult, WinterMelon, TallNut, Spikeweed, MagnetShroom, Pumpkin
)

if TYPE_CHECKING:
    from src.core.game_manager import GameManager


PLANT_CARD_INFO = [
    {'type': PlantType.SUNFLOWER, 'name': '向日葵', 'cost': 50, 'key': '1'},
    {'type': PlantType.PEASHOOTER, 'name': '豌豆射手', 'cost': 100, 'key': '2'},
    {'type': PlantType.REPEATER, 'name': '双发射手', 'cost': 200, 'key': '3'},
    {'type': PlantType.SNOW_PEA, 'name': '寒冰射手', 'cost': 175, 'key': '4'},
    {'type': PlantType.WALLNUT, 'name': '坚果墙', 'cost': 50, 'key': '5'},
    {'type': PlantType.CHERRY_BOMB, 'name': '樱桃炸弹', 'cost': 150, 'key': '6'},
    {'type': PlantType.POTATO_MINE, 'name': '土豆地雷', 'cost': 25, 'key': '7'},
    {'type': PlantType.CHOMPER, 'name': '大嘴花', 'cost': 150, 'key': '8'},
    {'type': PlantType.THREEPEATER, 'name': '三线射手', 'cost': 325, 'key': '9'},
    {'type': PlantType.MELON_PULT, 'name': '西瓜投手', 'cost': 300, 'key': '0'},
    {'type': PlantType.WINTER_MELON, 'name': '冰西瓜', 'cost': 500, 'key': 'q'},
    {'type': PlantType.TALL_NUT, 'name': '高坚果', 'cost': 125, 'key': 'w'},
    {'type': PlantType.SPIKEWEED, 'name': '地刺', 'cost': 100, 'key': 'e'},
    {'type': PlantType.MAGNET_SHROOM, 'name': '磁力菇', 'cost': 100, 'key': 'r'},
    {'type': PlantType.PUMPKIN, 'name': '南瓜头', 'cost': 125, 'key': 't'},
]


PLANT_FACTORY = {
    PlantType.SUNFLOWER: Sunflower,
    PlantType.PEASHOOTER: Peashooter,
    PlantType.REPEATER: Repeater,
    PlantType.SNOW_PEA: SnowPea,
    PlantType.WALLNUT: WallNut,
    PlantType.CHERRY_BOMB: CherryBomb,
    PlantType.POTATO_MINE: PotatoMine,
    PlantType.CHOMPER: Chomper,
    PlantType.THREEPEATER: Threepeater,
    PlantType.MELON_PULT: MelonPult,
    PlantType.WINTER_MELON: WinterMelon,
    PlantType.TALL_NUT: TallNut,
    PlantType.SPIKEWEED: Spikeweed,
    PlantType.MAGNET_SHROOM: MagnetShroom,
    PlantType.PUMPKIN: Pumpkin,
}


class UIManager:
    """UI管理器"""
    
    CARD_WIDTH = 60
    CARD_HEIGHT = 80
    CARD_SPACING = 10
    CARD_START_X = 200
    CARD_START_Y = 10
    
    def __init__(self):
        self.selected_plant: PlantType = None
        self.font = None
    
    def init_font(self):
        """初始化字体"""
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
    
    def handle_click(self, x: int, y: int, game_manager: 'GameManager') -> bool:
        """处理点击事件"""
        for i, card_info in enumerate(PLANT_CARD_INFO):
            card_x = self.CARD_START_X + i * (self.CARD_WIDTH + self.CARD_SPACING)
            card_rect = pygame.Rect(card_x, self.CARD_START_Y, self.CARD_WIDTH, self.CARD_HEIGHT)
            
            if card_rect.collidepoint(x, y):
                if game_manager.sun_count >= card_info['cost']:
                    self.selected_plant = card_info['type']
                return True
        
        return False
    
    def create_plant(self, x: float, y: float) -> object:
        """创建选中的植物"""
        if self.selected_plant is None:
            return None
        
        plant_class = PLANT_FACTORY.get(self.selected_plant)
        if plant_class:
            plant = plant_class(x, y)
            self.selected_plant = None
            return plant
        
        return None
    
    def get_selected_plant_cost(self) -> int:
        """获取选中植物的成本"""
        if self.selected_plant is None:
            return 0
        
        for card_info in PLANT_CARD_INFO:
            if card_info['type'] == self.selected_plant:
                return card_info['cost']
        
        return 0
    
    def render(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染UI"""
        self._render_plant_cards(screen, game_manager)
        self._render_sun_counter(screen, game_manager)
        self._render_wave_info(screen, game_manager)
        self._render_selected_plant(screen, game_manager)
    
    def _render_plant_cards(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染植物卡片"""
        for i, card_info in enumerate(PLANT_CARD_INFO):
            card_x = self.CARD_START_X + i * (self.CARD_WIDTH + self.CARD_SPACING)
            card_rect = pygame.Rect(card_x, self.CARD_START_Y, self.CARD_WIDTH, self.CARD_HEIGHT)
            
            can_afford = game_manager.sun_count >= card_info['cost']
            is_selected = self.selected_plant == card_info['type']
            
            if is_selected:
                pygame.draw.rect(screen, (255, 255, 0), card_rect, 3)
            
            if can_afford:
                bg_color = (100, 150, 100)
            else:
                bg_color = (80, 80, 80)
            
            pygame.draw.rect(screen, bg_color, card_rect)
            pygame.draw.rect(screen, (0, 0, 0), card_rect, 2)
            
            plant_colors = {
                PlantType.SUNFLOWER: (255, 255, 0),
                PlantType.PEASHOOTER: (0, 200, 0),
                PlantType.REPEATER: (0, 150, 0),
                PlantType.SNOW_PEA: (135, 206, 250),
                PlantType.WALLNUT: (139, 69, 19),
                PlantType.CHERRY_BOMB: (220, 20, 60),
                PlantType.POTATO_MINE: (160, 82, 45),
                PlantType.CHOMPER: (128, 0, 128),
                PlantType.THREEPEATER: (0, 180, 0),
                PlantType.MELON_PULT: (0, 150, 0),
                PlantType.WINTER_MELON: (100, 150, 200),
                PlantType.TALL_NUT: (160, 120, 80),
                PlantType.SPIKEWEED: (100, 100, 100),
                PlantType.MAGNET_SHROOM: (128, 0, 128),
                PlantType.PUMPKIN: (255, 140, 0),
            }
            
            color = plant_colors.get(card_info['type'], (100, 100, 100))
            pygame.draw.circle(screen, color, 
                             (card_x + self.CARD_WIDTH // 2, 
                              self.CARD_START_Y + 30), 15)
            
            if self.font:
                cost_text = self.font.render(str(card_info['cost']), True, (255, 255, 255))
                screen.blit(cost_text, (card_x + 5, self.CARD_START_Y + 55))
                
                key_text = self.font.render(card_info['key'], True, (200, 200, 200))
                screen.blit(key_text, (card_x + 40, self.CARD_START_Y + 55))
    
    def _render_sun_counter(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染阳光计数器"""
        pygame.draw.rect(screen, (50, 50, 50), (10, 10, 150, 40))
        pygame.draw.rect(screen, (255, 255, 0), (15, 15, 30, 30))
        
        if self.font:
            sun_text = self.font.render(f"{game_manager.sun_count}", True, (255, 255, 0))
            screen.blit(sun_text, (55, 20))
    
    def _render_wave_info(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染波次信息"""
        if game_manager.wave_system:
            info = game_manager.wave_system.get_wave_info()
            
            if self.font:
                wave_text = self.font.render(
                    f"Wave: {info['current_wave']}/{info['total_waves']}", 
                    True, (255, 255, 255)
                )
                screen.blit(wave_text, (750, 20))
    
    def _render_selected_plant(self, screen: pygame.Surface, game_manager: 'GameManager'):
        """渲染选中的植物（跟随鼠标）"""
        if self.selected_plant:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            plant_colors = {
                PlantType.SUNFLOWER: (255, 255, 0),
                PlantType.PEASHOOTER: (0, 200, 0),
                PlantType.REPEATER: (0, 150, 0),
                PlantType.SNOW_PEA: (135, 206, 250),
                PlantType.WALLNUT: (139, 69, 19),
                PlantType.CHERRY_BOMB: (220, 20, 60),
                PlantType.POTATO_MINE: (160, 82, 45),
                PlantType.CHOMPER: (128, 0, 128),
                PlantType.THREEPEATER: (0, 180, 0),
                PlantType.MELON_PULT: (0, 150, 0),
                PlantType.WINTER_MELON: (100, 150, 200),
                PlantType.TALL_NUT: (160, 120, 80),
                PlantType.SPIKEWEED: (100, 100, 100),
                PlantType.MAGNET_SHROOM: (128, 0, 128),
                PlantType.PUMPKIN: (255, 140, 0),
            }
            
            color = plant_colors.get(self.selected_plant, (100, 100, 100))
            pygame.draw.circle(screen, color, (mouse_x, mouse_y), 25, 2)
