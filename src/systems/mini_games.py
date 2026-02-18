import pygame
import random
import math
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


class MiniGameType(Enum):
    """小游戏类型枚举"""
    ZOMBIE_AQUARIUM = auto()
    BEGHOULED = auto()
    WALLNUT_BOWLING = auto()


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


class ZombieAquarium:
    """僵尸水族馆小游戏"""
    
    def __init__(self):
        self.zombies: List[AquariumZombie] = []
        self.food_count = 3
        self.food_timer = 0.0
        self.gold = 0
        self.max_zombies = 10
        self.game_time = 0.0
        self.max_time = 180.0  # 3分钟
        self.running = True
        
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
                return zombie.collect_gold()
        
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


class BeghouledGame:
    """宝石迷阵小游戏"""
    
    GRID_ROWS = 8
    GRID_COLS = 8
    CELL_SIZE = 60
    GRID_OFFSET_X = 210
    GRID_OFFSET_Y = 60
    
    COLORS = [
        (255, 0, 0),    # 红色 - 樱桃炸弹
        (0, 255, 0),    # 绿色 - 豌豆射手
        (0, 0, 255),    # 蓝色 - 寒冰射手
        (255, 255, 0),  # 黄色 - 向日葵
        (128, 0, 128),  # 紫色 - 大嘴花
        (255, 140, 0),  # 橙色 - 坚果墙
    ]
    
    def __init__(self):
        self.grid: List[List[int]] = []
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.score = 0
        self.matches = 0
        self.target_matches = 75
        self.running = True
        self.animation_cells: List[Tuple[int, int, float]] = []
        
        self._init_grid()
    
    def _init_grid(self):
        """初始化网格"""
        self.grid = []
        for row in range(self.GRID_ROWS):
            grid_row = []
            for col in range(self.GRID_COLS):
                grid_row.append(random.randint(0, len(self.COLORS) - 1))
            self.grid.append(grid_row)
        
        # 确保没有初始匹配
        while self._find_matches():
            self._init_grid()
    
    def _get_cell_from_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """从屏幕坐标获取网格单元"""
        col = (x - self.GRID_OFFSET_X) // self.CELL_SIZE
        row = (y - self.GRID_OFFSET_Y) // self.CELL_SIZE
        
        if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
            return (row, col)
        
        return None
    
    def _find_matches(self) -> List[Tuple[int, int]]:
        """查找匹配的单元格"""
        matches = set()
        
        # 水平匹配
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS - 2):
                color = self.grid[row][col]
                if color == self.grid[row][col + 1] == self.grid[row][col + 2]:
                    matches.add((row, col))
                    matches.add((row, col + 1))
                    matches.add((row, col + 2))
        
        # 垂直匹配
        for row in range(self.GRID_ROWS - 2):
            for col in range(self.GRID_COLS):
                color = self.grid[row][col]
                if color == self.grid[row + 1][col] == self.grid[row + 2][col]:
                    matches.add((row, col))
                    matches.add((row + 1, col))
                    matches.add((row + 2, col))
        
        return list(matches)
    
    def _remove_matches(self, matches: List[Tuple[int, int]]):
        """移除匹配的单元格"""
        for row, col in matches:
            self.grid[row][col] = -1
            self.animation_cells.append((row, col, 0.5))
        
        self.matches += len(matches)
        self.score += len(matches) * 10
    
    def _drop_cells(self):
        """让单元格下落"""
        for col in range(self.GRID_COLS):
            # 收集非空单元格
            column = []
            for row in range(self.GRID_ROWS):
                if self.grid[row][col] != -1:
                    column.append(self.grid[row][col])
            
            # 填充新单元格
            while len(column) < self.GRID_ROWS:
                column.insert(0, random.randint(0, len(self.COLORS) - 1))
            
            # 写回网格
            for row in range(self.GRID_ROWS):
                self.grid[row][col] = column[row]
    
    def handle_click(self, x: int, y: int) -> bool:
        """处理点击事件"""
        cell = self._get_cell_from_pos(x, y)
        if not cell:
            return False
        
        if self.selected_cell is None:
            self.selected_cell = cell
            return True
        
        # 检查是否相邻
        row1, col1 = self.selected_cell
        row2, col2 = cell
        
        if abs(row1 - row2) + abs(col1 - col2) == 1:
            # 交换
            self.grid[row1][col1], self.grid[row2][col2] = \
                self.grid[row2][col2], self.grid[row1][col1]
            
            # 检查是否有匹配
            matches = self._find_matches()
            if matches:
                self._remove_matches(matches)
            else:
                # 没有匹配，交换回来
                self.grid[row1][col1], self.grid[row2][col2] = \
                    self.grid[row2][col2], self.grid[row1][col1]
        
        self.selected_cell = None
        return True
    
    def update(self, dt: float):
        """更新游戏状态"""
        # 更新动画
        for i in range(len(self.animation_cells) - 1, -1, -1):
            row, col, timer = self.animation_cells[i]
            timer -= dt
            if timer <= 0:
                self.animation_cells.pop(i)
            else:
                self.animation_cells[i] = (row, col, timer)
        
        # 检查并处理匹配
        if not self.animation_cells:
            matches = self._find_matches()
            if matches:
                self._remove_matches(matches)
                self._drop_cells()
        
        # 检查游戏结束
        if self.matches >= self.target_matches:
            self.running = False
    
    def render(self, screen: pygame.Surface):
        """渲染游戏画面"""
        screen.fill((50, 50, 50))
        
        # 绘制网格
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                x = self.GRID_OFFSET_X + col * self.CELL_SIZE
                y = self.GRID_OFFSET_Y + row * self.CELL_SIZE
                
                # 绘制单元格背景
                rect = pygame.Rect(x, y, self.CELL_SIZE - 2, self.CELL_SIZE - 2)
                
                # 选中高亮
                if self.selected_cell == (row, col):
                    pygame.draw.rect(screen, (255, 255, 0), rect.inflate(4, 4))
                
                # 绘制宝石
                color_idx = self.grid[row][col]
                if color_idx >= 0:
                    color = self.COLORS[color_idx]
                    
                    # 动画效果
                    for anim_row, anim_col, timer in self.animation_cells:
                        if anim_row == row and anim_col == col:
                            alpha = int(255 * timer / 0.5)
                            color = tuple(min(255, c + 50) for c in color)
                    
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        # 分数
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        # 匹配数
        matches_text = font.render(f"Matches: {self.matches}/{self.target_matches}", True, (255, 255, 255))
        screen.blit(matches_text, (20, 60))
        
        # 提示
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("Swap adjacent gems to make 3+ matches", True, (200, 200, 200))
        screen.blit(hint_text, (250, 20))


class WallnutBowling:
    """坚果保龄球小游戏"""
    
    def __init__(self):
        self.wallnuts: List[Dict] = []
        self.zombies: List[Dict] = []
        self.score = 0
        self.wallnuts_left = 10
        self.zombies_spawned = 0
        self.zombies_to_spawn = 20
        self.spawn_timer = 0.0
        self.spawn_interval = 3.0
        self.running = True
        self.game_over = False
        
    def launch_wallnut(self, row: int):
        """发射坚果"""
        if self.wallnuts_left > 0:
            self.wallnuts.append({
                'x': 100,
                'y': 100 + row * 100 + 50,
                'row': row,
                'vx': 300,
                'vy': 0,
                'radius': 25,
                'bounces': 0
            })
            self.wallnuts_left -= 1
    
    def _spawn_zombie(self):
        """生成僵尸"""
        if self.zombies_spawned < self.zombies_to_spawn:
            row = random.randint(0, 4)
            self.zombies.append({
                'x': 900,
                'y': 100 + row * 100 + 50,
                'row': row,
                'vx': -40,
                'health': 100,
                'radius': 25
            })
            self.zombies_spawned += 1
    
    def update(self, dt: float):
        """更新游戏状态"""
        # 生成僵尸
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self._spawn_zombie()
            self.spawn_timer = 0.0
        
        # 更新坚果
        for wallnut in self.wallnuts[:]:
            wallnut['x'] += wallnut['vx'] * dt
            wallnut['y'] += wallnut['vy'] * dt
            
            # 边界反弹
            if wallnut['y'] < 100 or wallnut['y'] > 550:
                wallnut['vy'] *= -0.8
                wallnut['y'] = max(100, min(550, wallnut['y']))
            
            # 移除超出屏幕的坚果
            if wallnut['x'] > 950:
                self.wallnuts.remove(wallnut)
        
        # 更新僵尸
        for zombie in self.zombies[:]:
            zombie['x'] += zombie['vx'] * dt
            
            # 检查与坚果碰撞
            for wallnut in self.wallnuts:
                dist = math.sqrt((wallnut['x'] - zombie['x'])**2 + 
                               (wallnut['y'] - zombie['y'])**2)
                if dist < wallnut['radius'] + zombie['radius']:
                    # 碰撞
                    zombie['health'] -= 50
                    wallnut['vx'] *= 0.9
                    wallnut['vy'] += random.uniform(-100, 100)
                    wallnut['bounces'] += 1
                    
                    if wallnut['bounces'] >= 3:
                        if wallnut in self.wallnuts:
                            self.wallnuts.remove(wallnut)
            
            # 移除死亡僵尸
            if zombie['health'] <= 0:
                self.zombies.remove(zombie)
                self.score += 10
            elif zombie['x'] < 0:
                # 僵尸到达左侧，游戏结束
                self.game_over = True
                self.running = False
        
        # 检查胜利条件
        if self.zombies_spawned >= self.zombies_to_spawn and len(self.zombies) == 0:
            self.running = False
    
    def render(self, screen: pygame.Surface):
        """渲染游戏画面"""
        screen.fill((0, 100, 0))
        
        # 绘制草坪
        for row in range(5):
            y = 100 + row * 100
            color = (34, 139, 34) if row % 2 == 0 else (0, 128, 0)
            pygame.draw.rect(screen, color, (0, y, 900, 100))
        
        # 绘制坚果
        for wallnut in self.wallnuts:
            pygame.draw.circle(screen, (139, 69, 19), 
                             (int(wallnut['x']), int(wallnut['y'])), 
                             wallnut['radius'])
            # 眼睛
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(wallnut['x'] - 8), int(wallnut['y'] - 5)), 3)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (int(wallnut['x'] + 8), int(wallnut['y'] - 5)), 3)
        
        # 绘制僵尸
        for zombie in self.zombies:
            pygame.draw.rect(screen, (128, 128, 128), 
                           (int(zombie['x'] - 20), int(zombie['y'] - 30), 40, 60))
            # 眼睛
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(zombie['x'] - 8), int(zombie['y'] - 15)), 4)
            pygame.draw.circle(screen, (255, 0, 0), 
                             (int(zombie['x'] + 8), int(zombie['y'] - 15)), 4)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        # 分数
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
        
        # 剩余坚果
        wallnut_text = font.render(f"Wallnuts: {self.wallnuts_left}", True, (139, 69, 19))
        screen.blit(wallnut_text, (200, 20))
        
        # 僵尸进度
        zombie_text = font.render(f"Zombies: {self.zombies_spawned}/{self.zombies_to_spawn}", True, (255, 255, 255))
        screen.blit(zombie_text, (400, 20))
        
        # 提示
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_text = hint_font.render("Click a row to launch wallnut!", True, (200, 200, 200))
        screen.blit(hint_text, (300, 580))
        
        # 行号
        for row in range(5):
            row_text = font.render(str(row + 1), True, (255, 255, 255))
            screen.blit(row_text, (50, 100 + row * 100 + 40))


class MiniGameManager:
    """小游戏管理器"""
    
    def __init__(self):
        self.current_game = None
        self.game_type = None
        self.available_games = {
            MiniGameType.ZOMBIE_AQUARIUM: ZombieAquarium,
            MiniGameType.BEGHOULED: BeghouledGame,
            MiniGameType.WALLNUT_BOWLING: WallnutBowling,
        }
    
    def start_game(self, game_type: MiniGameType):
        """开始小游戏"""
        self.game_type = game_type
        game_class = self.available_games.get(game_type)
        if game_class:
            self.current_game = game_class()
    
    def update(self, dt: float):
        """更新当前游戏"""
        if self.current_game:
            self.current_game.update(dt)
    
    def render(self, screen: pygame.Surface):
        """渲染当前游戏"""
        if self.current_game:
            self.current_game.render(screen)
    
    def handle_click(self, x: int, y: int):
        """处理点击事件"""
        if not self.current_game:
            return
        
        if self.game_type == MiniGameType.ZOMBIE_AQUARIUM:
            # 先尝试收集金币
            gold = self.current_game.collect_gold(x, y)
            if gold > 0:
                self.current_game.gold += gold
                return
            
            # 再尝试喂食
            self.current_game.feed_zombie(x, y)
            
        elif self.game_type == MiniGameType.BEGHOULED:
            self.current_game.handle_click(x, y)
            
        elif self.game_type == MiniGameType.WALLNUT_BOWLING:
            # 根据Y坐标确定行
            for row in range(5):
                row_y = 100 + row * 100
                if row_y <= y < row_y + 100:
                    self.current_game.launch_wallnut(row)
                    break
    
    def is_game_running(self) -> bool:
        """检查游戏是否在进行中"""
        return self.current_game is not None and self.current_game.running
    
    def get_score(self) -> int:
        """获取当前分数"""
        if self.current_game:
            return getattr(self.current_game, 'score', 0)
        return 0
