"""
游戏窗口 - 使用Arcade引擎的主窗口
"""

import arcade
from ..ecs import World
from ..ecs.systems import (
    RenderSystem, MovementSystem, CollisionSystem,
    HealthSystem, SunSystem, WaveSystem,
    PlantBehaviorSystem, ProjectileSystem, ZombieBehaviorSystem
)
from .entity_factory import EntityFactory
from .planting_system import PlantingSystem


class GameWindow(arcade.Window):
    """
    游戏主窗口
    
    使用Arcade引擎和ECS架构
    """
    
    SCREEN_WIDTH = 900
    SCREEN_HEIGHT = 600
    SCREEN_TITLE = "植物大战僵尸 - Arcade ECS"
    BACKGROUND_COLOR = (34, 139, 34)
    
    def __init__(self):
        super().__init__(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.SCREEN_TITLE
        )
        
        # 创建ECS世界
        self.world = World()
        
        # 初始化系统
        self._init_systems()
        
        # 创建实体工厂
        self.entity_factory = EntityFactory(self.world)
        
        # 创建种植系统
        self.planting_system = PlantingSystem(self.world, self.entity_factory)
        
        # 游戏状态
        self.sun_count = 50
        self.score = 0
        self.current_level = 1
        self.game_over = False
        self.victory = False
        
        # 设置背景色
        arcade.set_background_color(self.BACKGROUND_COLOR)
    
    def _init_systems(self):
        """初始化所有ECS系统"""
        # 渲染系统（优先级最低，最后执行）
        self.render_system = RenderSystem(priority=100)
        self.world.add_system(self.render_system)
        
        # 移动系统
        self.movement_system = MovementSystem(priority=10)
        self.world.add_system(self.movement_system)
        
        # 碰撞系统
        self.collision_system = CollisionSystem(priority=20)
        self.world.add_system(self.collision_system)
        
        # 生命值系统
        self.health_system = HealthSystem(priority=30)
        self.world.add_system(self.health_system)
        
        # 投射物系统
        self.projectile_system = ProjectileSystem(self.world._entity_manager, priority=35)
        self.world.add_system(self.projectile_system)
        
        # 植物行为系统
        self.plant_behavior_system = PlantBehaviorSystem(self.entity_factory, priority=40)
        self.world.add_system(self.plant_behavior_system)
        
        # 僵尸行为系统
        self.zombie_behavior_system = ZombieBehaviorSystem(priority=45)
        self.world.add_system(self.zombie_behavior_system)
        
        # 阳光系统
        self.sun_system = SunSystem(priority=50)
        self.world.add_system(self.sun_system)
        
        # 波次系统
        self.wave_system = WaveSystem(self.current_level, priority=60)
        self.world.add_system(self.wave_system)
    
    def on_update(self, delta_time: float):
        """更新游戏状态"""
        if self.game_over or self.victory:
            return
        
        # 更新ECS世界
        self.world.update(delta_time)
        
        # 更新种植系统
        self.planting_system.update(delta_time, self.sun_count)
        
        # 检查游戏结束条件
        self._check_game_over()
    
    def on_draw(self):
        """渲染游戏画面"""
        self.clear()
        
        # 渲染网格（可选）
        self._draw_grid()
        
        # 渲染所有实体
        self.render_system.render(self.world._component_manager)
        
        # 渲染UI
        self._draw_ui()
        
        # 渲染种植系统
        self.planting_system.render()
        
        # 渲染游戏结束/胜利画面
        if self.game_over:
            self._draw_game_over()
        elif self.victory:
            self._draw_victory()
    
    def _draw_grid(self):
        """绘制草坪网格"""
        # 5行9列的网格
        rows = 5
        cols = 9
        cell_width = 80
        cell_height = 100
        start_x = 100
        start_y = 50
        
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * cell_width
                y = start_y + row * cell_height
                
                # 绘制网格单元
                arcade.draw_lrtb_rectangle_outline(
                    x, x + cell_width,
                    y + cell_height, y,
                    (0, 100, 0), 1
                )
    
    def _draw_ui(self):
        """绘制UI界面"""
        # 阳光计数
        arcade.draw_text(
            f"阳光: {self.sun_count}",
            10, self.SCREEN_HEIGHT - 30,
            arcade.color.YELLOW, 20
        )
        
        # 分数
        arcade.draw_text(
            f"分数: {self.score}",
            10, self.SCREEN_HEIGHT - 60,
            arcade.color.WHITE, 20
        )
        
        # 波次信息
        wave_info = self.wave_system.get_wave_info()
        arcade.draw_text(
            wave_info,
            self.SCREEN_WIDTH - 200, self.SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 16
        )
    
    def _draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明背景
        arcade.draw_lrtb_rectangle_filled(
            0, self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT, 0,
            (0, 0, 0, 180)
        )
        
        arcade.draw_text(
            "游戏结束",
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 50,
            arcade.color.RED, 48,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "按 R 返回菜单",
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )
    
    def _draw_victory(self):
        """绘制胜利画面"""
        # 半透明背景
        arcade.draw_lrtb_rectangle_filled(
            0, self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT, 0,
            (0, 0, 0, 180)
        )
        
        arcade.draw_text(
            "胜利！",
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 50,
            arcade.color.GOLD, 48,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"最终得分: {self.score}",
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "按空格键继续下一关",
            self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50,
            arcade.color.WHITE, 24,
            anchor_x="center"
        )
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有僵尸到达最左侧
        from ..ecs.components import TransformComponent, ZombieComponent
        
        zombies = self.world.query_entities(TransformComponent, ZombieComponent)
        for entity_id in zombies:
            transform = self.world.get_component(entity_id, TransformComponent)
            if transform and transform.x <= 0:
                self.game_over = True
                return
        
        # 检查是否完成所有波次且没有僵尸
        if self.wave_system.is_complete() and len(zombies) == 0:
            self.victory = True
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键"""
        if key == arcade.key.ESCAPE:
            # 暂停/恢复游戏
            pass
        elif key == arcade.key.R:
            # 重置游戏
            if self.game_over:
                self.reset_game()
        elif key == arcade.key.SPACE:
            # 下一关
            if self.victory:
                self.next_level()
    
    def on_mouse_press(self, x, y, button, modifiers):
        """处理鼠标点击"""
        if self.game_over or self.victory:
            return
        
        # 处理种植
        if self.planting_system.handle_mouse_press(x, y, self.sun_count):
            # 消耗阳光
            cost = self.planting_system.get_planting_cost()
            if cost > 0:
                self.spend_sun(cost)
            return
    
    def reset_game(self):
        """重置游戏"""
        self.world.clear()
        self.planting_system.clear()
        self.sun_count = 50
        self.score = 0
        self.game_over = False
        self.victory = False
        self._init_systems()
    
    def next_level(self):
        """进入下一关"""
        self.current_level += 1
        self.reset_game()
    
    def add_sun(self, amount: int):
        """添加阳光"""
        self.sun_count += amount
    
    def spend_sun(self, amount: int) -> bool:
        """消耗阳光"""
        if self.sun_count >= amount:
            self.sun_count -= amount
            return True
        return False
    
    def add_score(self, points: int):
        """添加分数"""
        self.score += points