"""
测试存档系统
"""

import pytest
import os
import tempfile
import shutil
from src.arcade_game.save_system import (
    SaveSystem, GameSaveData, 
    get_save_system, init_save_system
)


class TestGameSaveData:
    """测试游戏存档数据类"""
    
    def test_initialization(self):
        """测试初始化"""
        data = GameSaveData()
        
        assert data.version == "1.0"
        assert data.current_level == 1
        assert data.sun_count == 50
        assert data.score == 0
        assert data.plants == []
        assert data.zombies == []
        assert data.suns == []
    
    def test_custom_values(self):
        """测试自定义值"""
        data = GameSaveData(
            current_level=3,
            sun_count=200,
            score=1000,
            plants=[{'type': 'sunflower', 'x': 100, 'y': 200}]
        )
        
        assert data.current_level == 3
        assert data.sun_count == 200
        assert data.score == 1000
        assert len(data.plants) == 1


class TestSaveSystem:
    """测试存档系统"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.save_system = SaveSystem(self.temp_dir)
    
    def teardown_method(self):
        """每个测试方法后执行"""
        # 清理临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.save_system.save_dir == self.temp_dir
        assert self.save_system.auto_save_timer == 0.0
        assert os.path.exists(self.temp_dir)
    
    def test_save_and_load_game(self):
        """测试保存和加载游戏"""
        # 创建存档数据
        data = GameSaveData(
            current_level=2,
            sun_count=150,
            score=500,
            plants=[{'type': 'peashooter', 'x': 100, 'y': 200}]
        )
        
        # 保存游戏
        result = self.save_system.save_game(1, data)
        assert result is True
        
        # 加载游戏
        loaded_data = self.save_system.load_game(1)
        assert loaded_data is not None
        assert loaded_data.current_level == 2
        assert loaded_data.sun_count == 150
        assert loaded_data.score == 500
        assert len(loaded_data.plants) == 1
    
    def test_save_invalid_slot(self):
        """测试无效槽位"""
        data = GameSaveData()
        
        # 槽位0无效
        result = self.save_system.save_game(0, data)
        assert result is False
        
        # 槽位6无效
        result = self.save_system.save_game(6, data)
        assert result is False
    
    def test_load_nonexistent_save(self):
        """测试加载不存在的存档"""
        loaded_data = self.save_system.load_game(1)
        assert loaded_data is None
    
    def test_delete_save(self):
        """测试删除存档"""
        # 先保存
        data = GameSaveData()
        self.save_system.save_game(1, data)
        
        # 确认存在
        assert self.save_system.has_save(1)
        
        # 删除
        result = self.save_system.delete_save(1)
        assert result is True
        
        # 确认删除
        assert not self.save_system.has_save(1)
    
    def test_delete_nonexistent_save(self):
        """测试删除不存在的存档"""
        result = self.save_system.delete_save(1)
        assert result is False
    
    def test_get_save_info(self):
        """测试获取存档信息"""
        # 保存游戏
        data = GameSaveData(
            current_level=3,
            score=1000,
            save_name="测试存档"
        )
        self.save_system.save_game(1, data)
        
        # 获取信息
        info = self.save_system.get_save_info(1)
        assert info is not None
        assert info['slot'] == 1
        assert info['current_level'] == 3
        assert info['score'] == 1000
        assert info['save_name'] == "测试存档"
    
    def test_get_all_saves(self):
        """测试获取所有存档"""
        # 创建多个存档
        for i in range(1, 4):
            data = GameSaveData(current_level=i)
            self.save_system.save_game(i, data)
        
        # 获取所有存档
        saves = self.save_system.get_all_saves()
        assert len(saves) == 3
    
    def test_has_save(self):
        """测试检查存档是否存在"""
        # 初始不存在
        assert not self.save_system.has_save(1)
        
        # 保存后存在
        data = GameSaveData()
        self.save_system.save_game(1, data)
        assert self.save_system.has_save(1)
    
    def test_get_next_available_slot(self):
        """测试获取下一个可用槽位"""
        # 初始应该是1
        slot = self.save_system.get_next_available_slot()
        assert slot == 1
        
        # 占用1和2
        data = GameSaveData()
        self.save_system.save_game(1, data)
        self.save_system.save_game(2, data)
        
        # 下一个应该是3
        slot = self.save_system.get_next_available_slot()
        assert slot == 3
    
    def test_auto_save(self):
        """测试自动存档"""
        save_called = [False]
        
        def save_callback(slot):
            save_called[0] = True
        
        # 更新计时器（超过自动存档间隔）
        result = self.save_system.update_auto_save(70.0, save_callback)
        
        assert result is True
        assert save_called[0] is True
    
    def test_export_and_import_save(self):
        """测试导出和导入存档"""
        # 创建并保存游戏
        data = GameSaveData(current_level=5, score=2000)
        self.save_system.save_game(1, data)
        
        # 导出
        export_path = os.path.join(self.temp_dir, "export.json")
        result = self.save_system.export_save(1, export_path)
        assert result is True
        assert os.path.exists(export_path)
        
        # 导入到槽位2
        result = self.save_system.import_save(export_path, 2)
        assert result is True
        
        # 验证导入的数据
        loaded_data = self.save_system.load_game(2)
        assert loaded_data.current_level == 5
        assert loaded_data.score == 2000


class TestGlobalSaveSystem:
    """测试全局存档系统"""
    
    def test_get_save_system(self):
        """测试获取全局实例"""
        import src.arcade_game.save_system as save_module
        save_module._save_system = None
        
        # 获取实例
        manager1 = get_save_system()
        assert manager1 is not None
        
        # 再次获取应该是同一个实例
        manager2 = get_save_system()
        assert manager1 is manager2
    
    def test_init_save_system(self):
        """测试初始化存档系统"""
        import src.arcade_game.save_system as save_module
        
        # 初始化
        manager = init_save_system()
        assert manager is not None
        
        # 再次初始化应该是新实例
        old_manager = save_module._save_system
        new_manager = init_save_system()
        assert new_manager is not old_manager


class TestSaveSystemIntegration:
    """测试存档系统集成"""
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.temp_dir = tempfile.mkdtemp()
        self.save_system = SaveSystem(self.temp_dir)
    
    def teardown_method(self):
        """每个测试方法后执行"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_save_workflow(self):
        """测试完整存档流程"""
        # 1. 创建游戏数据
        data = GameSaveData(
            current_level=3,
            sun_count=300,
            score=1500,
            plants=[
                {'type': 'sunflower', 'x': 100, 'y': 200},
                {'type': 'peashooter', 'x': 180, 'y': 200}
            ],
            zombies=[
                {'type': 'normal', 'x': 500, 'y': 200}
            ]
        )
        
        # 2. 保存游戏
        result = self.save_system.save_game(1, data)
        assert result is True
        
        # 3. 获取存档信息
        info = self.save_system.get_save_info(1)
        assert info['current_level'] == 3
        assert info['score'] == 1500
        
        # 4. 加载游戏
        loaded_data = self.save_system.load_game(1)
        assert loaded_data is not None
        assert len(loaded_data.plants) == 2
        assert len(loaded_data.zombies) == 1
        
        # 5. 导出存档
        export_path = os.path.join(self.temp_dir, "backup.json")
        result = self.save_system.export_save(1, export_path)
        assert result is True
        
        # 6. 删除原存档
        result = self.save_system.delete_save(1)
        assert result is True
        
        # 7. 从导出文件导入
        result = self.save_system.import_save(export_path, 2)
        assert result is True
        
        # 8. 验证导入的数据
        imported_data = self.save_system.load_game(2)
        assert imported_data.current_level == 3
        assert imported_data.sun_count == 300
    
    def test_multiple_saves_management(self):
        """测试多存档管理"""
        # 创建5个存档
        for i in range(1, 6):
            data = GameSaveData(
                current_level=i,
                score=i * 100,
                save_name=f"存档 {i}"
            )
            self.save_system.save_game(i, data)
        
        # 获取所有存档
        saves = self.save_system.get_all_saves()
        assert len(saves) == 5
        
        # 检查存档槽位已满
        slot = self.save_system.get_next_available_slot()
        assert slot == -1
        
        # 删除中间的一个
        self.save_system.delete_save(3)
        
        # 检查现在有空位
        slot = self.save_system.get_next_available_slot()
        assert slot == 3
