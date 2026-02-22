"""
游戏窗口 - 使用Arcade引擎的主窗口
"""

import arcade
import traceback
from ..ecs import World
from ..core.logger import get_module_logger
from ..ecs.systems import (
    RenderSystem, OptimizedRenderSystem, MovementSystem, CollisionSystem,
    HealthSystem, SunSystem, WaveSystem,
    PlantBehaviorSystem, ProjectileSystem, ZombieBehaviorSystem
)
from ..ecs.components import (
    TransformComponent, HealthComponent, ZombieComponent,
    PlantComponent, GridPositionComponent, SpriteComponent
)
from ..core.event_bus import EventBus, Event, EventType
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
from .ui_renderer import UIRenderer, GameOverRenderer
from .visual_effects_optimized import OptimizedVisualEffectsSystem
from .pvz_visual_effects import PvzVisualEffectsSystem
from .three_d_effects_optimized import ThreeDEffectsOptimized
from .save_system import SaveSystem, GameSaveData, get_save_system
from .zombie_render_integration import get_zombie_render_integration
from ..core.performance_monitor import get_performance_monitor, toggle_debug
from ..core.game_state import GameStateManager, GameState
from ..core.game_constants import EASY, NORMAL, HARD
from ..ui.menu_system import MenuSystem


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
        # 初始化日志记录器
        self.logger = get_module_logger(__name__)
        
        super().__init__(
            self.SCREEN_WIDTH,
            self.SCREEN_HEIGHT,
            self.SCREEN_TITLE
        )
        
        self.logger.info("游戏窗口初始化开始")
        
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
        self.game_over = False
        self.victory = False
        self.current_difficulty = "normal"
        
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
        self.three_d_effects = None
        self.zombie_render_integration = None
        self.save_system = None
        self.event_bus = None
        self.play_time = 0.0
        
        # 显示主菜单
        self.menu_system.show_main_menu()
        
        arcade.set_background_color(self.BACKGROUND_COLOR)
        
        self._mouse_x = 0
        self._mouse_y = 0
        
        self.logger.info("游戏窗口初始化完成")
    
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
        self.visual_effects = PvzVisualEffectsSystem()
        
        # 创建背景渲染器
        self.background_renderer = BackgroundRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 先创建3D效果系统
        self.three_d_effects = ThreeDEffectsOptimized()
        
        # 初始化僵尸渲染集成系统
        self.zombie_render_integration = get_zombie_render_integration()
        
        # 初始化存档系统
        self.save_system = get_save_system()
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 注册僵尸死亡回调
        self.zombie_behavior_system.register_death_callback(self._on_zombie_death)
        
        # 重置游戏数据（根据难度设置初始阳光）
        self.sun_count = difficulty_config.initial_sun
        self.score = 0
        self.play_time = 0.0
    
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
        # 使用渲染系统
        from ..ecs.systems import RenderSystem
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
        
        self.zombie_behavior_system = ZombieBehaviorSystem(
            entity_manager=self.world._entity_manager,
            priority=45
        )
        self.world.add_system(self.zombie_behavior_system)
        
        self.sun_system = SunSystem(priority=50)
        self.world.add_system(self.sun_system)
        
        self.wave_system = WaveSystem(self.current_level, priority=60)
        self.world.add_system(self.wave_system)
    
    def _register_event_handlers(self):
        """注册事件处理器"""
        self.event_bus.subscribe(EventType.DAMAGE_DEALT, self._on_damage_dealt)
        self.event_bus.subscribe(EventType.EXPLOSION, self._on_explosion)
        self.event_bus.subscribe(EventType.PLANT_DIED, self._on_plant_died)
    
    def _on_damage_dealt(self, event: Event):
        """处理伤害事件"""
        x = event.data.get('x', 0)
        y = event.data.get('y', 0)
        damage = event.data.get('damage', 0)
        damage_type = event.data.get('damage_type', 'normal')
        target_id = event.data.get('target_id')
        
        self.damage_number_system.add_damage_number(x, y, damage, damage_type)
        
        self.particle_system.create_hit_effect(x, y)
        
        # 添加视觉特效
        if damage_type == 'ice':
            self.visual_effects.create_frost(x, y, radius=40, duration=0.4)
            self.visual_effects.create_hit_spark(x, y, length=15, color=(150, 200, 255))
            # Add PVZ-style ice trail
            self.visual_effects.create_ice_trail(x, y, radius=35, duration=0.5)
        else:
            self.visual_effects.create_hit_spark(x, y)
            self.visual_effects.create_ripple(x, y, max_radius=30, color=(255, 200, 100))
            # Add PVZ-style damage pop
            self.visual_effects.create_damage_pop(x, y, damage, color=(255, 255, 255), duration=1.0)
        
        # 如果目标是僵尸，触发僵尸受击效果
        if target_id is not None:
            self.zombie_render_integration.trigger_hit(target_id, damage)
        
        self._play_damage_sound(damage_type)
    
    def _play_damage_sound(self, damage_type: str):
        """根据伤害类型播放音效"""
        from .audio_manager import SoundType
        if damage_type == 'ice':
            self.audio_manager.play_ice_hit_sound()
        elif damage_type == 'fire':
            self.audio_manager.play_fire_hit_sound()
        else:
            self.audio_manager.play_hit_sound()
    
    def _on_explosion(self, event: Event):
        """处理爆炸事件"""
        x = event.data.get('x', 0)
        y = event.data.get('y', 0)
        radius = event.data.get('radius', 100)
        explosion_type = event.data.get('explosion_type', 'cherry_bomb')
        
        intensity = min(radius / 10, 20)
        self.screen_shake.shake(intensity, 0.3)
        
        particle_count = int(radius / 5)
        from .particle_system import Color
        self.particle_system.create_explosion(x, y, Color(255, 100, 0), particle_count)
        
        # 添加视觉特效
        if explosion_type == 'cherry_bomb':
            self.visual_effects.create_cherry_bomb_visual(x, y)
        elif explosion_type == 'potato_mine':
            self.visual_effects.create_potato_mine_visual(x, y)
        else:
            self.visual_effects.create_explosion(x, y, max_radius=radius, color=(255, 150, 50))
            self.visual_effects.create_shockwave(x, y, max_radius=radius * 1.5)
        
        self.audio_manager.play_sound(self._get_explosion_sound_type(explosion_type))
    
    def _get_explosion_sound_type(self, explosion_type: str):
        """获取爆炸音效类型"""
        from .audio_manager import SoundType
        if explosion_type == 'cherry_bomb':
            return SoundType.CHERRY_BOMB
        elif explosion_type == 'potato_mine':
            return SoundType.POTATO_MINE
        return SoundType.EXPLOSION
    
    def _on_plant_died(self, event: Event):
        """处理植物死亡事件"""
        entity_id = event.data.get('entity_id')
        row = event.data.get('row', -1)
        col = event.data.get('col', -1)
        
        # 从 planting_system 中移除植物引用
        if row >= 0 and col >= 0:
            if self.planting_system.is_position_occupied(row, col):
                # 获取该位置的实体
                plant_entity = self.planting_system.get_plant_at(row, col)
                if plant_entity and plant_entity.id == entity_id:
                    # 从 planted_positions 中移除
                    del self.planting_system.planted_positions[(row, col)]
        
        # 销毁实体
        try:
            from ..ecs import Entity
            entity = Entity()
            entity.id = entity_id
            self.world.destroy_entity(entity)
        except Exception as e:
            self.logger.warning(f"销毁植物实体失败: {e}")
    
    def on_update(self, delta_time: float):
        """更新游戏状态"""
        # 如果在菜单中，只更新菜单
        if self.game_state.is_in_menu():
            return
        
        # 如果暂停，不更新游戏逻辑
        if self.game_state.is_paused():
            return
        
        # 如果游戏未初始化或已结束，不更新
        if not self.world or self.game_over or self.victory:
            return
        
        try:
            # 更新游戏时长
            self.play_time += delta_time
            
            # 更新ECS世界
            self.world.update(delta_time)
            
            # 更新种植系统
            self.planting_system.update(delta_time, self.sun_count)
            
            # 更新僵尸生成器
            self.zombie_spawner.update(delta_time)
            
            # 更新阳光收集系统
            self.sun_collection_system.update(delta_time)
            
            # 更新粒子系统
            self.particle_system.update(delta_time)
            
            # 更新伤害数字系统
            self.damage_number_system.update(delta_time)
            
            # 更新屏幕震动
            self.screen_shake.update(delta_time)
            
            # 更新UI渲染器
            self.ui_renderer.update(delta_time)
            self.ui_renderer.set_sun_count(self.sun_count)
            self.ui_renderer.set_score(self.score)
            
            # 更新波次信息
            self.ui_renderer.set_wave_info(
                self.zombie_spawner.current_wave,
                self.zombie_spawner.total_waves,
                getattr(self.zombie_spawner, 'get_wave_progress', lambda: 0.0)()
            )
            
            # 更新背景动画
            self.background_renderer.update(delta_time)
            
            # 更新视觉特效系统
            self.visual_effects.update(delta_time)
            
            # 更新3D效果系统
            self.three_d_effects.update(delta_time)
            
            # 更新僵尸渲染集成系统
            self.zombie_render_integration.update(delta_time, self.world._component_manager)
            
            # 更新血条系统
            self._update_health_bars()
            
            # 检查游戏结束条件
            self._check_game_over()
        except Exception as e:
            self.logger.error(f"游戏更新时发生异常: {e}")
            self.logger.error(traceback.format_exc())
    
    def _update_health_bars(self):
        """更新血条显示"""
        # 更新僵尸血条
        zombies = self.world._component_manager.query(
            TransformComponent, HealthComponent, ZombieComponent
        )
        for entity_id in zombies:
            transform = self.world._component_manager.get_component(entity_id, TransformComponent)
            health = self.world._component_manager.get_component(entity_id, HealthComponent)
            
            if transform and health:
                # 如果血条不存在，添加血条
                if self.health_bar_system.get_health_bar(entity_id) is None:
                    self.health_bar_system.add_health_bar(
                        entity_id, transform.x, transform.y,
                        health.current, health.max_health
                    )
                else:
                    # 更新血条位置和血量
                    self.health_bar_system.update_health_bar(
                        entity_id, health.current, health.max_health,
                        transform.x, transform.y
                    )
        
        # 更新植物血条（只对高血量植物如坚果墙显示）
        plants = self.world._component_manager.query(
            TransformComponent, HealthComponent, PlantComponent
        )
        for entity_id in plants:
            health = self.world._component_manager.get_component(entity_id, HealthComponent)
            # 只对最大生命值大于100的植物显示血条
            if health and health.max_health > 100:
                transform = self.world._component_manager.get_component(entity_id, TransformComponent)
                if transform:
                    if self.health_bar_system.get_health_bar(entity_id) is None:
                        self.health_bar_system.add_health_bar(
                            entity_id, transform.x, transform.y,
                            health.current, health.max_health,
                            width=40, height=4  # 植物血条小一些
                        )
                    else:
                        self.health_bar_system.update_health_bar(
                            entity_id, health.current, health.max_health,
                            transform.x, transform.y
                        )
    
    def on_draw(self):
        """渲染游戏画面"""
        # 开始性能监控帧
        perf_monitor = get_performance_monitor()
        perf_monitor.begin_frame()
        
        self.clear()
        
        # 如果在菜单中，只渲染菜单
        if self.game_state.is_in_menu():
            self.menu_system.render()
            perf_monitor.end_frame()
            return
        
        # 如果游戏未初始化，不渲染游戏画面
        if not self.world:
            perf_monitor.end_frame()
            return
        
        # 获取屏幕震动偏移（暂时不应用）
        shake_x, shake_y = self.screen_shake.get_offset()
        
        # 渲染背景
        self.background_renderer.render()
        
        # 渲染所有实体
        self.render_system.render(self.world._component_manager)
        
        # 渲染僵尸特效（阴影、尘土、表情等）
        self._render_zombie_effects()
        
        # 渲染血条
        self.health_bar_system.render()
        
        # 渲染伤害数字
        self.damage_number_system.render()
        
        # 渲染种植系统（传递鼠标位置）
        self.planting_system.render(self._mouse_x, self._mouse_y)
        
        # 渲染阳光
        self.sun_collection_system.render_suns()
        
        # 渲染粒子效果
        self.particle_system.render()
        
        # 渲染视觉特效
        self.visual_effects.render()
        
        # 渲染UI
        self._draw_ui()
        
        # 如果暂停，渲染暂停菜单
        if self.game_state.is_paused():
            self.menu_system.render()
        
        # 如果游戏结束或胜利，渲染结束菜单
        if self.game_state.is_game_over() or self.game_state.is_victory():
            self.menu_system.render()
        
        # 更新性能监控数据
        perf_monitor.set_entity_count(len(self.world._entity_manager._entities))
        perf_monitor.set_particle_count(self.particle_system.get_total_particle_count())
        
        # 渲染性能监控信息
        perf_monitor.render()
        
        # 结束性能监控帧
        perf_monitor.end_frame()
    
    def _render_zombie_effects(self):
        """渲染僵尸特效（阴影、尘土、表情等）"""
        # 获取所有僵尸实体并渲染特效
        zombies = self.world._component_manager.query(
            TransformComponent, SpriteComponent, ZombieComponent
        )
        for zombie_id in zombies:
            self.zombie_render_integration.render(zombie_id, self.world._component_manager)
    
    def _draw_ui(self):
        """绘制UI界面"""
        # 使用增强的UI渲染器
        self.ui_renderer.render()
    
    def _draw_game_over(self):
        """绘制游戏结束画面 - 使用增强版渲染器"""
        self.game_over_renderer.show(False, self.score, self.zombie_spawner.current_wave)
        self.game_over_renderer.render()
    
    def _draw_victory(self):
        """绘制胜利画面 - 使用增强版渲染器"""
        self.game_over_renderer.show(True, self.score, self.zombie_spawner.current_wave)
        self.game_over_renderer.render()
    
    def _check_game_over(self):
        """检查游戏是否结束"""
        # 检查是否有僵尸到达最左侧
        zombies = self.world._component_manager.query(TransformComponent, ZombieComponent)
        for entity_id in zombies:
            transform = self.world._component_manager.get_component(entity_id, TransformComponent)
            if transform and transform.x <= 0:
                self.game_over = True
                # 使用游戏状态管理器
                self.game_state.game_over(self.score)
                # 显示游戏结束菜单
                self.menu_system.show_game_over(False, self.score)
                # 播放游戏结束音效
                self.audio_manager.play_game_over_sound()
                return
        
        # 检查是否完成所有波次且没有僵尸
        if self.zombie_spawner.is_level_complete():
            zombies_remaining = len(self.world._component_manager.query(TransformComponent, ZombieComponent))
            if zombies_remaining == 0:
                self.victory = True
                # 使用游戏状态管理器
                self.game_state.victory(self.score)
                # 显示胜利菜单
                self.menu_system.show_game_over(True, self.score)
                # 播放胜利音效
                self.audio_manager.play_victory_sound()
    
    def _on_zombie_death(self, zombie_id: int, score_value: int):
        """僵尸死亡回调"""
        self.add_score(score_value)
        # 播放僵尸死亡音效
        self.audio_manager.play_zombie_death_sound()
        
        # 获取僵尸位置并创建粒子效果
        transform = self.world._component_manager.get_component(zombie_id, TransformComponent)
        if transform:
            self.particle_system.create_zombie_death_effect(transform.x, transform.y)
            # 触发僵尸死亡动画
            from .zombie_visual_system import DeathType
            self.zombie_render_integration.start_death_animation(
                zombie_id, transform.x, transform.y,
                zombie_type='normal', death_type=DeathType.NORMAL
            )
        
        # 移除血条
        self.health_bar_system.remove_health_bar(zombie_id)
        
        # 移除僵尸渲染效果
        self.zombie_render_integration.remove_zombie(zombie_id)
    
    def _on_sun_collected(self, amount: int, x: float, y: float):
        """阳光收集回调"""
        self.add_sun(amount)
        # 创建收集粒子效果
        self.particle_system.create_collect_effect(x, y)
        # 创建阳光发光效果
        self.particle_system.create_sun_glow(x, y)
    
    def show_damage_number(self, x: float, y: float, damage: int, damage_type: str = "normal"):
        """
        显示伤害数字
        
        Args:
            x: X坐标
            y: Y坐标
            damage: 伤害值
            damage_type: 伤害类型
        """
        self.damage_number_system.add_damage_number(x, y, damage, damage_type)
    
    def trigger_screen_shake(self, intensity: float = 10.0, duration: float = 0.3):
        """
        触发屏幕震动
        
        Args:
            intensity: 震动强度
            duration: 持续时间
        """
        self.screen_shake.shake(intensity, duration)
    
    def on_key_press(self, key, modifiers):
        """处理键盘按键"""
        if key == arcade.key.ESCAPE:
            # 暂停/恢复游戏
            if self.game_state.is_playing():
                self.game_state.pause_game()
            elif self.game_state.is_paused():
                self.game_state.resume_game()
        elif key == arcade.key.R:
            # 重置游戏 - 任何时候都可以重置
            self.reset_game()
        elif key == arcade.key.SPACE:
            # 下一关
            if self.victory:
                self.next_level()
        elif key == arcade.key.F5:
            # 快速保存到槽位1
            self.save_game(1)
        elif key == arcade.key.F9:
            # 快速加载槽位1
            self.load_game(1)
        elif key == arcade.key.F3:
            # 切换性能监控显示
            toggle_debug()
    
    def save_game(self, slot: int = 1) -> bool:
        """
        保存游戏
        
        Args:
            slot: 存档槽位
            
        Returns:
            是否保存成功
        """
        # 先清理已销毁的植物引用
        self.planting_system._cleanup_destroyed_plants()
        
        # 收集植物数据
        plants = []
        for (row, col), entity in self.planting_system.planted_positions.items():
            from ..ecs.components import PlantComponent, TransformComponent
            try:
                plant_comp = self.world._component_manager.get_component(entity, PlantComponent)
                transform_comp = self.world._component_manager.get_component(entity, TransformComponent)
                if plant_comp and transform_comp:
                    plants.append({
                        'plant_type': plant_comp.plant_type.name,
                        'x': transform_comp.x,
                        'y': transform_comp.y,
                        'row': row,
                        'col': col,
                        'health': plant_comp.health if hasattr(plant_comp, 'health') else 100
                    })
            except Exception:
                # 如果获取组件失败，跳过这个植物
                continue
        
        # 收集僵尸数据
        zombies = []
        from ..ecs.components import ZombieComponent, HealthComponent
        zombie_entities = self.world._component_manager.query(TransformComponent, ZombieComponent, HealthComponent)
        for entity_id in zombie_entities:
            transform = self.world._component_manager.get_component(entity_id, TransformComponent)
            zombie = self.world._component_manager.get_component(entity_id, ZombieComponent)
            health = self.world._component_manager.get_component(entity_id, HealthComponent)
            if transform and zombie and health:
                zombies.append({
                    'zombie_type': zombie.zombie_type.name if hasattr(zombie, 'zombie_type') else 'NORMAL',
                    'x': transform.x,
                    'y': transform.y,
                    'health': health.current,
                    'max_health': health.max_health
                })
        
        # 创建存档数据
        save_data = GameSaveData(
            save_name=f"存档 {slot}",
            current_level=self.current_level,
            sun_count=self.sun_count,
            score=self.score,
            play_time=self.play_time,
            wave_index=getattr(self.zombie_spawner, 'current_wave', 0),
            plants=plants,
            zombies=zombies
        )
        
        # 保存
        success = self.save_system.save_game(slot, save_data)
        if success:
            print(f"游戏已保存到槽位 {slot}")
        return success
    
    def load_game(self, slot: int = 1) -> bool:
        """
        加载游戏
        
        Args:
            slot: 存档槽位
            
        Returns:
            是否加载成功
        """
        save_data = self.save_system.load_game(slot)
        if not save_data:
            return False
        
        # 重置游戏
        self.reset_game()
        
        # 恢复游戏状态
        self.current_level = save_data.current_level
        self.sun_count = save_data.sun_count
        self.score = save_data.score
        self.play_time = save_data.play_time
        
        # 重新初始化僵尸生成器
        self.zombie_spawner.set_level(self.current_level)
        
        # 恢复植物
        for plant_data in save_data.plants:
            try:
                from ..ecs.components import PlantType
                plant_type = PlantType[plant_data['plant_type']]
                
                # 选择对应的卡片
                for card in self.planting_system.cards:
                    if card.plant_type == plant_type:
                        self.planting_system._select_card(card)
                        
                        # 种植植物
                        if self.planting_system._can_plant_at(plant_data['row'], plant_data['col'], float('inf')):
                            self.planting_system._plant_at(plant_data['row'], plant_data['col'])
                        break
            except Exception as e:
                print(f"恢复植物失败: {e}")
        
        print(f"游戏已从槽位 {slot} 加载")
        return True
    
    def on_mouse_press(self, x: float, y: float, button, modifiers):
        """处理鼠标点击"""
        # 如果有菜单显示，优先处理菜单点击
        if (self.game_state.is_in_menu() or 
            self.game_state.is_paused() or 
            self.game_state.is_game_over() or 
            self.game_state.is_victory()):
            if self.menu_system.on_mouse_click(x, y):
                return
        
        # 如果游戏未初始化，不处理游戏点击
        if not self.world:
            return
        
        # 先尝试收集阳光
        if self.sun_collection_system.handle_mouse_press(x, y):
            # 播放收集音效
            self.audio_manager.play_collect_sun_sound()
            return
        
        # 处理种植
        handled, planted, removed = self.planting_system.handle_mouse_press(x, y, self.sun_count, return_tuple=True)
        if handled:
            if planted:
                # 播放种植音效
                self.audio_manager.play_plant_sound()
                # 创建种植粒子效果
                self.particle_system.create_plant_effect(x, y)
                # 创建种植视觉特效
                self.visual_effects.create_planting_visual(x, y)
                # 消耗阳光
                cost = self.planting_system.get_planting_cost()
                if cost > 0:
                    self.spend_sun(cost)
            elif removed is not None:
                # 植物被移除，创建特效
                row, col = removed
                cell_x = self.planting_system.GRID_START_X + col * self.planting_system.CELL_WIDTH + self.planting_system.CELL_WIDTH / 2
                cell_y = self.planting_system.GRID_START_Y + row * self.planting_system.CELL_HEIGHT + self.planting_system.CELL_HEIGHT / 2
                # 创建移除植物的粒子效果
                self.particle_system.create_plant_effect(cell_x, cell_y)
            return
    
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """处理鼠标移动"""
        self._mouse_x = x
        self._mouse_y = y
        
        # 如果在菜单中，传递给菜单系统
        if (self.game_state.is_in_menu() or 
            self.game_state.is_paused() or 
            self.game_state.is_game_over() or 
            self.game_state.is_victory()):
            self.menu_system.on_mouse_motion(x, y)
            return
        
        # 更新植物卡片悬浮状态
        if self.planting_system:
            self.planting_system.handle_mouse_move(x, y)
    
    def reset_game(self):
        """重置游戏"""
        self.world.clear()
        self.planting_system.clear()
        self.zombie_spawner.reset()
        self.sun_collection_system.reset()
        self.particle_system.clear()
        self.health_bar_system.clear()
        self.damage_number_system.clear()
        self.visual_effects.clear()
        self.zombie_render_integration.clear()
        self.screen_shake.stop()
        self.sun_count = 50
        self.score = 0
        self.game_over = False
        self.victory = False
        self._init_systems()
        self._register_event_handlers()
        self.zombie_spawner.set_level(self.current_level)
        self.zombie_behavior_system.register_death_callback(self._on_zombie_death)
        self.sun_collection_system.register_collection_callback(self._on_sun_collected)
    
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
    
    # ==================== 游戏状态回调 ====================
    
    def _on_state_change(self, old_state, new_state):
        """游戏状态改变回调"""
        self.logger.info(f"游戏状态: {old_state.name} -> {new_state.name}")
    
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
    
    # ==================== 菜单回调 ====================
    
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
