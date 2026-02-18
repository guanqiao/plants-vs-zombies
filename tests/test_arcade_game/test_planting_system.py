"""
测试种植系统
"""

import pytest
from src.ecs import World
from src.arcade_game.entity_factory import EntityFactory
from src.arcade_game.planting_system import PlantingSystem, PlantCard
from src.ecs.components import PlantType


class TestPlantCard:
    """测试植物卡片"""
    
    def test_card_initialization(self):
        """测试卡片初始化"""
        card = PlantCard(PlantType.PEASHOOTER, x=100, y=200)
        
        assert card.plant_type == PlantType.PEASHOOTER
        assert card.x == 100
        assert card.y == 200
        assert card.cost == 100  # 豌豆射手成本
        assert not card.is_selected
        assert card.is_available
    
    def test_card_contains_point(self):
        """测试点是否在卡片内"""
        card = PlantCard(PlantType.SUNFLOWER, x=100, y=100, width=60, height=80)
        
        # 卡片中心点
        assert card.contains_point(100, 100)
        
        # 卡片内部
        assert card.contains_point(90, 90)
        assert card.contains_point(110, 110)
        
        # 卡片外部
        assert not card.contains_point(50, 50)
        assert not card.contains_point(200, 200)
    
    def test_card_availability(self):
        """测试卡片可用性"""
        card = PlantCard(PlantType.WALLNUT, x=100, y=100)
        card.cooldown_duration = 5.0  # 设置较长的冷却时间
        
        # 初始状态：阳光足够，可用
        card.update(0.016, sun_count=100)
        assert card.is_available
        
        # 阳光不足
        card.update(0.016, sun_count=10)
        assert not card.is_available
        
        # 恢复阳光后应该可用
        card.update(0.016, sun_count=100)
        assert card.is_available
        
        # 开始冷却后不可用
        card.start_cooldown()
        card.update(0.016, sun_count=100)
        assert not card.is_available
    
    def test_card_cooldown(self):
        """测试卡片冷却"""
        card = PlantCard(PlantType.PEASHOOTER, x=100, y=100)
        card.cooldown_duration = 1.0
        
        # 确保初始状态可用
        card.update(0.016, sun_count=1000)
        assert card.is_available
        
        # 开始冷却
        card.start_cooldown()
        assert card.cooldown_timer == 1.0
        card.update(0.016, sun_count=1000)  # 更新状态
        assert not card.is_available
        
        # 冷却进行中（使用近似值）
        card.update(0.5, sun_count=1000)
        assert 0.48 <= card.cooldown_timer <= 0.52  # 允许浮点误差
        assert not card.is_available
        
        # 冷却结束
        card.update(0.6, sun_count=1000)  # 多更新一点确保结束
        assert card.cooldown_timer == 0
        assert card.is_available


class TestPlantingSystem:
    """测试种植系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.planting_system = PlantingSystem(self.world, self.entity_factory)
    
    def test_init_cards(self):
        """测试初始化卡片"""
        assert len(self.planting_system.cards) == 7  # 7种植物卡片
        
        # 检查卡片类型
        plant_types = [card.plant_type for card in self.planting_system.cards]
        assert PlantType.SUNFLOWER in plant_types
        assert PlantType.PEASHOOTER in plant_types
        assert PlantType.WALLNUT in plant_types
    
    def test_get_grid_position(self):
        """测试获取网格位置"""
        # 网格起点
        pos = self.planting_system._get_grid_position(100, 50)
        assert pos == (0, 0)
        
        # 网格中心
        pos = self.planting_system._get_grid_position(140, 100)
        assert pos == (0, 0)
        
        # 第二个格子
        pos = self.planting_system._get_grid_position(180, 150)
        assert pos == (1, 1)
        
        # 网格外部（负坐标）
        pos = self.planting_system._get_grid_position(-10, -10)
        assert pos is None
    
    def test_can_plant_at(self):
        """测试是否可以种植"""
        # 选择豌豆射手卡片
        peashooter_card = self.planting_system.cards[1]  # 豌豆射手
        self.planting_system._select_card(peashooter_card)
        
        # 阳光足够，位置空闲
        assert self.planting_system._can_plant_at(0, 0, sun_count=100)
        
        # 阳光不足
        assert not self.planting_system._can_plant_at(0, 0, sun_count=10)
        
        # 种植后，位置被占用
        self.planting_system._plant_at(0, 0)
        assert not self.planting_system._can_plant_at(0, 0, sun_count=100)
    
    def test_plant_at(self):
        """测试在指定位置种植"""
        # 选择向日葵卡片
        sunflower_card = self.planting_system.cards[0]
        self.planting_system._select_card(sunflower_card)
        
        # 种植
        entity = self.planting_system._plant_at(2, 3)
        
        # 验证实体创建
        assert entity is not None
        assert (2, 3) in self.planting_system.planted_positions
        
        # 验证位置记录
        stored_entity = self.planting_system.get_plant_at(2, 3)
        assert stored_entity == entity
        
        # 验证卡片冷却
        assert sunflower_card.cooldown_timer > 0
        
        # 验证取消选择
        assert self.planting_system.selected_card is None
    
    def test_remove_plant(self):
        """测试移除植物"""
        # 先种植
        sunflower_card = self.planting_system.cards[0]
        self.planting_system._select_card(sunflower_card)
        entity = self.planting_system._plant_at(1, 2)
        
        # 验证已种植
        assert (1, 2) in self.planting_system.planted_positions
        
        # 移除
        self.planting_system.remove_plant(1, 2)
        
        # 验证已移除
        assert (1, 2) not in self.planting_system.planted_positions
        assert self.planting_system.get_plant_at(1, 2) is None
    
    def test_select_and_deselect_card(self):
        """测试选择和取消选择卡片"""
        card1 = self.planting_system.cards[0]
        card2 = self.planting_system.cards[1]
        
        # 选择卡片1
        self.planting_system._select_card(card1)
        assert self.planting_system.selected_card == card1
        assert card1.is_selected
        
        # 选择卡片2，卡片1应该取消选择
        self.planting_system._select_card(card2)
        assert self.planting_system.selected_card == card2
        assert not card1.is_selected
        assert card2.is_selected
        
        # 取消选择
        self.planting_system._deselect_card()
        assert self.planting_system.selected_card is None
        assert not card2.is_selected
    
    def test_is_position_occupied(self):
        """测试位置是否被占用"""
        # 初始状态：空闲
        assert not self.planting_system.is_position_occupied(0, 0)
        
        # 种植后：占用
        sunflower_card = self.planting_system.cards[0]
        self.planting_system._select_card(sunflower_card)
        self.planting_system._plant_at(0, 0)
        
        assert self.planting_system.is_position_occupied(0, 0)
    
    def test_clear(self):
        """测试清空所有植物"""
        # 种植多个植物（需要重新选择卡片）
        sunflower_card = self.planting_system.cards[0]
        
        self.planting_system._select_card(sunflower_card)
        self.planting_system._plant_at(0, 0)
        
        self.planting_system._select_card(sunflower_card)
        self.planting_system._plant_at(1, 1)
        
        # 验证已种植
        assert len(self.planting_system.planted_positions) == 2
        
        # 清空
        self.planting_system.clear()
        
        # 验证已清空
        assert len(self.planting_system.planted_positions) == 0
    
    def test_handle_mouse_press_card(self):
        """测试鼠标点击卡片"""
        # 点击第一个卡片（向日葵）
        card = self.planting_system.cards[0]
        result = self.planting_system.handle_mouse_press(card.x, card.y, sun_count=100)
        
        assert result is True
        assert self.planting_system.selected_card == card
        assert card.is_selected
    
    def test_handle_mouse_press_plant(self):
        """测试鼠标点击种植"""
        # 先选择卡片
        card = self.planting_system.cards[0]
        self.planting_system._select_card(card)
        
        # 点击网格位置（第一格中心）
        grid_x = 100 + 40  # GRID_START_X + CELL_WIDTH/2
        grid_y = 50 + 50   # GRID_START_Y + CELL_HEIGHT/2
        
        result = self.planting_system.handle_mouse_press(grid_x, grid_y, sun_count=100)
        
        assert result is True
        assert (0, 0) in self.planting_system.planted_positions
        assert self.planting_system.selected_card is None  # 种植后取消选择
    
    def test_get_planting_cost(self):
        """测试获取种植成本"""
        # 未选择卡片
        assert self.planting_system.get_planting_cost() == 0
        
        # 选择豌豆射手
        peashooter_card = self.planting_system.cards[1]
        self.planting_system._select_card(peashooter_card)
        
        assert self.planting_system.get_planting_cost() == 100
        
        # 选择向日葵
        sunflower_card = self.planting_system.cards[0]
        self.planting_system._select_card(sunflower_card)
        
        assert self.planting_system.get_planting_cost() == 50


class TestPlantingSystemIntegration:
    """测试种植系统集成"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.world = World()
        self.entity_factory = EntityFactory(self.world)
        self.planting_system = PlantingSystem(self.world, self.entity_factory)
    
    def test_full_planting_workflow(self):
        """测试完整的种植流程"""
        sun_count = 200
        
        # 1. 选择向日葵卡片
        sunflower_card = self.planting_system.cards[0]
        result = self.planting_system.handle_mouse_press(sunflower_card.x, sunflower_card.y, sun_count)
        assert result is True
        
        # 2. 在网格上种植
        grid_x = 100 + 40
        grid_y = 50 + 50
        result = self.planting_system.handle_mouse_press(grid_x, grid_y, sun_count)
        assert result is True
        
        # 3. 验证种植成功
        assert (0, 0) in self.planting_system.planted_positions
        
        # 4. 验证阳光消耗（成本50）
        assert self.planting_system.get_planting_cost() == 0
        
        # 5. 尝试在同一位置再次种植（应该失败）
        peashooter_card = self.planting_system.cards[1]
        self.planting_system._select_card(peashooter_card)
        can_plant = self.planting_system._can_plant_at(0, 0, sun_count=1000)
        assert not can_plant
    
    def test_multiple_plants(self):
        """测试种植多个植物"""
        sunflower_card = self.planting_system.cards[0]
        
        # 种植3个向日葵
        positions = [(0, 0), (0, 1), (0, 2)]
        
        for row, col in positions:
            self.planting_system._select_card(sunflower_card)
            
            # 计算网格位置
            x = 100 + col * 80 + 40
            y = 50 + row * 100 + 50
            
            self.planting_system.handle_mouse_press(x, y, sun_count=1000)
        
        # 验证所有位置都有植物
        for row, col in positions:
            assert self.planting_system.is_position_occupied(row, col)
        
        # 验证种植了3个植物
        assert len(self.planting_system.planted_positions) == 3