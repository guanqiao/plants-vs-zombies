"""
种植系统 - 处理植物种植的所有逻辑

包括：
- 植物卡片UI
- 鼠标点击种植
- 阳光消耗验证
- 网格位置检查
"""

from typing import Optional, Dict, List, Tuple
import arcade
from ..ecs import World, Entity
from ..ecs.components import PlantType, PLANT_CONFIGS
from .entity_factory import EntityFactory


class PlantCard:
    """
    植物卡片类
    
    表示UI上的一个植物选择卡片
    """
    
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
        self.cooldown_timer = 0.0
        self.cooldown_duration = config.get('attack_cooldown', 1.5)
    
    def contains_point(self, px: float, py: float) -> bool:
        """检查点是否在卡片内"""
        half_width = self.width / 2
        half_height = self.height / 2
        return (self.x - half_width <= px <= self.x + half_width and
                self.y - half_height <= py <= self.y + half_height)
    
    def update(self, dt: float, sun_count: int) -> None:
        """更新卡片状态"""
        # 更新冷却
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.cooldown_timer = 0
        
        # 检查是否可用（阳光足够且不在冷却）
        self.is_available = (sun_count >= self.cost and 
                            self.cooldown_timer <= 0)
    
    def start_cooldown(self) -> None:
        """开始冷却"""
        self.cooldown_timer = self.cooldown_duration
    
    def render(self) -> None:
        """渲染卡片"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        # 背景色（根据可用性变化）
        if self.is_available:
            bg_color = self.color
            alpha = 255
        else:
            bg_color = (100, 100, 100)  # 灰色表示不可用
            alpha = 150
        
        # 绘制卡片背景
        arcade.draw_lrtb_rectangle_filled(
            self.x - half_width, self.x + half_width,
            self.y + half_height, self.y - half_height,
            (*bg_color, alpha)
        )
        
        # 绘制选中边框
        if self.is_selected:
            arcade.draw_lrtb_rectangle_outline(
                self.x - half_width, self.x + half_width,
                self.y + half_height, self.y - half_height,
                arcade.color.YELLOW, 3
            )
        else:
            arcade.draw_lrtb_rectangle_outline(
                self.x - half_width, self.x + half_width,
                self.y + half_height, self.y - half_height,
                arcade.color.BLACK, 2
            )
        
        # 绘制植物名称（简化显示）
        arcade.draw_text(
            self.name[:4],  # 显示前4个字符
            self.x, self.y + half_height - 15,
            arcade.color.WHITE, 10,
            anchor_x="center"
        )
        
        # 绘制阳光成本
        arcade.draw_text(
            f"{self.cost}",
            self.x, self.y - half_height + 10,
            arcade.color.YELLOW, 12,
            anchor_x="center"
        )
        
        # 绘制冷却遮罩
        if self.cooldown_timer > 0:
            cooldown_percent = self.cooldown_timer / self.cooldown_duration
            cooldown_height = self.height * cooldown_percent
            
            arcade.draw_lrtb_rectangle_filled(
                self.x - half_width, self.x + half_width,
                self.y - half_height + cooldown_height, self.y - half_height,
                (0, 0, 0, 180)
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
        
        # 已种植的植物位置 (row, col) -> Entity
        self.planted_positions: Dict[Tuple[int, int], Entity] = {}
        
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
    
    def handle_mouse_press(self, x: float, y: float, sun_count: int) -> bool:
        """
        处理鼠标点击
        
        Returns:
            是否处理了点击事件
        """
        # 检查是否点击了卡片
        for card in self.cards:
            if card.contains_point(x, y):
                if card.is_available:
                    self._select_card(card)
                    return True
                return False
        
        # 检查是否点击了网格（种植）
        if self.selected_card:
            grid_pos = self._get_grid_position(x, y)
            if grid_pos:
                row, col = grid_pos
                if self._can_plant_at(row, col, sun_count):
                    self._plant_at(row, col)
                    return True
            
            # 点击了无效位置，取消选择
            self._deselect_card()
            return True
        
        return False
    
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
    
    def render(self) -> None:
        """渲染种植系统UI"""
        # 渲染所有卡片
        for card in self.cards:
            card.render()
        
        # 渲染选中植物的预览
        if self.selected_card:
            self._render_plant_preview()
    
    def _render_plant_preview(self) -> None:
        """渲染植物种植预览"""
        # 获取鼠标位置
        mouse_x, mouse_y = arcade.get_mouse_position()
        
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
            arcade.draw_rectangle_filled(
                x, y, 60, 80, color
            )
            arcade.draw_rectangle_outline(
                x, y, 60, 80, arcade.color.WHITE, 2
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