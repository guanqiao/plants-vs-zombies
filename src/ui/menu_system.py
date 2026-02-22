"""
菜单系统 - 管理所有游戏菜单

包括：
- 主菜单
- 关卡选择
- 暂停菜单
- 游戏结束/胜利界面
"""

from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Tuple
import arcade


class MenuButton:
    """
    菜单按钮
    
    可点击的菜单按钮，支持悬停效果
    """
    
    def __init__(self, text: str, x: float, y: float, 
                 width: float = 200, height: float = 50,
                 callback: Optional[Callable] = None):
        """
        初始化按钮
        
        Args:
            text: 按钮文本
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            callback: 点击回调函数
        """
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.callback = callback
        self.is_hovered = False
        
        # 颜色配置
        self.color_normal = (100, 150, 100)
        self.color_hover = (150, 200, 150)
        self.color_text = (255, 255, 255)
        
    def render(self):
        """渲染按钮"""
        color = self.color_hover if self.is_hovered else self.color_normal
        
        # 绘制按钮背景
        arcade.draw_rect_filled(arcade.XYWH(self.x, self.y, self.width, self.height), color
        )
        
        # 绘制边框
        arcade.draw_rect_outline(arcade.XYWH(self.x, self.y, self.width, self.height), (50, 100, 50), 2
        )
        
        # 绘制文本
        arcade.draw_text(
            self.text, self.x, self.y,
            self.color_text, 20,
            anchor_x="center", anchor_y="center"
        )
    
    def check_hover(self, mouse_x: float, mouse_y: float) -> bool:
        """
        检查鼠标悬停
        
        Args:
            mouse_x: 鼠标X坐标
            mouse_y: 鼠标Y坐标
            
        Returns:
            是否悬停
        """
        half_width = self.width / 2
        half_height = self.height / 2
        
        self.is_hovered = (
            self.x - half_width <= mouse_x <= self.x + half_width and
            self.y - half_height <= mouse_y <= self.y + half_height
        )
        
        return self.is_hovered
    
    def on_click(self):
        """处理点击事件"""
        if self.callback:
            self.callback()


class BaseMenu(ABC):
    """
    菜单基类
    
    所有菜单的抽象基类
    """
    
    def __init__(self, window_width: float, window_height: float):
        """
        初始化菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
        """
        self.window_width = window_width
        self.window_height = window_height
        self.buttons: List[MenuButton] = []
        self.is_visible = False
        
    @abstractmethod
    def setup(self):
        """设置菜单（创建按钮等）"""
        pass
    
    def show(self):
        """显示菜单"""
        self.is_visible = True
        self.setup()
    
    def hide(self):
        """隐藏菜单"""
        self.is_visible = False
    
    def render(self):
        """渲染菜单"""
        if not self.is_visible:
            return
        
        # 绘制半透明背景
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (0, 0, 0, 180)
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()
    
    def on_mouse_motion(self, x: float, y: float):
        """
        处理鼠标移动
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
        """
        if not self.is_visible:
            return
        
        for button in self.buttons:
            button.check_hover(x, y)
    
    def on_mouse_click(self, x: float, y: float):
        """
        处理鼠标点击
        
        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            
        Returns:
            是否处理了点击
        """
        if not self.is_visible:
            return False
        
        for button in self.buttons:
            if button.check_hover(x, y):
                button.on_click()
                return True
        
        return False


class MainMenu(BaseMenu):
    """
    主菜单
    
    游戏启动时显示的主菜单
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_start_game: Callable,
                 on_level_select: Callable,
                 on_settings: Callable,
                 on_quit: Callable):
        """
        初始化主菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_start_game: 开始游戏回调
            on_level_select: 关卡选择回调
            on_settings: 设置回调
            on_quit: 退出回调
        """
        super().__init__(window_width, window_height)
        self.on_start_game = on_start_game
        self.on_level_select = on_level_select
        self.on_settings = on_settings
        self.on_quit = on_quit
        
    def setup(self):
        """设置主菜单按钮"""
        self.buttons.clear()
        
        center_x = self.window_width / 2
        start_y = self.window_height / 2 + 100
        spacing = 70
        
        # 标题
        self.title = "植物大战僵尸"
        
        # 开始游戏按钮
        self.buttons.append(MenuButton(
            "开始游戏", center_x, start_y,
            callback=self.on_start_game
        ))
        
        # 关卡选择按钮
        self.buttons.append(MenuButton(
            "关卡选择", center_x, start_y - spacing,
            callback=self.on_level_select
        ))
        
        # 设置按钮
        self.buttons.append(MenuButton(
            "设置", center_x, start_y - spacing * 2,
            callback=self.on_settings
        ))
        
        # 退出按钮
        self.buttons.append(MenuButton(
            "退出游戏", center_x, start_y - spacing * 3,
            callback=self.on_quit
        ))
    
    def render(self):
        """渲染主菜单"""
        if not self.is_visible:
            return
        
        # 绘制背景
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (50, 100, 50)
        )
        
        # 绘制标题
        arcade.draw_text(
            self.title,
            self.window_width / 2, self.window_height - 100,
            (255, 255, 0), 48,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()


class LevelSelectMenu(BaseMenu):
    """
    关卡选择菜单
    
    选择要玩的关卡
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_level_selected: Callable[[int], None],
                 on_back: Callable,
                 max_unlocked_level: int = 1):
        """
        初始化关卡选择菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_level_selected: 关卡选择回调
            on_back: 返回回调
            max_unlocked_level: 最大解锁关卡
        """
        super().__init__(window_width, window_height)
        self.on_level_selected = on_level_selected
        self.on_back = on_back
        self.max_unlocked_level = max_unlocked_level
        self.total_levels = 7
        
    def setup(self):
        """设置关卡选择按钮"""
        self.buttons.clear()
        
        # 关卡按钮
        button_width = 80
        button_height = 80
        cols = 4
        start_x = self.window_width / 2 - (cols * button_width) / 2 + button_width / 2
        start_y = self.window_height / 2 + 50
        
        for i in range(self.total_levels):
            level = i + 1
            col = i % cols
            row = i // cols
            
            x = start_x + col * (button_width + 20)
            y = start_y - row * (button_height + 20)
            
            # 根据解锁状态设置颜色
            is_unlocked = level <= self.max_unlocked_level
            
            button = MenuButton(
                f"{level}", x, y, button_width, button_height,
                callback=lambda l=level: self._on_level_click(l) if is_unlocked else None
            )
            
            if not is_unlocked:
                button.color_normal = (100, 100, 100)
                button.color_hover = (100, 100, 100)
            
            self.buttons.append(button)
        
        # 返回按钮
        self.buttons.append(MenuButton(
            "返回", self.window_width / 2, 100,
            callback=self.on_back
        ))
    
    def _on_level_click(self, level: int):
        """处理关卡点击"""
        if level <= self.max_unlocked_level:
            self.on_level_selected(level)
    
    def render(self):
        """渲染关卡选择菜单"""
        if not self.is_visible:
            return
        
        # 绘制背景
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (50, 80, 50)
        )
        
        # 绘制标题
        arcade.draw_text(
            "选择关卡",
            self.window_width / 2, self.window_height - 80,
            (255, 255, 255), 36,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()
        
        # 绘制说明
        arcade.draw_text(
            "灰色关卡未解锁",
            self.window_width / 2, 50,
            (150, 150, 150), 16,
            anchor_x="center", anchor_y="center"
        )


class PauseMenu(BaseMenu):
    """
    暂停菜单
    
    游戏暂停时显示的菜单
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_resume: Callable,
                 on_restart: Callable,
                 on_main_menu: Callable):
        """
        初始化暂停菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_resume: 继续游戏回调
            on_restart: 重新开始回调
            on_main_menu: 返回主菜单回调
        """
        super().__init__(window_width, window_height)
        self.on_resume = on_resume
        self.on_restart = on_restart
        self.on_main_menu = on_main_menu
        
    def setup(self):
        """设置暂停菜单按钮"""
        self.buttons.clear()
        
        center_x = self.window_width / 2
        center_y = self.window_height / 2
        spacing = 60
        
        # 继续游戏按钮
        self.buttons.append(MenuButton(
            "继续游戏", center_x, center_y + spacing,
            callback=self.on_resume
        ))
        
        # 重新开始按钮
        self.buttons.append(MenuButton(
            "重新开始", center_x, center_y,
            callback=self.on_restart
        ))
        
        # 返回主菜单按钮
        self.buttons.append(MenuButton(
            "返回主菜单", center_x, center_y - spacing,
            callback=self.on_main_menu
        ))
    
    def render(self):
        """渲染暂停菜单"""
        if not self.is_visible:
            return
        
        # 绘制半透明遮罩
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (0, 0, 0, 150)
        )
        
        # 绘制标题
        arcade.draw_text(
            "游戏暂停",
            self.window_width / 2, self.window_height / 2 + 150,
            (255, 255, 255), 36,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()


class DifficultySelectMenu(BaseMenu):
    """
    难度选择菜单
    
    选择游戏难度
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_difficulty_selected: Callable[[str], None],
                 on_back: Callable):
        """
        初始化难度选择菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_difficulty_selected: 难度选择回调，参数为难度标识 'easy', 'normal', 'hard'
            on_back: 返回回调
        """
        super().__init__(window_width, window_height)
        self.on_difficulty_selected = on_difficulty_selected
        self.on_back = on_back
        self.selected_difficulty = "normal"
        
        # 难度描述
        self.difficulty_descriptions = {
            "easy": {
                "name": "简单",
                "color": (100, 200, 100),
                "desc": "初始阳光: 150 | 阳光价值: 50 | 僵尸较弱"
            },
            "normal": {
                "name": "普通",
                "color": (200, 200, 100),
                "desc": "初始阳光: 100 | 阳光价值: 25 | 标准体验"
            },
            "hard": {
                "name": "困难",
                "color": (200, 100, 100),
                "desc": "初始阳光: 50 | 阳光价值: 25 | 僵尸更强"
            }
        }
        
    def setup(self):
        """设置难度选择菜单按钮"""
        self.buttons.clear()
        
        center_x = self.window_width / 2
        start_y = self.window_height / 2 + 80
        spacing = 70
        
        # 简单难度按钮
        easy_button = MenuButton(
            "简单", center_x, start_y,
            callback=lambda: self._select_difficulty("easy")
        )
        easy_button.color_normal = (100, 180, 100)
        easy_button.color_hover = (120, 220, 120)
        self.buttons.append(easy_button)
        
        # 普通难度按钮
        normal_button = MenuButton(
            "普通", center_x, start_y - spacing,
            callback=lambda: self._select_difficulty("normal")
        )
        normal_button.color_normal = (180, 180, 100)
        normal_button.color_hover = (220, 220, 120)
        self.buttons.append(normal_button)
        
        # 困难难度按钮
        hard_button = MenuButton(
            "困难", center_x, start_y - spacing * 2,
            callback=lambda: self._select_difficulty("hard")
        )
        hard_button.color_normal = (180, 100, 100)
        hard_button.color_hover = (220, 120, 120)
        self.buttons.append(hard_button)
        
        # 返回按钮
        self.buttons.append(MenuButton(
            "返回", center_x, start_y - spacing * 3 - 20,
            callback=self.on_back
        ))
    
    def _select_difficulty(self, difficulty: str):
        """处理难度选择"""
        self.selected_difficulty = difficulty
        if self.on_difficulty_selected:
            self.on_difficulty_selected(difficulty)
    
    def render(self):
        """渲染难度选择菜单"""
        if not self.is_visible:
            return
        
        # 绘制背景
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (50, 80, 50)
        )
        
        # 绘制标题
        arcade.draw_text(
            "选择难度",
            self.window_width / 2, self.window_height - 80,
            (255, 255, 255), 36,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()
        
        # 绘制难度说明
        desc_y = 120
        arcade.draw_text(
            "简单：初始阳光150，阳光价值50，僵尸较弱",
            self.window_width / 2, desc_y,
            (150, 220, 150), 14,
            anchor_x="center", anchor_y="center"
        )
        arcade.draw_text(
            "普通：初始阳光100，阳光价值25，标准体验",
            self.window_width / 2, desc_y - 20,
            (220, 220, 150), 14,
            anchor_x="center", anchor_y="center"
        )
        arcade.draw_text(
            "困难：初始阳光50，阳光价值25，僵尸更强更快",
            self.window_width / 2, desc_y - 40,
            (220, 150, 150), 14,
            anchor_x="center", anchor_y="center"
        )


class SettingsMenu(BaseMenu):
    """
    设置菜单
    
    游戏设置：音量控制、显示设置等
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_back: Callable,
                 on_master_volume_change: Optional[Callable[[float], None]] = None,
                 on_sfx_volume_change: Optional[Callable[[float], None]] = None,
                 on_music_volume_change: Optional[Callable[[float], None]] = None):
        """
        初始化设置菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_back: 返回回调
            on_master_volume_change: 主音量变化回调
            on_sfx_volume_change: 音效音量变化回调
            on_music_volume_change: 音乐音量变化回调
        """
        super().__init__(window_width, window_height)
        self.on_back = on_back
        self.on_master_volume_change = on_master_volume_change
        self.on_sfx_volume_change = on_sfx_volume_change
        self.on_music_volume_change = on_music_volume_change
        
        # 音量设置 (0.0 - 1.0)
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.music_volume = 0.5
        
        # 当前正在拖动的滑块
        self.dragging_slider: Optional[str] = None
    
    def setup(self):
        """设置设置菜单"""
        self.buttons.clear()
        
        center_x = self.window_width / 2
        start_y = self.window_height - 100
        spacing = 60
        
        # 返回按钮
        self.buttons.append(MenuButton(
            "返回", center_x, 100,
            callback=self.on_back
        ))
    
    def render(self):
        """渲染设置菜单"""
        if not self.is_visible:
            return
        
        # 绘制背景
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), (50, 80, 50)
        )
        
        # 绘制标题
        arcade.draw_text(
            "设置",
            self.window_width / 2, self.window_height - 80,
            (255, 255, 255), 36,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制音量控制
        center_x = self.window_width / 2
        start_y = self.window_height - 180
        spacing = 80
        
        # 主音量
        self._render_volume_slider(
            center_x, start_y,
            "主音量", self.master_volume,
            "master"
        )
        
        # 音效音量
        self._render_volume_slider(
            center_x, start_y - spacing,
            "音效音量", self.sfx_volume,
            "sfx"
        )
        
        # 音乐音量
        self._render_volume_slider(
            center_x, start_y - spacing * 2,
            "音乐音量", self.music_volume,
            "music"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()
    
    def _render_volume_slider(self, x: float, y: float, label: str, 
                               value: float, slider_id: str):
        """渲染音量滑块"""
        slider_width = 300
        slider_height = 20
        
        # 标签
        arcade.draw_text(
            label,
            x - slider_width / 2 - 10, y + 5,
            (255, 255, 255), 20,
            anchor_x="right", anchor_y="center"
        )
        
        # 滑块背景
        arcade.draw_rect_filled(arcade.XYWH(x, y, slider_width, slider_height), (50, 50, 50)
        )
        
        # 滑块填充
        fill_width = slider_width * value
        arcade.draw_rect_filled(arcade.XYWH(x - (slider_width - fill_width) / 2, y, fill_width, slider_height), (100, 200, 100)
        )
        
        # 滑块边框
        arcade.draw_rect_outline(arcade.XYWH(x, y, slider_width, slider_height), (100, 100, 100), 2
        )
        
        # 滑块手柄
        handle_x = x - slider_width / 2 + fill_width
        arcade.draw_circle_filled(
            handle_x, y, 12,
            (200, 200, 200)
        )
        arcade.draw_circle_outline(
            handle_x, y, 12,
            (255, 255, 255), 2
        )
        
        # 数值显示
        arcade.draw_text(
            f"{int(value * 100)}%",
            x + slider_width / 2 + 20, y,
            (255, 255, 255), 18,
            anchor_x="left", anchor_y="center"
        )
    
    def on_mouse_motion(self, x: float, y: float):
        """处理鼠标移动"""
        super().on_mouse_motion(x, y)
        
        if self.dragging_slider:
            self._update_slider_value(x, self.dragging_slider)
    
    def on_mouse_click(self, x: float, y: float) -> bool:
        """处理鼠标点击"""
        if not self.is_visible:
            return False
        
        # 先检查按钮
        for button in self.buttons:
            if button.check_hover(x, y):
                button.on_click()
                return True
        
        # 检查滑块点击
        center_x = self.window_width / 2
        start_y = self.window_height - 180
        spacing = 80
        
        if self._is_on_slider(x, y, center_x, start_y, 300, 20):
            self.dragging_slider = "master"
            self._update_slider_value(x, "master")
            return True
        elif self._is_on_slider(x, y, center_x, start_y - spacing, 300, 20):
            self.dragging_slider = "sfx"
            self._update_slider_value(x, "sfx")
            return True
        elif self._is_on_slider(x, y, center_x, start_y - spacing * 2, 300, 20):
            self.dragging_slider = "music"
            self._update_slider_value(x, "music")
            return True
        
        return False
    
    def _is_on_slider(self, mouse_x: float, mouse_y: float,
                      slider_x: float, slider_y: float,
                      slider_width: float, slider_height: float) -> bool:
        """检查鼠标是否在滑块上"""
        half_width = slider_width / 2 + 20
        half_height = slider_height / 2 + 10
        return (slider_x - half_width <= mouse_x <= slider_x + half_width and
                slider_y - half_height <= mouse_y <= slider_y + half_height)
    
    def _update_slider_value(self, mouse_x: float, slider_id: str):
        """更新滑块值"""
        center_x = self.window_width / 2
        slider_width = 300
        
        # 计算相对位置
        relative_x = mouse_x - (center_x - slider_width / 2)
        value = max(0.0, min(1.0, relative_x / slider_width))
        
        if slider_id == "master":
            self.master_volume = value
            if self.on_master_volume_change:
                self.on_master_volume_change(value)
        elif slider_id == "sfx":
            self.sfx_volume = value
            if self.on_sfx_volume_change:
                self.on_sfx_volume_change(value)
        elif slider_id == "music":
            self.music_volume = value
            if self.on_music_volume_change:
                self.on_music_volume_change(value)


class GameOverMenu(BaseMenu):
    """
    游戏结束菜单
    
    游戏胜利或失败时显示的菜单
    """
    
    def __init__(self, window_width: float, window_height: float,
                 on_restart: Callable,
                 on_main_menu: Callable):
        """
        初始化游戏结束菜单
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
            on_restart: 重新开始回调
            on_main_menu: 返回主菜单回调
        """
        super().__init__(window_width, window_height)
        self.on_restart = on_restart
        self.on_main_menu = on_main_menu
        self.is_victory = False
        self.score = 0
        
    def show_result(self, is_victory: bool, score: int):
        """
        显示游戏结果
        
        Args:
            is_victory: 是否胜利
            score: 最终得分
        """
        self.is_victory = is_victory
        self.score = score
        self.show()
        
    def setup(self):
        """设置游戏结束菜单按钮"""
        self.buttons.clear()
        
        center_x = self.window_width / 2
        center_y = self.window_height / 2
        spacing = 60
        
        # 重新开始按钮
        self.buttons.append(MenuButton(
            "重新开始", center_x, center_y,
            callback=self.on_restart
        ))
        
        # 返回主菜单按钮
        self.buttons.append(MenuButton(
            "返回主菜单", center_x, center_y - spacing,
            callback=self.on_main_menu
        ))
    
    def render(self):
        """渲染游戏结束菜单"""
        if not self.is_visible:
            return
        
        # 绘制背景
        color = (50, 100, 50) if self.is_victory else (100, 50, 50)
        arcade.draw_rect_filled(arcade.XYWH(self.window_width / 2, self.window_height / 2, self.window_width, self.window_height), color
        )
        
        # 绘制标题
        title = "胜利！" if self.is_victory else "游戏结束"
        title_color = (255, 255, 0) if self.is_victory else (255, 100, 100)
        
        arcade.draw_text(
            title,
            self.window_width / 2, self.window_height / 2 + 150,
            title_color, 48,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制得分
        arcade.draw_text(
            f"得分: {self.score}",
            self.window_width / 2, self.window_height / 2 + 80,
            (255, 255, 255), 24,
            anchor_x="center", anchor_y="center"
        )
        
        # 绘制按钮
        for button in self.buttons:
            button.render()


class MenuSystem:
    """
    菜单系统管理器
    
    统一管理所有菜单
    """
    
    def __init__(self, window_width: float, window_height: float):
        """
        初始化菜单系统
        
        Args:
            window_width: 窗口宽度
            window_height: 窗口高度
        """
        self.window_width = window_width
        self.window_height = window_height
        
        # 回调函数（需要在GameWindow中设置）
        self.on_start_game: Optional[Callable] = None
        self.on_level_select: Optional[Callable[[int], None]] = None
        self.on_settings: Optional[Callable] = None
        self.on_quit: Optional[Callable] = None
        self.on_resume: Optional[Callable] = None
        self.on_restart: Optional[Callable] = None
        self.on_main_menu: Optional[Callable] = None
        self.on_difficulty_selected: Optional[Callable[[str], None]] = None
        
        # 音量变化回调
        self.on_master_volume_change: Optional[Callable[[float], None]] = None
        self.on_sfx_volume_change: Optional[Callable[[float], None]] = None
        self.on_music_volume_change: Optional[Callable[[float], None]] = None
        
        # 菜单实例
        self.main_menu: Optional[MainMenu] = None
        self.level_select_menu: Optional[LevelSelectMenu] = None
        self.difficulty_select_menu: Optional[DifficultySelectMenu] = None
        self.pause_menu: Optional[PauseMenu] = None
        self.game_over_menu: Optional[GameOverMenu] = None
        self.settings_menu: Optional[SettingsMenu] = None
        
        # 当前显示的菜单
        self.current_menu: Optional[BaseMenu] = None
        
    def setup(self):
        """设置菜单系统"""
        # 主菜单
        self.main_menu = MainMenu(
            self.window_width, self.window_height,
            self._on_start_game,
            self._on_level_select,
            self._on_settings,
            self._on_quit
        )
        
        # 关卡选择菜单
        self.level_select_menu = LevelSelectMenu(
            self.window_width, self.window_height,
            self._on_level_selected,
            self._on_back_to_main
        )
        
        # 难度选择菜单
        self.difficulty_select_menu = DifficultySelectMenu(
            self.window_width, self.window_height,
            self._on_difficulty_selected,
            self._on_back_to_main_from_difficulty
        )
        
        # 暂停菜单
        self.pause_menu = PauseMenu(
            self.window_width, self.window_height,
            self._on_resume,
            self._on_restart,
            self._on_main_menu
        )
        
        # 游戏结束菜单
        self.game_over_menu = GameOverMenu(
            self.window_width, self.window_height,
            self._on_restart,
            self._on_main_menu
        )
        
        # 设置菜单
        self.settings_menu = SettingsMenu(
            self.window_width, self.window_height,
            self._on_back_to_main_from_settings,
            self._on_master_volume_change,
            self._on_sfx_volume_change,
            self._on_music_volume_change
        )
    
    def show_main_menu(self):
        """显示主菜单"""
        self.current_menu = self.main_menu
        self.main_menu.show()
    
    def show_level_select(self, max_unlocked_level: int = 1):
        """显示关卡选择菜单"""
        self.level_select_menu.max_unlocked_level = max_unlocked_level
        self.current_menu = self.level_select_menu
        self.level_select_menu.show()
    
    def show_difficulty_select(self):
        """显示难度选择菜单"""
        self.current_menu = self.difficulty_select_menu
        self.difficulty_select_menu.show()
    
    def show_pause_menu(self):
        """显示暂停菜单"""
        self.current_menu = self.pause_menu
        self.pause_menu.show()
    
    def show_game_over(self, is_victory: bool, score: int):
        """显示游戏结束菜单"""
        self.current_menu = self.game_over_menu
        self.game_over_menu.show_result(is_victory, score)
    
    def show_settings(self):
        """显示设置菜单"""
        self.current_menu = self.settings_menu
        self.settings_menu.show()
    
    def hide_current_menu(self):
        """隐藏当前菜单"""
        if self.current_menu:
            self.current_menu.hide()
            self.current_menu = None
    
    def render(self):
        """渲染当前菜单"""
        if self.current_menu:
            self.current_menu.render()
    
    def on_mouse_motion(self, x: float, y: float):
        """处理鼠标移动"""
        if self.current_menu:
            self.current_menu.on_mouse_motion(x, y)
    
    def on_mouse_click(self, x: float, y: float) -> bool:
        """处理鼠标点击"""
        if self.current_menu:
            return self.current_menu.on_mouse_click(x, y)
        return False
    
    # 回调函数包装器
    def _on_start_game(self):
        # 先显示难度选择菜单
        self.show_difficulty_select()
    
    def _on_level_select(self):
        if self.on_level_select:
            self.show_level_select()
    
    def _on_settings(self):
        if self.on_settings:
            self.on_settings()
    
    def _on_quit(self):
        if self.on_quit:
            self.on_quit()
    
    def _on_level_selected(self, level: int):
        # 选择关卡后也显示难度选择
        self._pending_level = level
        self.show_difficulty_select()
    
    def _on_difficulty_selected(self, difficulty: str):
        """难度选择回调"""
        if self.on_difficulty_selected:
            self.on_difficulty_selected(difficulty)
    
    def _on_back_to_main(self):
        self.show_main_menu()
    
    def _on_back_to_main_from_difficulty(self):
        """从难度选择返回"""
        self.show_main_menu()
    
    def _on_resume(self):
        self.hide_current_menu()
        if self.on_resume:
            self.on_resume()
    
    def _on_restart(self):
        self.hide_current_menu()
        if self.on_restart:
            self.on_restart()
    
    def _on_main_menu(self):
        self.hide_current_menu()
        if self.on_main_menu:
            self.on_main_menu()
    
    def _on_back_to_main_from_settings(self):
        """从设置返回主菜单"""
        self.show_main_menu()
    
    def _on_master_volume_change(self, value: float):
        """主音量变化回调"""
        if self.on_master_volume_change:
            self.on_master_volume_change(value)
    
    def _on_sfx_volume_change(self, value: float):
        """音效音量变化回调"""
        if self.on_sfx_volume_change:
            self.on_sfx_volume_change(value)
    
    def _on_music_volume_change(self, value: float):
        """音乐音量变化回调"""
        if self.on_music_volume_change:
            self.on_music_volume_change(value)
