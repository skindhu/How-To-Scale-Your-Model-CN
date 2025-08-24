"""
日志配置模块
统一管理项目的日志配置和输出

创建时间：2024-12-19
项目：系列技术文章翻译
"""

import logging
from typing import Optional

class LoggingConfig:
    """日志配置管理类"""

    def __init__(self,
                 log_level: str = 'INFO'):
        self.log_level = getattr(logging, log_level.upper())
        self._setup_logging()

    def _setup_logging(self):
        """设置日志配置"""
        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)

        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # 创建格式化器
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # 记录日志配置信息
        logging.info(f"日志系统初始化完成")
        logging.info(f"日志级别: {logging.getLevelName(self.log_level)}")
        logging.info("日志输出: 仅控制台输出")

    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志记录器"""
        return logging.getLogger(name)

    def create_module_logger(self, module_name: str) -> logging.Logger:
        """为特定模块创建日志记录器"""
        logger = logging.getLogger(f"translator.{module_name}")
        return logger

class ProgressLogger:
    """进度日志记录器"""

    def __init__(self, total_items: int, description: str = "Processing"):
        self.total_items = total_items
        self.current_item = 0
        self.description = description
        self.logger = logging.getLogger("progress")

    def update(self, increment: int = 1, message: str = ""):
        """更新进度"""
        self.current_item += increment
        progress = (self.current_item / self.total_items) * 100

        log_message = f"{self.description}: {self.current_item}/{self.total_items} ({progress:.1f}%)"
        if message:
            log_message += f" - {message}"

        self.logger.info(log_message)

    def complete(self, message: str = "完成"):
        """标记完成"""
        self.logger.info(f"{self.description}: {message} (总计: {self.total_items})")

def setup_logging(log_level: str = 'INFO') -> LoggingConfig:
    """便捷函数：设置日志系统"""
    return LoggingConfig(log_level)

def get_logger(name: str) -> logging.Logger:
    """便捷函数：获取日志记录器"""
    return logging.getLogger(name)
