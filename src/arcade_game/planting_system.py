"""
种植系统 - 处理植物种植的所有逻辑

包括：
- 植物卡片UI（带动画效果）
- 鼠标点击种植
- 阳光消耗验证
- 网格位置检查
"""

import os
import math
from typing import Optional, Dict, List, Tuple
import arcade
from ..ecs import World, Entity
from ..ecs.components import PlantType, PLANT_CONFIGS
from .entity_factory import EntityFactory
from .sprite_manager import get_sprite_manager


class PlantCard:
    """
    植物卡片类
    
    表示UI上的一个植物选择卡片，带有增强的视觉效果
    """
    
    PLANT_SPRITE_FILES = {
        'PEASHOOTER': 'peashooter.png',
        'SUNFLOWER': 'sunflower.png',
        'WALLNUT': 'wallnut.png',
        'CHERRY_BOMB': 'cherry_bomb.png',
        'SNOW_PEA': 'snow_pea.png',
        'REPEATER': 'repeater.png',
        'CHOMPER': 'chomper.png',
        'POTATO_MINE': 'potato_mine.png',
    }
    
    # 卡片颜色配置
    CARD_BG_AVAILABLE = (60, 80, 60, 230)
    CARD_BG_UNAVAILABLE = (40, 40, 40, 200)
    CARD_BG_HOVER = (80, 100, 80, 240)
    CARD_BORDER_NORMAL = (100, 100, 100)
    CARD_BORDER_SELECTED = (255, 220, 50)
    CARD_BORDER_HOVER = (150, 180, 150)
    SUN_COST_COLOR = (255, 220, 50)
    COOLDAY_OVERLAY = (0, 0, 0, 150)
    
    def __init__(self, plant_type: PlantType, x: float, y: float, 
                 width: float = 60, height: float = 80):
        self.plant_type = plant_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        config = PLANT_CONFIGS.get(plant_type, {})
        self.cost = config.get('cost', 100)
        self.color = config.get('color', (0, 200, 0))
        self.name = plant_type.name
        
        self.is_selected = False
        self.is_available = True
        self.is_hovered = False
        self.cooldown_timer = 0.0
        self.cooldown_duration = config.get('attack_cooldown', 1.5)
        
        # 动画状态
        self._scale = 1.0
        self._target_scale = 1.0
        self._glow_intensity = 0.0
        self._shake_offset = 0.0
        self._time = 0.0
        
        self._texture = self._load_texture()
    
    def _load_texture(self) -> Optional[arcade.Texture]:
        """加载植物精灵图纹理"""
        sprite_manager = get_sprite_manager()
        
        # 获取文件名
        filename = self.PLANT_SPRITE_FILES.get(self.plant_type.name)
        if not filename:
            return None
        
        # 构建完整路径
        texture_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'sprites', 'plants', filename
        )
        
        # 加载纹理
        if os.path.exists(texture_path):
            try:
                texture_name = f"planting_card_{self.plant_type.name.lower()}"
                return sprite_manager.load_texture(texture_name, texture_path)
            except Exception:
                pass
        return None
    
    def contains_point(self, px: float, py: float) -> bool:
        """检查点是否在卡片内"""
        half_width = self.width / 2 * self._scale
        half_height = self.height / 2 * self._scale
        return (self.x - half_width <= px <= self.x + half_width and
                self.y - half_height <= py <= self.y + half_height)
    
    def update(self, dt: float, sun_count: int) -> None:
        """更新卡片状态"""
        self._time += dt
        
        # 更新冷却
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.cooldown_timer = 0
        
        # 检查是否可用（阳光足够且不在冷却）
        was_available = self.is_available
        self.is_available = (sun_count >= self.cost and 
                            self.cooldown_timer <= 0)
        
        # 如果刚变得可用，触发动画
        if self.is_available and not was_available:
            self._target_scale = 1.15
            self._glow_intensity = 1.0
        
        # 更新动画状态
        self._update_animations(dt)
    
    def _update_animations(self, dt: float) -> None:
        """更新动画状态"""
        # 缩放动画（弹性效果）
        scale_diff = self._target_scale - self._scale
        self._scale += scale_diff * 0.15
        if abs(scale_diff) < 0.01:
            self._scale = self._target_scale
            if self._target_scale > 1.0:
                self._target_scale = 1.0
        
        # 发光衰减
        self._glow_intensity *= 0.92
        if self._glow_intensity < 0.01:
            self._glow_intensity = 0.0
        
        # 震动衰减
        self._shake_offset *= 0.85
        if abs(self._shake_offset) < 0.1:
            self._shake_offset = 0.0
    
    def set_hover(self, is_hovered: bool) -> None:
        """设置悬浮状态"""
        if is_hovered != self.is_hovered:
            self.is_hovered = is_hovered
            if is_hovered and self.is_available:
                self._target_scale = 1.08
            else:
                self._target_scale = 1.0
    
    def trigger_shake(self) -> None:
        """触发震动效果（用于不可用时点击）"""
        self._shake_offset = 5.0
    
    def start_cooldown(self) -> None:
        """开始冷却"""
        self.cooldown_timer = self.cooldown_duration
        self._target_scale = 1.0
        self._scale = 1.0
    
    def render(self) -> None:
        """渲染卡片"""
        # 计算缩放后的尺寸
        scaled_width = self.width * self._scale
        scaled_height = self.height * self._scale
        half_width = scaled_width / 2
        half_height = scaled_height / 2
        
        # 应用震动偏移
        render_x = self.x + self._shake_offset
        render_y = self.y
        
        # 绘制发光效果
        if self._glow_intensity > 0:
            glow_size = 5 + self._glow_intensity * 10
            glow_alpha = int(100 * self._glow_intensity)
            arcade.draw_lrbt_rectangle_filled(
                render_x - half_width - glow_size, render_x + half_width + glow_size,
                render_y - half_height - glow_size, render_y + half_height + glow_size,
                (255, 255, 100, glow_alpha)
            )
        
        # 确定背景颜色
        if not self.is_available:
            bg_color = self.CARD_BG_UNAVAILABLE
        elif self.is_hovered or self.is_selected:
            bg_color = self.CARD_BG_HOVER
        else:
            bg_color = self.CARD_BG_AVAILABLE
        
        # 绘制卡片背景
        arcade.draw_lrbt_rectangle_filled(
            render_x - half_width, render_x + half_width,
            render_y - half_height, render_y + half_height,
            bg_color
        )
        
        # 绘制边框
        if self.is_selected:
            border_color = self.CARD_BORDER_SELECTED
            border_width = 3
            # 选中时添加脉冲效果
            pulse = 0.5 + 0.5 * math.sin(self._time * 5)
            pulse_alpha = int(100 * pulse)
            arcade.draw_lrbt_rectangle_outline(
                render_x - half_width - 2, render_x + half_width + 2,
                render_y - half_height - 2, render_y + half_height + 2,
                (*self.CARD_BORDER_SELECTED[:3], pulse_alpha), 2
            )
        elif self.is_hovered and self.is_available:
            border_color = self.CARD_BORDER_HOVER
            border_width = 2
        else:
            border_color = self.CARD_BORDER_NORMAL
            border_width = 1
        
        arcade.draw_lrbt_rectangle_outline(
            render_x - half_width, render_x + half_width,
            render_y - half_height, render_y + half_height,
            border_color, border_width
        )
        
        # 绘制植物图标区域
        icon_y = render_y + half_height * 0.2
        icon_size = 20 * self._scale
        arcade.draw_circle_filled(
            render_x, icon_y, icon_size,
            self.color if self.is_available else (80, 80, 80)
        )
        # 添加高光
        if self.is_available:
            arcade.draw_circle_filled(
                render_x - icon_size * 0.3, icon_y + icon_size * 0.3,
                icon_size * 0.3,
                (min(255, self.color[0] + 50), min(255, self.color[1] + 50), min(255, self.color[2] + 50))
            )
        
        # 绘制植物名称（简化显示）
        name_y = render_y + half_height - 12 * self._scale
        arcade.draw_text(
            self.name[:4],
            render_x, name_y,
            arcade.color.WHITE if self.is_available else (150, 150, 150),
            int(9 * self._scale),
            anchor_x="center"
        )
        
        # 绘制阳光成本
        cost_y = render_y - half_height + 12 * self._scale
        cost_color = self.SUN_COST_COLOR if self.is_available else (100, 100, 100)
        arcade.draw_text(
            f"{self.cost}",
            render_x, cost_y,
            cost_color,
            int(11 * self._scale),
            anchor_x="center",
            bold=True
        )
        
        # 绘制冷却遮罩
        if self.cooldown_timer > 0:
            cooldown_percent = self.cooldown_timer / self.cooldown_duration
            cooldown_height = scaled_height * cooldown_percent
            
            arcade.draw_lrbt_rectangle_filled(
                render_x - half_width, render_x + half_width,
                render_y - half_height, render_y - half_height + cooldown_height,
                self.COOLDAY_OVERLAY
            )
            
            # 绘制冷却进度条
            progress_width = scaled_width * (1.0 - cooldown_percent)
            if progress_width > 0:
                arcade.draw_lrbt_rectangle_filled(
                    render_x - half_width, render_x - half_width + progress_width,
                    render_y - half_height - 3, render_y - half_height,
                    (100, 200, 100)
                )


class PlantingSystem:
    """
    种植系统
    
    管理植物种植的所有逻辑
    """
    
    # 网格配置
    GRID_ROWS = 5
    GRID_COLS = 9
    CELL_WIDTH = 80
    CELL_HEIGHT = 100
    GRID_START_X = 100
    GRID_START_Y = 50
    
    def __init__(self, world: World, entity_factory: EntityFactory):
        self.world = world
        self.entity_factory = entity_factory
        
        # 植物卡片
        self.cards: List[PlantCard] = []
        self.selected_card: Optional[PlantCard] = None
        
        # 铲子模式
        self.shovel_mode = False
        self.shovel_x = 0
        self.shovel_y = 0
        
        # 已种植的植物位置 (row, col) -> Entity
        self.planted_positions: Dict[Tuple[int, int], Entity] = {}
        
        # 卡片冷却配置
        self.card_cooldowns: Dict[PlantType, float] = {}
        
        # 初始化卡片
        self._init_cards()
    
    def _init_cards(self) -> None:
        """初始化植物卡片"""
        # 要显示的植物类型
        plant_types = [
            PlantType.SUNFLOWER,
            PlantType.PEASHOOTER,
            PlantType.WALLNUT,
            PlantType.SNOW_PEA,
            PlantType.CHERRY_BOMB,
            PlantType.REPEATER,
            PlantType.THREEPEATER,
        ]
        
        # 在屏幕顶部创建卡片
        start_x = 150
        y = 550
        spacing = 70
        
        for i, plant_type in enumerate(plant_types):
            x = start_x + i * spacing
            card = PlantCard(plant_type, x, y)
            self.cards.append(card)
    
    def update(self, dt: float, sun_count: int) -> None:
        """更新种植系统"""
        for card in self.cards:
            card.update(dt, sun_count)
        
        # 清理已销毁的植物引用
        self._cleanup_destroyed_plants()
    
    def _cleanup_destroyed_plants(self) -> None:
        """
        清理已销毁的植物引用
        
        某些植物（如樱桃炸弹）会在爆炸后自动销毁自己，
        但 planted_positions 中仍然保留着对它们的引用。
        这个方法会清理这些无效的引用。
        """
        positions_to_remove = []
        for (row, col), entity in self.planted_positions.items():
            should_remove = False
            
            # 检查1：实体是否还存在（通过检查其组件）
            from ..ecs.components import TransformComponent, HealthComponent
            transform = self.world.get_component(entity, TransformComponent)
            if transform is None:
                should_remove = True
            else:
                # 检查2：实体是否已死亡（HealthComponent.is_dead）
                health = self.world.get_component(entity, HealthComponent)
                if health and health.is_dead:
                    should_remove = True
            
            if should_remove:
                positions_to_remove.append((row, col))
        
        # 移除无效引用
        for pos in positions_to_remove:
            del self.planted_positions[pos]
    
    def handle_mouse_move(self, x: float, y: float) -> None:
        """处理鼠标移动，更新悬浮状态"""
        for card in self.cards:
            card.set_hover(card.contains_point(x, y))
        
        # 更新铲子位置
        if self.shovel_mode:
            self.shovel_x = x
            self.shovel_y = y
    
    def handle_mouse_press(self, x: float, y: float, sun_count: int, 
                         return_tuple: bool = False) -> bool | tuple[bool, bool, tuple[int, int] | None]:
        """
        处理鼠标点击
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            sun_count: 当前阳光数量
            return_tuple: 是否返回元组 (向后兼容)
            
        Returns:
            如果 return_tuple=True，返回 (是否处理了点击, 是否成功种植, 被移除的植物位置)
            否则返回是否处理了点击（向后兼容）
        """
        result = self._handle_mouse_press_internal(x, y, sun_count)
        if return_tuple:
            return result
        return result[0]
    
    def _handle_mouse_press_internal(self, x: float, y: float, sun_count: int) -> tuple[bool, bool, tuple[int, int] | None]:
        """
        处理鼠标点击
        
        Returns:
            (是否处理了点击事件, 是否成功种植, 被移除的植物位置 (row, col) 或 None)
        """
        # 检查是否点击了铲子按钮区域
        shovel_x = 70
        shovel_y = 550
        shovel_width = 50
        shovel_height = 80
        if (shovel_x - shovel_width/2 <= x <= shovel_x + shovel_width/2 and
            shovel_y - shovel_height/2 <= y <= shovel_y + shovel_height/2):
            # 切换铲子模式
            self.shovel_mode = not self.shovel_mode
            if self.shovel_mode:
                self._deselect_card()
            return (True, False, None)
        
        # 如果在铲子模式
        if self.shovel_mode:
            grid_pos = self._get_grid_position(x, y)
            if grid_pos:
                row, col = grid_pos
                if (row, col) in self.planted_positions:
                    # 移除植物
                    self.remove_plant(row, col)
                    return (True, False, (row, col))
            # 点击了其他地方，退出铲子模式
            self.shovel_mode = False
            return (True, False, None)
        
        # 检查是否点击了卡片
        for card in self.cards:
            if card.contains_point(x, y):
                if card.is_available:
                    self._select_card(card)
                    self.shovel_mode = False
                    return (True, False, None)  # 处理了点击，但没有种植
                else:
                    # 不可用时触发震动效果
                    card.trigger_shake()
                    return (False, False, None)
        
        # 检查是否点击了网格（种植）
        if self.selected_card:
            grid_pos = self._get_grid_position(x, y)
            if grid_pos:
                row, col = grid_pos
                if self._can_plant_at(row, col, sun_count):
                    self._plant_at(row, col)
                    return (True, True, None)  # 处理了点击，且成功种植
            
            # 点击了无效位置，取消选择
            self._deselect_card()
            return (True, False, None)  # 处理了点击，但没有种植
        
        return (False, False, None)
    
    def _select_card(self, card: PlantCard) -> None:
        """选择卡片"""
        # 取消之前的选择
        if self.selected_card:
            self.selected_card.is_selected = False
        
        # 选择新卡片
        self.selected_card = card
        card.is_selected = True
    
    def _deselect_card(self) -> None:
        """取消选择"""
        if self.selected_card:
            self.selected_card.is_selected = False
            self.selected_card = None
    
    def _get_grid_position(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        """
        将屏幕坐标转换为网格坐标
        
        Returns:
            (row, col) 或 None
        """
        col = int((x - self.GRID_START_X) / self.CELL_WIDTH)
        row = int((y - self.GRID_START_Y) / self.CELL_HEIGHT)
        
        # 检查是否在有效范围内
        if 0 <= row < self.GRID_ROWS and 0 <= col < self.GRID_COLS:
            return (row, col)
        
        return None
    
    def _can_plant_at(self, row: int, col: int, sun_count: int) -> bool:
        """检查是否可以在指定位置种植"""
        # 检查位置是否已被占用
        if (row, col) in self.planted_positions:
            return False
        
        # 检查阳光是否足够
        if not self.selected_card:
            return False
        
        if sun_count < self.selected_card.cost:
            return False
        
        return True
    
    def _plant_at(self, row: int, col: int) -> Optional[Entity]:
        """
        在指定位置种植植物
        
        Returns:
            创建的实体或None
        """
        if not self.selected_card:
            return None
        
        # 计算网格中心位置
        x = self.GRID_START_X + col * self.CELL_WIDTH + self.CELL_WIDTH / 2
        y = self.GRID_START_Y + row * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
        
        # 创建植物实体
        entity = self.entity_factory.create_plant(
            self.selected_card.plant_type,
            x, y,
            row, col
        )
        
        # 记录种植位置
        self.planted_positions[(row, col)] = entity
        
        # 开始卡片冷却
        self.selected_card.start_cooldown()
        
        # 取消选择
        self._deselect_card()
        
        return entity
    
    def remove_plant(self, row: int, col: int) -> None:
        """移除指定位置的植物"""
        if (row, col) in self.planted_positions:
            entity = self.planted_positions[(row, col)]
            self.world.destroy_entity(entity)
            del self.planted_positions[(row, col)]
    
    def get_plant_at(self, row: int, col: int) -> Optional[Entity]:
        """获取指定位置的植物"""
        return self.planted_positions.get((row, col))
    
    def is_position_occupied(self, row: int, col: int) -> bool:
        """检查位置是否被占用"""
        return (row, col) in self.planted_positions
    
    def render(self, mouse_x: float = 0, mouse_y: float = 0) -> None:
        """渲染种植系统UI"""
        # 渲染铲子按钮
        self._render_shovel_button()
        
        # 渲染所有卡片
        for card in self.cards:
            card.render()
        
        # 渲染选中植物的预览
        if self.selected_card:
            self._render_plant_preview(mouse_x, mouse_y)
        
        # 渲染铲子模式的预览
        if self.shovel_mode:
            self._render_shovel_preview()
    
    def _render_shovel_button(self) -> None:
        """渲染铲子按钮"""
        shovel_x = 70
        shovel_y = 550
        shovel_width = 50
        shovel_height = 80
        
        # 确定背景颜色
        if self.shovel_mode:
            bg_color = (180, 140, 100, 240)
            border_color = (255, 200, 100)
            border_width = 3
        else:
            bg_color = (100, 80, 60, 220)
            border_color = (120, 100, 80)
            border_width = 2
        
        # 绘制按钮背景
        half_width = shovel_width / 2
        half_height = shovel_height / 2
        arcade.draw_lrbt_rectangle_filled(
            shovel_x - half_width, shovel_x + half_width,
            shovel_y - half_height, shovel_y + half_height,
            bg_color
        )
        
        # 绘制边框
        arcade.draw_lrbt_rectangle_outline(
            shovel_x - half_width, shovel_x + half_width,
            shovel_y - half_height, shovel_y + half_height,
            border_color, border_width
        )
        
        # 绘制铲子图标
        shovel_icon_y = shovel_y + 10
        # 铲子手柄
        arcade.draw_lrbt_rectangle_filled(
            shovel_x - 3, shovel_x + 3,
            shovel_icon_y, shovel_icon_y + 30,
            (139, 90, 43)
        )
        # 铲子头部
        arcade.draw_triangle_filled(
            shovel_x - 10, shovel_icon_y - 5,
            shovel_x + 10, shovel_icon_y - 5,
            shovel_x, shovel_icon_y - 25,
            (169, 169, 169)
        )
        # 铲子连接部分
        arcade.draw_lrbt_rectangle_filled(
            shovel_x - 4, shovel_x + 4,
            shovel_icon_y - 5, shovel_icon_y + 5,
            (139, 69, 19)
        )
        
        # 绘制文字
        arcade.draw_text(
            "铲子",
            shovel_x, shovel_y - half_height + 12,
            arcade.color.WHITE,
            9,
            anchor_x="center"
        )
    
    def _render_shovel_preview(self) -> None:
        """渲染铲子模式的预览"""
        grid_pos = self._get_grid_position(self.shovel_x, self.shovel_y)
        if grid_pos:
            row, col = grid_pos
            
            # 计算网格位置
            x = self.GRID_START_X + col * self.CELL_WIDTH + self.CELL_WIDTH / 2
            y = self.GRID_START_Y + row * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
            
            # 根据是否有植物选择颜色
            if (row, col) in self.planted_positions:
                color = (255, 100, 100, 150)  # 红色表示可移除
                outline_color = (255, 0, 0)
            else:
                color = (100, 100, 100, 100)  # 灰色表示无植物
                outline_color = (150, 150, 150)
            
            # 绘制预览
            arcade.draw_lrbt_rectangle_filled(
                x - 35, x + 35,
                y - 45, y + 45,
                color
            )
            arcade.draw_lrbt_rectangle_outline(
                x - 35, x + 35,
                y - 45, y + 45,
                outline_color, 3
            )
            
            # 绘制铲子图标跟随鼠标
            arcade.draw_circle_filled(self.shovel_x, self.shovel_y, 20, (200, 150, 100, 180))
            arcade.draw_text("✕", self.shovel_x, self.shovel_y - 5, (255, 255, 255), 16, anchor_x="center")
    
    def _render_plant_preview(self, mouse_x: float, mouse_y: float) -> None:
        """渲染植物种植预览"""
        # 检查是否在网格上
        grid_pos = self._get_grid_position(mouse_x, mouse_y)
        if grid_pos:
            row, col = grid_pos
            
            # 计算网格位置
            x = self.GRID_START_X + col * self.CELL_WIDTH + self.CELL_WIDTH / 2
            y = self.GRID_START_Y + row * self.CELL_HEIGHT + self.CELL_HEIGHT / 2
            
            # 根据是否可以种植选择颜色
            if (row, col) in self.planted_positions:
                color = (255, 0, 0, 100)  # 红色表示不可种植
            else:
                color = (*self.selected_card.color[:3], 100)  # 半透明植物色
            
            # 绘制预览
            arcade.draw_lrbt_rectangle_filled(
                x - 30, x + 30,
                y - 40, y + 40,
                color
            )
            arcade.draw_lrbt_rectangle_outline(
                x - 30, x + 30,
                y - 40, y + 40,
                arcade.color.WHITE, 2
            )
    
    def get_planting_cost(self) -> int:
        """获取当前选中植物的种植成本"""
        if self.selected_card:
            return self.selected_card.cost
        return 0
    
    def clear(self) -> None:
        """清空所有种植的植物"""
        for entity in self.planted_positions.values():
            self.world.destroy_entity(entity)
        self.planted_positions.clear()
        self._deselect_card()
        self.shovel_mode = False
    
    def register_plant_card(self, plant_type: str, cost: int, cooldown: float) -> None:
        """
        注册植物卡片（用于测试和动态配置）
        
        Args:
            plant_type: 植物类型名称
            cost: 阳光成本
            cooldown: 冷却时间（秒）
        """
        # 将字符串转换为PlantType枚举
        try:
            pt = PlantType[plant_type]
            self.card_cooldowns[pt] = cooldown
            
            # 检查是否已存在该类型的卡片
            for card in self.cards:
                if card.plant_type == pt:
                    card.cooldown_duration = cooldown
                    card.cost = cost
                    return
            
            # 如果不存在，创建新卡片
            # 添加到卡片列表（使用默认位置）
            x = 150 + len(self.cards) * 70
            y = 550
            card = PlantCard(pt, x, y)
            card.cost = cost
            card.cooldown_duration = cooldown
            self.cards.append(card)
        except KeyError:
            pass  # 无效的植物类型
    
    def can_plant(self, plant_type: str) -> bool:
        """
        检查是否可以种植指定植物
        
        Args:
            plant_type: 植物类型名称
            
        Returns:
            True if 可以种植
        """
        try:
            pt = PlantType[plant_type]
            for card in self.cards:
                if card.plant_type == pt:
                    return card.is_available
        except KeyError:
            pass
        return False
    
    def plant(self, plant_type: str, row: int, col: int) -> Optional[Entity]:
        """
        在指定位置种植植物
        
        Args:
            plant_type: 植物类型名称
            row: 网格行
            col: 网格列
            
        Returns:
            创建的实体或None
        """
        try:
            pt = PlantType[plant_type]
            
            # 查找对应的卡片
            for card in self.cards:
                if card.plant_type == pt and card.is_available:
                    self._select_card(card)
                    if self._can_plant_at(row, col, float('inf')):  # 假设阳光无限
                        return self._plant_at(row, col)
                    break
        except KeyError:
            pass
        return None
    
    def select_plant_type(self, index: int) -> None:
        """
        通过索引选择植物卡片（用于键盘快捷键）
        
        Args:
            index: 卡片索引（从0开始）
        """
        if 0 <= index < len(self.cards):
            card = self.cards[index]
            if card.is_available:
                self._select_card(card)
                self.shovel_mode = False
    
    def cancel_selection(self) -> None:
        """取消植物选择"""
        self._deselect_card()
    
    def on_mouse_motion(self, x: float, y: float) -> None:
        """
        处理鼠标移动（旧方法名，保持向后兼容）
        新代码应使用 handle_mouse_move
        """
        self.handle_mouse_move(x, y)