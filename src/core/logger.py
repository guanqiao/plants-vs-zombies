"""
日志系统模块

提供统一的日志记录功能，支持控制台输出和文件输出。
确保程序异常退出时，异常信息能被记录到日志文件中。
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """
    日志管理器（单例模式）
    
    提供统一的日志记录接口，支持：
    - 控制台输出
    - 文件输出（按日期分割）
    - 异常捕获和记录
    """
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Logger._initialized:
            return
        
        self._logger = logging.getLogger("GameLogger")
        self._logger.setLevel(logging.DEBUG)
        self._handlers: list[logging.Handler] = []
        self._logs_dir: Optional[Path] = None
        
        Logger._initialized = True
    
    def setup(self, logs_dir: str = "logs", log_level: int = logging.DEBUG) -> None:
        """
        初始化日志系统
        
        Args:
            logs_dir: 日志文件存储目录
            log_level: 日志级别（默认为 DEBUG）
        """
        self._logs_dir = Path(logs_dir)
        self._logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 清除现有处理器
        for handler in self._handlers:
            self._logger.removeHandler(handler)
        self._handlers.clear()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        self._handlers.append(console_handler)
        
        # 文件处理器（按日期命名）
        log_file = self._logs_dir / f"game_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        self._handlers.append(file_handler)
        
        self._logger.setLevel(log_level)
        self.info(f"日志系统初始化完成，日志文件: {log_file}")
    
    def setup_exception_hook(self) -> None:
        """
        设置全局异常捕获钩子
        
        捕获所有未处理的异常并记录到日志中
        """
        def exception_hook(exc_type, exc_value, exc_traceback):
            """自定义异常处理函数"""
            if issubclass(exc_type, KeyboardInterrupt):
                # 正常处理键盘中断
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # 记录异常信息
            self._logger.critical("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
            
            # 调用原始异常处理
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = exception_hook
        self.debug("全局异常捕获已设置")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称（通常使用模块名）
            
        Returns:
            配置好的日志记录器
        """
        return logging.getLogger(name)
    
    def debug(self, message: str) -> None:
        """记录 DEBUG 级别日志"""
        self._logger.debug(message)
    
    def info(self, message: str) -> None:
        """记录 INFO 级别日志"""
        self._logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录 WARNING 级别日志"""
        self._logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录 ERROR 级别日志"""
        self._logger.error(message)
    
    def critical(self, message: str) -> None:
        """记录 CRITICAL 级别日志"""
        self._logger.critical(message)
    
    def exception(self, message: str) -> None:
        """记录异常信息（包含堆栈跟踪）"""
        self._logger.exception(message)


# 全局日志实例
def get_logger() -> Logger:
    """获取日志管理器实例"""
    return Logger()


def get_module_logger(name: str) -> logging.Logger:
    """
    获取模块日志记录器
    
    在模块中使用：
        from src.core.logger import get_module_logger
        logger = get_module_logger(__name__)
        logger.info("消息")
    
    Args:
        name: 模块名称（通常传入 __name__）
        
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)
