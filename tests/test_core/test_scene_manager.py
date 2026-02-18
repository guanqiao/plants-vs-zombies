import pytest
from abc import ABC, abstractmethod


class TestScene:
    """场景基类测试"""

    def test_scene_is_abstract(self):
        """测试Scene是抽象类"""
        from src.core.scene import Scene
        from abc import ABC
        
        assert issubclass(Scene, ABC)

    def test_scene_has_required_methods(self):
        """测试Scene有必需的方法"""
        from src.core.scene import Scene
        
        assert hasattr(Scene, 'enter')
        assert hasattr(Scene, 'exit')
        assert hasattr(Scene, 'update')
        assert hasattr(Scene, 'render')
        assert hasattr(Scene, 'handle_event')


class TestSceneManager:
    """场景管理器测试"""

    def test_scene_manager_initialization(self):
        """测试场景管理器初始化"""
        from src.core.scene_manager import SceneManager
        
        manager = SceneManager()
        
        assert manager is not None
        assert manager.current_scene is None

    def test_scene_manager_register_scene(self):
        """测试注册场景"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene = MagicMock()
        
        manager.register_scene('menu', mock_scene)
        
        assert 'menu' in manager._scenes

    def test_scene_manager_change_scene(self):
        """测试切换场景"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene1 = MagicMock()
        mock_scene2 = MagicMock()
        
        manager.register_scene('menu', mock_scene1)
        manager.register_scene('playing', mock_scene2)
        
        manager.change_scene('menu')
        
        assert manager.current_scene == mock_scene1
        mock_scene1.enter.assert_called_once()

    def test_scene_manager_change_scene_calls_exit(self):
        """测试切换场景时调用exit"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene1 = MagicMock()
        mock_scene2 = MagicMock()
        
        manager.register_scene('menu', mock_scene1)
        manager.register_scene('playing', mock_scene2)
        
        manager.change_scene('menu')
        manager.change_scene('playing')
        
        mock_scene1.exit.assert_called_once()
        mock_scene2.enter.assert_called_once()

    def test_scene_manager_update(self):
        """测试更新当前场景"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene = MagicMock()
        
        manager.register_scene('menu', mock_scene)
        manager.change_scene('menu')
        manager.update(0.016)
        
        mock_scene.update.assert_called_once_with(0.016)

    def test_scene_manager_render(self):
        """测试渲染当前场景"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene = MagicMock()
        mock_screen = MagicMock()
        
        manager.register_scene('menu', mock_scene)
        manager.change_scene('menu')
        manager.render(mock_screen)
        
        mock_scene.render.assert_called_once_with(mock_screen)

    def test_scene_manager_handle_event(self):
        """测试处理事件"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene = MagicMock()
        mock_event = MagicMock()
        
        manager.register_scene('menu', mock_scene)
        manager.change_scene('menu')
        manager.handle_event(mock_event)
        
        mock_scene.handle_event.assert_called_once_with(mock_event)

    def test_scene_manager_no_current_scene(self):
        """测试没有当前场景时的行为"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_screen = MagicMock()
        mock_event = MagicMock()
        
        manager.update(0.016)
        manager.render(mock_screen)
        manager.handle_event(mock_event)
        
        assert True

    def test_scene_manager_change_to_nonexistent_scene(self):
        """测试切换到不存在的场景"""
        from src.core.scene_manager import SceneManager
        
        manager = SceneManager()
        
        manager.change_scene('nonexistent')
        
        assert manager.current_scene is None

    def test_scene_manager_has_scene(self):
        """测试检查场景是否存在"""
        from src.core.scene_manager import SceneManager
        from unittest.mock import MagicMock
        
        manager = SceneManager()
        mock_scene = MagicMock()
        
        manager.register_scene('menu', mock_scene)
        
        assert manager.has_scene('menu')
        assert not manager.has_scene('nonexistent')
