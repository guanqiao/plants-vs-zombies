"""
成就系统测试

测试成就管理器的所有功能
"""

import pytest
import os
import tempfile
import shutil
from src.core.achievement_system import (
    AchievementManager,
    AchievementType,
    Achievement,
    get_achievement_manager,
    init_achievement_manager,
    ACHIEVEMENT_DEFINITIONS
)


class TestAchievement:
    """测试成就数据类"""
    
    def test_achievement_creation(self):
        """测试成就创建"""
        achievement = Achievement(
            achievement_type=AchievementType.FIRST_WIN,
            name="初次胜利",
            description="完成第一关",
            max_progress=1
        )
        
        assert achievement.achievement_type == AchievementType.FIRST_WIN
        assert achievement.name == "初次胜利"
        assert achievement.description == "完成第一关"
        assert achievement.max_progress == 1
        assert achievement.progress == 0
        assert not achievement.is_unlocked
    
    def test_achievement_to_dict(self):
        """测试成就转换为字典"""
        achievement = Achievement(
            achievement_type=AchievementType.FIRST_WIN,
            name="初次胜利",
            description="完成第一关",
            max_progress=1
        )
        
        data = achievement.to_dict()
        
        assert data['achievement_type'] == 'FIRST_WIN'
        assert data['name'] == '初次胜利'
        assert data['description'] == '完成第一关'
        assert data['max_progress'] == 1
    
    def test_achievement_from_dict(self):
        """测试从字典创建成就"""
        data = {
            'achievement_type': 'FIRST_WIN',
            'name': '初次胜利',
            'description': '完成第一关',
            'icon': 'icon.png',
            'is_unlocked': True,
            'unlock_time': '2026-02-21 12:00:00',
            'progress': 1,
            'max_progress': 1,
            'is_hidden': False
        }
        
        achievement = Achievement.from_dict(data)
        
        assert achievement.achievement_type == AchievementType.FIRST_WIN
        assert achievement.name == '初次胜利'
        assert achievement.is_unlocked
        assert achievement.unlock_time == '2026-02-21 12:00:00'


class TestAchievementManager:
    """测试成就管理器"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """创建成就管理器实例"""
        return AchievementManager(save_dir=temp_dir)
    
    def test_initialization(self, manager):
        """测试初始化"""
        assert len(manager.achievements) == len(ACHIEVEMENT_DEFINITIONS)
        
        # 检查所有成就都已初始化
        for achievement_type in AchievementType:
            assert achievement_type in manager.achievements
            achievement = manager.achievements[achievement_type]
            assert achievement.name != ""
            assert achievement.description != ""
    
    def test_unlock_achievement(self, manager):
        """测试解锁成就"""
        # 解锁成就
        result = manager.unlock(AchievementType.FIRST_WIN)
        assert result is True
        
        # 检查成就已解锁
        assert manager.is_unlocked(AchievementType.FIRST_WIN)
        
        # 再次解锁应该返回False
        result = manager.unlock(AchievementType.FIRST_WIN)
        assert result is False
    
    def test_unlock_unknown_achievement(self, manager):
        """测试解锁未知成就"""
        # 使用不存在的成就类型应该返回False
        result = manager.unlock("UNKNOWN_TYPE")  # type: ignore
        assert result is False
    
    def test_update_progress(self, manager):
        """测试更新进度"""
        # 更新进度
        result = manager.update_progress(AchievementType.KILL_100_ZOMBIES, 50)
        assert result is False  # 未达到目标
        assert manager.get_progress(AchievementType.KILL_100_ZOMBIES) == 50
        
        # 达到目标
        result = manager.update_progress(AchievementType.KILL_100_ZOMBIES, 100)
        assert result is True  # 解锁了成就
        assert manager.is_unlocked(AchievementType.KILL_100_ZOMBIES)
    
    def test_add_progress(self, manager):
        """测试增加进度"""
        # 增加进度
        result = manager.add_progress(AchievementType.KILL_100_ZOMBIES, 50)
        assert result is False
        assert manager.get_progress(AchievementType.KILL_100_ZOMBIES) == 50
        
        # 继续增加
        result = manager.add_progress(AchievementType.KILL_100_ZOMBIES, 50)
        assert result is True  # 解锁了成就
        assert manager.is_unlocked(AchievementType.KILL_100_ZOMBIES)
    
    def test_get_achievement(self, manager):
        """测试获取成就信息"""
        achievement = manager.get_achievement(AchievementType.FIRST_WIN)
        
        assert achievement is not None
        assert achievement.achievement_type == AchievementType.FIRST_WIN
        assert achievement.name == "初次胜利"
    
    def test_get_all_achievements(self, manager):
        """测试获取所有成就"""
        achievements = manager.get_all_achievements()
        
        assert len(achievements) == len(ACHIEVEMENT_DEFINITIONS)
    
    def test_get_unlocked_achievements(self, manager):
        """测试获取已解锁成就"""
        # 初始状态
        unlocked = manager.get_unlocked_achievements()
        assert len(unlocked) == 0
        
        # 解锁一个成就
        manager.unlock(AchievementType.FIRST_WIN)
        unlocked = manager.get_unlocked_achievements()
        assert len(unlocked) == 1
        assert unlocked[0].achievement_type == AchievementType.FIRST_WIN
    
    def test_get_locked_achievements(self, manager):
        """测试获取未解锁成就"""
        locked = manager.get_locked_achievements()
        assert len(locked) == len(ACHIEVEMENT_DEFINITIONS)
        
        # 解锁一个成就
        manager.unlock(AchievementType.FIRST_WIN)
        locked = manager.get_locked_achievements()
        assert len(locked) == len(ACHIEVEMENT_DEFINITIONS) - 1
    
    def test_get_counts(self, manager):
        """测试获取计数"""
        assert manager.get_total_count() == len(ACHIEVEMENT_DEFINITIONS)
        assert manager.get_unlock_count() == 0
        
        manager.unlock(AchievementType.FIRST_WIN)
        assert manager.get_unlock_count() == 1
    
    def test_get_completion_percentage(self, manager):
        """测试获取完成百分比"""
        assert manager.get_completion_percentage() == 0.0
        
        manager.unlock(AchievementType.FIRST_WIN)
        expected_percentage = (1 / len(ACHIEVEMENT_DEFINITIONS)) * 100
        assert abs(manager.get_completion_percentage() - expected_percentage) < 0.01
    
    def test_unlock_callback(self, manager):
        """测试解锁回调"""
        callback_called = False
        unlocked_achievement = None
        
        def on_unlock(achievement):
            nonlocal callback_called, unlocked_achievement
            callback_called = True
            unlocked_achievement = achievement
        
        # 注册回调
        manager.register_unlock_callback(on_unlock)
        
        # 解锁成就
        manager.unlock(AchievementType.FIRST_WIN)
        
        assert callback_called is True
        assert unlocked_achievement is not None
        assert unlocked_achievement.achievement_type == AchievementType.FIRST_WIN
    
    def test_save_and_load(self, temp_dir):
        """测试保存和加载"""
        # 创建管理器并解锁一些成就
        manager1 = AchievementManager(save_dir=temp_dir)
        manager1.unlock(AchievementType.FIRST_WIN)
        manager1.update_progress(AchievementType.KILL_100_ZOMBIES, 50)
        
        # 保存
        result = manager1.save_progress()
        assert result is True
        
        # 创建新管理器并加载
        manager2 = AchievementManager(save_dir=temp_dir)
        
        # 检查加载的数据
        assert manager2.is_unlocked(AchievementType.FIRST_WIN)
        assert manager2.get_progress(AchievementType.KILL_100_ZOMBIES) == 50
    
    def test_reset_all(self, manager):
        """测试重置所有成就"""
        # 解锁一些成就
        manager.unlock(AchievementType.FIRST_WIN)
        manager.update_progress(AchievementType.KILL_100_ZOMBIES, 50)
        
        # 重置
        manager.reset_all()
        
        # 检查所有成就已重置
        assert manager.get_unlock_count() == 0
        assert manager.get_progress(AchievementType.KILL_100_ZOMBIES) == 0
        assert not manager.is_unlocked(AchievementType.FIRST_WIN)
    
    def test_reset_single_achievement(self, manager):
        """测试重置单个成就"""
        # 解锁成就
        manager.unlock(AchievementType.FIRST_WIN)
        assert manager.is_unlocked(AchievementType.FIRST_WIN)
        
        # 重置
        result = manager.reset_progress(AchievementType.FIRST_WIN)
        assert result is True
        
        # 检查已重置
        assert not manager.is_unlocked(AchievementType.FIRST_WIN)
        assert manager.get_progress(AchievementType.FIRST_WIN) == 0
    
    def test_achievement_definitions(self):
        """测试成就定义配置"""
        # 检查所有成就类型都有定义
        for achievement_type in AchievementType:
            assert achievement_type in ACHIEVEMENT_DEFINITIONS
            config = ACHIEVEMENT_DEFINITIONS[achievement_type]
            assert 'name' in config
            assert 'description' in config
            assert 'max_progress' in config


class TestAchievementManagerSingleton:
    """测试成就管理器单例"""
    
    def test_get_achievement_manager(self):
        """测试获取单例"""
        # 重置单例
        import src.core.achievement_system as achievement_module
        achievement_module._achievement_manager = None
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 获取单例
            manager1 = get_achievement_manager(temp_dir)
            manager2 = get_achievement_manager(temp_dir)
            
            # 应该是同一个实例
            assert manager1 is manager2
        finally:
            shutil.rmtree(temp_dir)
    
    def test_init_achievement_manager(self):
        """测试初始化成就管理器"""
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 初始化应该创建新实例
            manager1 = init_achievement_manager(temp_dir)
            manager2 = init_achievement_manager(temp_dir)
            
            # init_achievement_manager每次都会创建新实例（用于重置）
            assert manager1 is not manager2
            assert isinstance(manager1, AchievementManager)
            assert isinstance(manager2, AchievementManager)
        finally:
            shutil.rmtree(temp_dir)
