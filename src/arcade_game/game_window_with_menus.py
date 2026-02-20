"""
游戏窗口（带菜单系统集成）- 使用Arcade引擎的主窗口

集成了菜单系统和游戏状态管理器
"""

import arcade
from ..ecs import World
from ..ecs.systems import (
    RenderSystem, MovementSystem, CollisionSystem,
    HealthSystem, SunSystem, WaveSystem,
    PlantBehaviorSystem, ProjectileSystem, ZombieBehaviorSystem
)
from ..ecs.components import (
    TransformComponent, HealthComponent, ZombieComponent,
    PlantComponent, GridPositionComponent
)
from ..core.event_bus import EventBus, Event, EventType
from ..core.game_state import GameStateManager, GameState
from ..core.game_constants import EASY, NORMAL, HARD
from ..ui.menu_system import MenuSystem
from .entity_factory import EntityFactory
from .planting_system import PlantingSystem
from .zombie_spawner import ZombieSpawner
from .sun_collection_system import SunCollectionSystem
from .audio_manager import get_audio_manager
from .particle_system import ParticleSystem
from .background_renderer import BackgroundRenderer
from .health_bar_system import HealthBarSystem
from .damage_number_system import DamageNumberSystem
from .screen_shake import ScreenShake
from .ui_renderer import UIRenderer
from .visual_effects import VisualEffectsSystem


class GameWindowWithMenus(arcade.Window):
    """
    游戏主窗口（带菜单系统集成）
    
    使用Arcade引擎和ECS架构，集成菜单系统和游戏状态管理
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
        
        # 游戏状态管理器
        self.game_state = GameStateManager()
        self._setup_game_state_callbacks()
        
        # 音效管理器（尽早初始化）
        self.audio_manager = get_audio_manager()
        
        # 菜单系统
        self.menu_system = MenuSystem(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self._setup_menu_callbacks()
        self.menu_system.setup()
        
        # 游戏数据
        self.sun_count = 50
        self.score = 0
        self.current_level = 1
        
        # 初始化游戏组件（延迟到实际开始游戏时）
        self.world = None
        self.entity_factory = None
        self.planting_system = None
        self.zombie_spawner = None
        self.sun_collection_system = None
        self.particle_system = None
        self.health_bar_system = None
        self.damage_number_system = None
        self.screen_shake = None
        self.ui_renderer = None
        self.visual_effects = None
        self.background_renderer = None
        self.event_bus = None
        
        # 显示主菜单
        self.menu_system.show_main_menu()
        
        arcade.set_background_color(self.BACKGROUND_COLOR)
        
        self._mouse_x = 0
        self._mouse_y = 0
    
    def _setup_game_state_callbacks(self):
        """设置游戏状态回调"""
        self.game_state.on_state_change = self._on_state_change
        self.game_state.on_start_game = self._on_start_game
        self.game_state.on_pause = self._on_pause
        self.game_state.on_resume = self._on_resume
        self.game_state.on_restart = self._on_restart
        self.game_state.on_quit = self._on_quit
    
    def _setup_menu_callbacks(self):
        """设置菜单回调"""
        self.menu_system.on_start_game = self._on_menu_start_game
        self.menu_system.on_level_select = self._on_menu_level_select
        self.menu_system.on_settings = self._on_menu_settings
        self.menu_system.on_quit = self._on_menu_quit
        self.menu_system.on_resume = self._on_menu_resume
        self.menu_system.on_restart = self._on_menu_restart
        self.menu_system.on_main_menu = self._on_menu_main_menu
        self.menu_system.on_difficulty_selected = self._on_difficulty_selected
        
        # 音量回调
        self.menu_system.on_master_volume_change = self._on_master_volume_change
        self.menu_system.on_sfx_volume_change = self._on_sfx_volume_change
        self.menu_system.on_music_volume_change = self._on_music_volume_change
    
    def _init_game_components(self, level: int = 1, difficulty: str = "normal"):
        """初始化游戏组件"""
        self.current_level = level
        self.current_difficulty = difficulty
        
        # 根据难度获取配置
        difficulty_config = self._get_difficulty_config(difficulty)
        
        # 创建ECS世界
        self.world = World()
        
        # 创建事件总线
        self.event_bus = EventBus()
        
        # 创建实体工厂
        self.entity_factory = EntityFactory(self.world)
        
        # 初始化系统
        self._init_systems()
        
        # 创建种植系统
        self.planting_system = PlantingSystem(self.world, self.entity_factory)
        
        # 创建僵尸生成器
        self.zombie_spawner = ZombieSpawner(self.world, self.entity_factory)
        self.zombie_spawner.set_level(self.current_level)
        self.zombie_spawner.set_difficulty(
            difficulty_config.zombie_speed_multiplier,
            difficulty_config.zombie_health_multiplier,
            difficulty_config.zombie_spawn_rate_multiplier
        )
        
        # 创建阳光收集系统
        self.sun_collection_system = SunCollectionSystem(self.world, self.entity_factory)
        self.sun_collection_system.register_collection_callback(self._on_sun_collected)
        # 设置难度相关配置
        self.sun_collection_system.set_difficulty_config(
            difficulty_config.auto_sun_spawn_interval,
            difficulty_config.sun_value
        )
        
        # 创建粒子系统
        self.particle_system = ParticleSystem()
        
        # 创建血条系统
        self.health_bar_system = HealthBarSystem()
        
        # 创建伤害数字系统
        self.damage_number_system = DamageNumberSystem()
        
        # 创建屏幕震动效果
        self.screen_shake = ScreenShake()
        
        # 创建UI渲染器
        self.ui_renderer = UIRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 创建视觉特效系统
        self.visual_effects = VisualEffectsSystem()
        
        # 创建背景渲染器
        self.background_renderer = BackgroundRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 注册僵尸死亡回调
        self.zombie_behavior_system.register_death_callback(self._on_zombie_death)
        
        # 重置游戏数据（根据难度设置初始阳光）
        self.sun_count = difficulty_config.initial_sun
        self.score = 0
    
    def _get_difficulty_config(self, difficulty: str):
        """获取难度配置"""
        if difficulty == "easy":
            return EASY
        elif difficulty == "hard":
            return HARD
        else:
            return NORMAL
    
    def _init_systems(self):
        """初始化所有ECS系统"""
        self.render_system = RenderSystem(priority=100)
        self.world.add_system(self.render_system)
        
        self.movement_system = MovementSystem(priority=10)
        self.world.add_system(self.movement_system)
        
        self.collision_system = CollisionSystem(priority=20)
        self.world.add_system(self.collision_system)
        
        self.health_system = HealthSystem(priority=30)
        self.world.add_system(self.health_system)
        
        self.projectile_system = ProjectileSystem(
            self.world._entity_manager,
            self.event_bus,
            priority=35
        )
        self.world.add_system(self.projectile_system)
        
        self.plant_behavior_system = PlantBehaviorSystem(
            self.entity_factory,
            self.event_bus,
            priority=40
        )
        self.world.add_system(self.plant_behavior_system)
        
        self.zombie_behavior_system = ZombieBehaviorSystem(priority=45)
        self.world.add_system(self.zombie_behavior_system)
        
        self.sun_system = SunSystem(priority=50)
        self.world.add_system(self.sun_system)
        
        self.wave_system = WaveSystem(self.current_level, priority=60)
        self.world.add_system(self.wave_system)
    
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)
        self.event_bus.subscribe(EventType.EXPLOSION, self._on_explosion)
    
    # 游戏状态回调
    def _on_state_change(self, old_state, new_state):
        """游戏状态改变回调"""
        print(f"游戏状态: {old_state.name} -> {new_state.name}")
    
    def _on_start_game(self, level, difficulty):
        """开始游戏回调"""
        self._init_game_components(level, difficulty)
        self.menu_system.hide_current_menu()
    
    def _on_pause(self):
        """暂停游戏回调"""
        self.menu_system.show_pause_menu()
    
    def _on_resume(self):
        """继续游戏回调"""
        self.menu_system.hide_current_menu()
    
    def _on_restart(self):
        """重新开始回调"""
        self._init_game_components(self.current_level, self.current_difficulty)
        self.menu_system.hide_current_menu()
    
    def _on_quit(self):
        """退出游戏回调"""
        arcade.close_window()
    
    # 菜单回调
    def _on_menu_start_game(self):
        """菜单开始游戏"""
        self.game_state.start_game(1)
    
    def _on_menu_level_select(self):
        """菜单关卡选择"""
        self.menu_system.show_level_select(self.game_state.max_unlocked_level)
    
    def _on_menu_settings(self):
        """菜单设置"""
        self.menu_system.show_settings()

    def _on_master_volume_change(self, value: float):
        """主音量变化回调"""
        self.audio_manager.set_master_volume(value)

    def _on_sfx_volume_change(self, value: float):
        """音效音量变化回调"""
        self.audio_manager.set_sfx_volume(value)

    def _on_music_volume_change(self, value: float):
        """音乐音量变化回调"""
        self.audio_manager.set_music_volume(value)
    
    def _on_menu_quit(self):
        """菜单退出"""
        self.game_state.quit_game()
    
    def _on_menu_resume(self):
        """菜单继续"""
        self.game_state.resume_game()
    
    def _on_menu_restart(self):
        """菜单重新开始"""
        self.game_state.restart_game()
    
    def _on_menu_main_menu(self):
        """菜单返回主菜单"""
        self.game_state.go_to_main_menu()
        self.menu_system.show_main_menu()
    
    def _on_difficulty_selected(self, difficulty: str):
        """难度选择回调"""
        # 保存当前选择的难度
        self.current_difficulty = difficulty
        # 开始游戏（使用当前关卡或默认关卡1）
        level = getattr(self.menu_system, '_pending_level', 1)
        self.game_state.start_game(level, difficulty)
    
    def on_update(self, delta_time: float):
        """更新游戏状态"""
        # 如果在菜单中，只更新菜单
        if self.game_state.is_in_menu():
            return
        
        # 如果暂停，不更新游戏逻辑
        if self.game_state.is_paused():
            return
        
        # 更新游戏组件
        if self.world:
            self.world.update(delta_time)
            self.planting_system.update(delta_time, self.sun_count)
            self.zombie_spawner.update(delta_time)
            self.sun_collection_system.update(delta_time)
            self.particle_system.update(delta_time)
            self.damage_number_system.update(delta_time)
            self.screen_shake.update(delta_time)
            self._update_health_bars()
            self._check_game_over()
    
    def on_draw(self):
        """渲染游戏画面"""
        arcade.start_render()
        
        # 如果在菜单中，只渲染菜单
        if self.game_state.is_in_menu():
            self.menu_system.render()
            return
        
        # 渲染游戏画面
        if self.background_renderer:
            self.background_renderer.render()
        
        if self.world:
            self.render_system.render(self.world._component_manager)
        
        if self.particle_system:
            self.particle_system.render()
        
        if self.health_bar_system:
            self.health_bar_system.render()
        
        if self.damage_number_system:
            self.damage_number_system.render()
        
        if self.planting_system:
            self.planting_system.render(self._mouse_x, self._mouse_y)
        
        if self.ui_renderer:
            self.ui_renderer.render(self.sun_count, self.score, self.current_level)
        
        # 如果暂停，渲染暂停菜单
        if self.game_state.is_paused():
            self.menu_system.render()
        
        # 如果游戏结束或胜利，渲染结束菜单
        if self.game_state.is_game_over() or self.game_state.is_victory():
            self.menu_system.render()
    
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """处理鼠标移动"""
        self._mouse_x = x
        self._mouse_y = y
        
        # 如果在菜单中，传递给菜单系统
        if self.game_state.is_in_menu() or self.game_state.is_paused():
            self.menu_system.on_mouse_motion(x, y)
            return
        
        # 更新种植系统的鼠标位置
        if self.planting_system:
            self.planting_system.handle_mouse_move(x, y)
    
    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """处理鼠标点击"""
        # 如果在菜单中或暂停，传递给菜单系统
        if self.game_state.is_in_menu() or self.game_state.is_paused():
            if self.menu_system.on_mouse_click(x, y):
                return
        
        # 如果在游戏中，处理游戏逻辑
        if self.game_state.is_playing():
            if button == arcade.MOUSE_BUTTON_LEFT:
                # 先尝试收集阳光
                if self.sun_collection_system:
                    collected = self.sun_collection_system.try_collect_sun(x, y)
                    if collected:
                        self.audio_manager.play_sun_collect_sound()
                        return
                
                # 使用 planting_system 处理种植/铲子点击
                if self.planting_system:
                    handled, planted, removed = self.planting_system.handle_mouse_press(
                        x, y, self.sun_count, return_tuple=True
                    )
                    if handled:
                        if planted:
                            # 处理种植后的逻辑
                            plant_type = None
                            if self.planting_system.selected_card:
                                plant_type = self.planting_system.selected_card.plant_type
                            self.sun_count -= self.planting_system.get_planting_cost()
                            self.audio_manager.play_plant_sound()
                            self.particle_system.create_plant_effect(x, y)
                        elif removed:
                            # 处理移除植物
                            pass
                        return
            
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                # 取消种植选择或退出铲子模式
                if self.planting_system:
                    self.planting_system.cancel_selection()
                    if hasattr(self.planting_system, 'shovel_mode'):
                        self.planting_system.shovel_mode = False
    
    def on_key_press(self, key: int, modifiers: int):
        """处理键盘按键"""
        if key == arcade.key.ESCAPE:
            # ESC键切换暂停
            if self.game_state.is_playing():
                self.game_state.pause_game()
            elif self.game_state.is_paused():
                self.game_state.resume_game()
        
        elif key == arcade.key.SPACE:
            # 空格键在胜利时进入下一关
            if self.game_state.is_victory():
                self.game_state.next_level()
        
        elif key == arcade.key.R:
            # R键重新开始
            if self.game_state.is_game_over() or self.game_state.is_victory():
                self.game_state.restart_game()
        
        # 数字键选择植物
        if self.game_state.is_playing() and self.planting_system:
            if key == arcade.key.KEY_1:
                self.planting_system.select_plant_type(0)
            elif key == arcade.key.KEY_2:
                self.planting_system.select_plant_type(1)
            elif key == arcade.key.KEY_3:
                self.planting_system.select_plant_type(2)
            elif key == arcade.key.KEY_4:
                self.planting_system.select_plant_type(3)
            elif key == arcade.key.KEY_5:
                self.planting_system.select_plant_type(4)
    
    def _update_health_bars(self):
        """更新血条显示"""
        if not self.world or not self.health_bar_system:
            return
        
        zombies = self.world._component_manager.query(
            TransformComponent, HealthComponent, ZombieComponent
        )
        for entity_id in zombies:
            transform = self.world._component_manager.get_component(entity_id, TransformComponent)
            health = self.world._component_manager.get_component(entity_id, HealthComponent)
            
            if transform and health:
                if self.health_bar_system.get_health_bar(entity_id) is None:
                    self.health_bar_system.add_health_bar(
                        entity_id, transform.x, transform.y,
                        health.current, health.max_health
                    )
                else:
                    self.health_bar_system.update_health_bar(
                        entity_id, transform.x, transform.y, health.current
                    )
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        if not self.world or not self.zombie_spawner:
            return
        
        # 检查是否有僵尸到达最左侧
        zombies = self.world._component_manager.query(TransformComponent, ZombieComponent)
        for entity_id in zombies:
            transform = self.world._component_manager.get_component(entity_id, TransformComponent)
            if transform and transform.x <= 0:
                self.game_state.game_over(self.score)
                self.menu_system.show_game_over(False, self.score)
                self.audio_manager.play_game_over_sound()
                return
        
        # 检查是否完成所有波次且没有僵尸
        if self.zombie_spawner.is_level_complete():
            zombies_remaining = len(self.world._component_manager.query(TransformComponent, ZombieComponent))
            if zombies_remaining == 0:
                self.game_state.victory(self.score)
                self.menu_system.show_game_over(True, self.score)
                self.audio_manager.play_victory_sound()
    
    def _on_zombie_death(self, zombie_id: int, score_value: int):
        """僵尸死亡回调"""
        self.score += score_value
        self.audio_manager.play_zombie_death_sound()
        
        if self.particle_system:
            transform = self.world._component_manager.get_component(zombie_id, TransformComponent)
            if transform:
                self.particle_system.create_zombie_death_effect(transform.x, transform.y)
        
        if self.health_bar_system:
            self.health_bar_system.remove_health_bar(zombie_id)
    
    def _on_sun_collected(self, amount: int, x: float, y: float):
        """阳光收集回调"""
        self.sun_count += amount
        if self.particle_system:
            self.particle_system.create_collect_effect(x, y)
    
    def _on_damage_dealt(self, event: Event):
        """处理伤害事件"""
        x = event.data.get('x', 0)
        y = event.data.get('y', 0)
        damage = event.data.get('damage', 0)
        damage_type = event.data.get('damage_type', 'normal')
        
        if self.damage_number_system:
            self.damage_number_system.add_damage_number(x, y, damage, damage_type)
        
        if self.particle_system:
            self.particle_system.create_hit_effect(x, y)
    
    def _on_explosion(self, event: Event):
        """处理爆炸事件"""
        x = event.data.get('x', 0)
        y = event.data.get('y', 0)
        radius = event.data.get('radius', 100)
        
        if self.particle_system:
            self.particle_system.create_explosion(x, y)
        
        if self.screen_shake:
            self.screen_shake.start_shake(0.5, 10)
