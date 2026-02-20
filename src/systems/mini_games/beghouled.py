"""
宝石迷阵小游戏 - Beghouled
类似消消乐的玩法，交换相邻植物形成三个或更多连线
"""
from typing import List, Tuple, Optional, Set
from .base_game import BaseMiniGame
from .types import MiniGameType


class BeghouledGame(BaseMiniGame):
    """
    宝石迷阵小游戏
    
    8x8网格，玩家交换相邻植物形成连线消除
    """
    
    GRID_SIZE = 8
    MATCH_MIN = 3  # 最小连线数
    
    def __init__(self):
        super().__init__(MiniGameType.BEGHOULED)
        self.grid: List[List[Optional[str]]] = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.score = 0
        self.moves = 0
        self._initialize_grid()
    
    def _initialize_grid(self):
        """初始化游戏网格"""
        import random
        plant_types = ['peashooter', 'sunflower', 'wallnut', 'cherry_bomb', 'snow_pea']
        
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                self.grid[row][col] = random.choice(plant_types)
    
    def update(self, dt: float):
        """更新游戏状态"""
        super().update(dt)
        
        # 检查并处理连线
        matches = self._find_all_matches()
        if matches:
            self._remove_matches(matches)
            self._fill_empty_cells()
    
    def handle_click(self, row: int, col: int) -> bool:
        """
        处理点击事件
        
        Args:
            row: 行索引
            col: 列索引
            
        Returns:
            True if 操作有效
        """
        if not self.is_running:
            return False
        
        if self.selected_cell is None:
            # 选择第一个格子
            self.selected_cell = (row, col)
            return True
        else:
            # 尝试交换
            if self._can_swap(self.selected_cell, (row, col)):
                if self._swap_cells(self.selected_cell, (row, col)):
                    self.moves += 1
                    self.selected_cell = None
                    return True
            
            # 交换失败，重新选择
            self.selected_cell = (row, col)
            return False
    
    def _can_swap(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> bool:
        """
        检查两个格子是否可以交换
        
        Args:
            cell1: 第一个格子坐标
            cell2: 第二个格子坐标
            
        Returns:
            True if 可以交换（相邻）
        """
        row1, col1 = cell1
        row2, col2 = cell2
        
        # 检查是否相邻
        return abs(row1 - row2) + abs(col1 - col2) == 1
    
    def _swap_cells(self, cell1: Tuple[int, int], cell2: Tuple[int, int]) -> bool:
        """
        交换两个格子的内容
        
        Args:
            cell1: 第一个格子坐标
            cell2: 第二个格子坐标
            
        Returns:
            True if 交换后形成连线
        """
        row1, col1 = cell1
        row2, col2 = cell2
        
        # 临时交换
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
        
        # 检查是否形成连线
        matches = self._find_all_matches()
        if matches:
            # 更新分数
            self.score += len(matches) * 10
            return True
        else:
            # 交换无效，恢复原状
            self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
            return False
    
    def _find_all_matches(self) -> Set[Tuple[int, int]]:
        """
        查找所有连线
        
        Returns:
            所有形成连线的格子坐标集合
        """
        matches = set()
        
        # 检查横向连线
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE - self.MATCH_MIN + 1):
                match = self._find_horizontal_match(row, col)
                if match:
                    matches.update(match)
        
        # 检查纵向连线
        for row in range(self.GRID_SIZE - self.MATCH_MIN + 1):
            for col in range(self.GRID_SIZE):
                match = self._find_vertical_match(row, col)
                if match:
                    matches.update(match)
        
        return matches
    
    def _find_horizontal_match(self, row: int, start_col: int) -> Optional[List[Tuple[int, int]]]:
        """
        查找横向连线
        
        Args:
            row: 行索引
            start_col: 起始列索引
            
        Returns:
            连线格子列表或None
        """
        plant_type = self.grid[row][start_col]
        if plant_type is None:
            return None
        
        match = [(row, start_col)]
        
        for col in range(start_col + 1, self.GRID_SIZE):
            if self.grid[row][col] == plant_type:
                match.append((row, col))
            else:
                break
        
        return match if len(match) >= self.MATCH_MIN else None
    
    def _find_vertical_match(self, start_row: int, col: int) -> Optional[List[Tuple[int, int]]]:
        """
        查找纵向连线
        
        Args:
            start_row: 起始行索引
            col: 列索引
            
        Returns:
            连线格子列表或None
        """
        plant_type = self.grid[start_row][col]
        if plant_type is None:
            return None
        
        match = [(start_row, col)]
        
        for row in range(start_row + 1, self.GRID_SIZE):
            if self.grid[row][col] == plant_type:
                match.append((row, col))
            else:
                break
        
        return match if len(match) >= self.MATCH_MIN else None
    
    def _remove_matches(self, matches: Set[Tuple[int, int]]):
        """
        移除连线格子
        
        Args:
            matches: 要移除的格子坐标集合
        """
        for row, col in matches:
            self.grid[row][col] = None
    
    def _fill_empty_cells(self):
        """填充空格"""
        import random
        plant_types = ['peashooter', 'sunflower', 'wallnut', 'cherry_bomb', 'snow_pea']
        
        # 让上方格子下落
        for col in range(self.GRID_SIZE):
            # 收集该列非空格子
            column = []
            for row in range(self.GRID_SIZE):
                if self.grid[row][col] is not None:
                    column.append(self.grid[row][col])
            
            # 从底部重新填充
            for row in range(self.GRID_SIZE - 1, -1, -1):
                if column:
                    self.grid[row][col] = column.pop()
                else:
                    # 生成新植物
                    self.grid[row][col] = random.choice(plant_types)
    
    def get_grid(self) -> List[List[Optional[str]]]:
        """
        获取当前网格状态
        
        Returns:
            网格状态副本
        """
        return [row[:] for row in self.grid]
    
    def get_score(self) -> int:
        """获取当前分数"""
        return self.score
    
    def get_moves(self) -> int:
        """获取移动次数"""
        return self.moves
    
    def get_selected_cell(self) -> Optional[Tuple[int, int]]:
        """获取当前选中的格子"""
        return self.selected_cell
