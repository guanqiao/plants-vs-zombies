"""
存档系统 - 管理游戏存档和加载

包括：
- 游戏状态保存
- 游戏状态加载
- 自动存档
- 多存档槽位
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from ..core.logger import get_module_logger


logger = get_module_logger(__name__)


@dataclass
class GameSaveData:
    """
    游戏存档数据
    
    存储游戏状态的所有数据
    """
    # 版本号（用于兼容性检查）
    version: str = "1.0"
    
    # 存档元数据
    save_name: str = ""
    save_time: str = ""
    play_time: float = 0.0  # 游戏时长（秒）
    
    # 游戏状态
    current_level: int = 1
    sun_count: int = 50
    score: int = 0
    
    # 植物数据
    plants: List[Dict[str, Any]] = None
    
    # 僵尸数据
    zombies: List[Dict[str, Any]] = None
    
    # 阳光数据
    suns: List[Dict[str, Any]] = None
    
    # 波次数据
    wave_index: int = 0
    wave_timer: float = 0.0
    
    def __post_init__(self):
        if self.plants is None:
            self.plants = []
        if self.zombies is None:
            self.zombies = []
        if self.suns is None:
            self.suns = []


class SaveSystem:
    """
    存档系统
    
    管理游戏存档的保存和加载
    """
    
    # 存档文件扩展名
    SAVE_EXTENSION = ".json"
    
    # 最大存档数量
    MAX_SAVE_SLOTS = 5
    
    # 自动存档间隔（秒）
    AUTO_SAVE_INTERVAL = 60.0
    
    def __init__(self, save_dir: str = "saves"):
        """
        初始化存档系统
        
        Args:
            save_dir: 存档目录
        """
        self.save_dir = save_dir
        self.auto_save_timer = 0.0
        
        # 确保存档目录存在
        self._ensure_save_dir()
    
    def _ensure_save_dir(self) -> None:
        """确保存档目录存在"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def _get_save_path(self, slot: int) -> str:
        """
        获取存档文件路径
        
        Args:
            slot: 存档槽位（1-5）
            
        Returns:
            存档文件路径
        """
        return os.path.join(self.save_dir, f"save_{slot}{self.SAVE_EXTENSION}")
    
    def save_game(self, slot: int, data: GameSaveData) -> bool:
        """
        保存游戏
        
        Args:
            slot: 存档槽位（1-5）
            data: 游戏存档数据
            
        Returns:
            是否保存成功
        """
        if not 1 <= slot <= self.MAX_SAVE_SLOTS:
            logger.warning(f"无效的存档槽位: {slot}")
            return False
        
        try:
            # 更新存档时间
            data.save_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 转换为字典
            save_dict = asdict(data)
            
            # 保存到文件
            save_path = self._get_save_path(slot)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"游戏已保存到槽位 {slot}")
            return True
            
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, slot: int) -> Optional[GameSaveData]:
        """
        加载游戏
        
        Args:
            slot: 存档槽位（1-5）
            
        Returns:
            游戏存档数据，如果加载失败则返回None
        """
        if not 1 <= slot <= self.MAX_SAVE_SLOTS:
            logger.warning(f"无效的存档槽位: {slot}")
            return None
        
        save_path = self._get_save_path(slot)
        
        if not os.path.exists(save_path):
            logger.debug(f"存档槽位 {slot} 不存在")
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_dict = json.load(f)
            
            # 版本兼容性检查
            version = save_dict.get('version', '1.0')
            if version != GameSaveData().version:
                logger.warning(f"存档版本 {version} 与当前版本不兼容")
            
            # 转换为数据类
            data = GameSaveData(**save_dict)
            
            logger.info(f"游戏已从槽位 {slot} 加载")
            return data
            
        except Exception as e:
            logger.error(f"加载游戏失败: {e}")
            return None
    
    def delete_save(self, slot: int) -> bool:
        """
        删除存档
        
        Args:
            slot: 存档槽位（1-5）
            
        Returns:
            是否删除成功
        """
        if not 1 <= slot <= self.MAX_SAVE_SLOTS:
            logger.warning(f"无效的存档槽位: {slot}")
            return False
        
        save_path = self._get_save_path(slot)
        
        if not os.path.exists(save_path):
            logger.debug(f"存档槽位 {slot} 不存在")
            return False
        
        try:
            os.remove(save_path)
            logger.info(f"存档槽位 {slot} 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除存档失败: {e}")
            return False
    
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        获取存档信息（不加载完整数据）
        
        Args:
            slot: 存档槽位（1-5）
            
        Returns:
            存档信息字典
        """
        if not 1 <= slot <= self.MAX_SAVE_SLOTS:
            return None
        
        save_path = self._get_save_path(slot)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_dict = json.load(f)
            
            # 只返回基本信息
            return {
                'slot': slot,
                'save_name': save_dict.get('save_name', f'存档 {slot}'),
                'save_time': save_dict.get('save_time', '未知'),
                'current_level': save_dict.get('current_level', 1),
                'score': save_dict.get('score', 0),
                'play_time': save_dict.get('play_time', 0.0)
            }
            
        except Exception as e:
            logger.error(f"获取存档信息失败: {e}")
            return None
    
    def get_all_saves(self) -> List[Dict[str, Any]]:
        """
        获取所有存档信息
        
        Returns:
            存档信息列表
        """
        saves = []
        
        for slot in range(1, self.MAX_SAVE_SLOTS + 1):
            info = self.get_save_info(slot)
            if info:
                saves.append(info)
        
        return saves
    
    def has_save(self, slot: int) -> bool:
        """
        检查存档槽位是否存在
        
        Args:
            slot: 存档槽位（1-5）
            
        Returns:
            是否存在
        """
        if not 1 <= slot <= self.MAX_SAVE_SLOTS:
            return False
        
        save_path = self._get_save_path(slot)
        return os.path.exists(save_path)
    
    def get_next_available_slot(self) -> int:
        """
        获取下一个可用的存档槽位
        
        Returns:
            槽位号（1-5），如果没有可用槽位则返回-1
        """
        for slot in range(1, self.MAX_SAVE_SLOTS + 1):
            if not self.has_save(slot):
                return slot
        
        return -1
    
    def update_auto_save(self, dt: float, save_callback) -> bool:
        """
        更新自动存档计时器
        
        Args:
            dt: 时间增量
            save_callback: 保存回调函数
            
        Returns:
            是否执行了自动存档
        """
        self.auto_save_timer += dt
        
        if self.auto_save_timer >= self.AUTO_SAVE_INTERVAL:
            self.auto_save_timer = 0.0
            
            # 使用第一个槽位作为自动存档
            if save_callback:
                save_callback(1)
                return True
        
        return False
    
    def export_save(self, slot: int, export_path: str) -> bool:
        """
        导出存档到指定路径
        
        Args:
            slot: 存档槽位
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        data = self.load_game(slot)
        if not data:
            return False
        
        try:
            save_dict = asdict(data)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(save_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"存档已导出到: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出存档失败: {e}")
            return False
    
    def import_save(self, import_path: str, slot: int) -> bool:
        """
        从指定路径导入存档
        
        Args:
            import_path: 导入路径
            slot: 目标存档槽位
            
        Returns:
            是否导入成功
        """
        if not os.path.exists(import_path):
            logger.warning(f"导入文件不存在: {import_path}")
            return False
        
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                save_dict = json.load(f)
            
            # 验证存档格式
            if 'version' not in save_dict:
                logger.warning("无效的存档文件格式")
                return False
            
            # 保存到指定槽位
            save_path = self._get_save_path(slot)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"存档已从 {import_path} 导入到槽位 {slot}")
            return True
            
        except Exception as e:
            logger.error(f"导入存档失败: {e}")
            return False


# 全局存档系统实例
_save_system: Optional[SaveSystem] = None


def get_save_system(save_dir: str = "saves") -> SaveSystem:
    """获取全局存档系统实例"""
    global _save_system
    if _save_system is None:
        _save_system = SaveSystem(save_dir)
    return _save_system


def init_save_system(save_dir: str = "saves") -> SaveSystem:
    """初始化存档系统"""
    global _save_system
    _save_system = SaveSystem(save_dir)
    return _save_system
