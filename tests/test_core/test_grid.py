import pytest


class TestGrid:
    """网格系统测试"""

    def test_grid_initialization(self):
        """测试网格初始化"""
        from src.core.grid import Grid
        
        grid = Grid()
        assert grid.ROWS == 5
        assert grid.COLS == 9

    def test_grid_cell_size(self):
        """测试格子大小"""
        from src.core.grid import Grid
        
        grid = Grid()
        assert grid.CELL_WIDTH == 80
        assert grid.CELL_HEIGHT == 100

    def test_grid_get_cell_position(self):
        """测试获取格子位置"""
        from src.core.grid import Grid
        
        grid = Grid()
        
        pos = grid.get_cell_position(0, 0)
        assert pos == (grid.OFFSET_X, grid.OFFSET_Y)
        
        pos = grid.get_cell_position(1, 1)
        assert pos == (grid.OFFSET_X + grid.CELL_WIDTH, grid.OFFSET_Y + grid.CELL_HEIGHT)

    def test_grid_get_cell_from_position(self):
        """测试从坐标获取格子"""
        from src.core.grid import Grid
        
        grid = Grid()
        
        cell = grid.get_cell_from_position(grid.OFFSET_X + 40, grid.OFFSET_Y + 50)
        assert cell == (0, 0)
        
        cell = grid.get_cell_from_position(grid.OFFSET_X + 120, grid.OFFSET_Y + 150)
        assert cell == (1, 1)

    def test_grid_is_valid_cell(self):
        """测试格子是否有效"""
        from src.core.grid import Grid
        
        grid = Grid()
        
        assert grid.is_valid_cell(0, 0) == True
        assert grid.is_valid_cell(4, 8) == True
        assert grid.is_valid_cell(-1, 0) == False
        assert grid.is_valid_cell(0, 9) == False
        assert grid.is_valid_cell(5, 0) == False

    def test_grid_place_plant(self):
        """测试放置植物"""
        from src.core.grid import Grid
        from unittest.mock import MagicMock
        
        grid = Grid()
        
        plant = MagicMock()
        plant.row = 2
        plant.col = 3
        
        result = grid.place_plant(2, 3, plant)
        assert result == True
        assert grid.get_plant_at(2, 3) == plant

    def test_grid_place_plant_occupied(self):
        """测试放置植物到已占用格子"""
        from src.core.grid import Grid
        from unittest.mock import MagicMock
        
        grid = Grid()
        
        plant1 = MagicMock()
        plant2 = MagicMock()
        
        grid.place_plant(2, 3, plant1)
        result = grid.place_plant(2, 3, plant2)
        assert result == False
        assert grid.get_plant_at(2, 3) == plant1

    def test_grid_remove_plant(self):
        """测试移除植物"""
        from src.core.grid import Grid
        from unittest.mock import MagicMock
        
        grid = Grid()
        
        plant = MagicMock()
        grid.place_plant(2, 3, plant)
        
        removed = grid.remove_plant(2, 3)
        assert removed == plant
        assert grid.get_plant_at(2, 3) is None

    def test_grid_remove_plant_empty(self):
        """测试从空格子移除植物"""
        from src.core.grid import Grid
        
        grid = Grid()
        
        removed = grid.remove_plant(2, 3)
        assert removed is None

    def test_grid_is_cell_occupied(self):
        """测试格子是否被占用"""
        from src.core.grid import Grid
        from unittest.mock import MagicMock
        
        grid = Grid()
        
        assert grid.is_cell_occupied(2, 3) == False
        
        plant = MagicMock()
        grid.place_plant(2, 3, plant)
        assert grid.is_cell_occupied(2, 3) == True
