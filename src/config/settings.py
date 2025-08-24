"""
配置文件模块
用于管理项目的所有配置参数

创建时间：2024-12-19
项目：系列技术文章翻译
"""

import os
from pathlib import Path
from typing import Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

class Config:
    """配置类，管理所有配置参数"""

    def __init__(self):
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        # 路径配置
        self.OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
        self.ORIGIN_DIR = os.getenv('ORIGIN_DIR', 'output/origin')
        self.TRANS_DIR = os.getenv('TRANS_DIR', 'output/trans')

        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

        # 爬虫配置
        self.USER_AGENT = os.getenv('USER_AGENT', 'Mozilla/5.0 (compatible; TranslationBot/1.0)')
        self.REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

        # 翻译配置
        self.TRANSLATOR_NAME = os.getenv('TRANSLATOR_NAME', '北极的树')
        self.BATCH_SIZE = int(os.getenv('BATCH_SIZE', '5'))

        # 验证必需配置
        self._validate_config()

    def _validate_config(self):
        """验证配置的有效性"""
        # 确保目录存在
        for directory in [self.OUTPUT_DIR, self.ORIGIN_DIR, self.TRANS_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_absolute_path(self, relative_path: str) -> Path:
        """获取相对于项目根目录的绝对路径"""
        return PROJECT_ROOT / relative_path

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典格式"""
        return {
            'paths': {
                'output_dir': self.OUTPUT_DIR,
                'origin_dir': self.ORIGIN_DIR,
                'trans_dir': self.TRANS_DIR,
            },
            'logging': {
                'log_level': self.LOG_LEVEL,
            },
            'crawler': {
                'user_agent': self.USER_AGENT,
                'request_delay': self.REQUEST_DELAY,
                'max_retries': self.MAX_RETRIES,
            },
            'translation': {
                'translator_name': self.TRANSLATOR_NAME,
                'batch_size': self.BATCH_SIZE,
            }
        }

# 全局配置实例
config = Config()

# 导出常用配置
OUTPUT_DIR = config.OUTPUT_DIR
ORIGIN_DIR = config.ORIGIN_DIR
TRANS_DIR = config.TRANS_DIR
LOG_LEVEL = config.LOG_LEVEL
USER_AGENT = config.USER_AGENT
REQUEST_DELAY = config.REQUEST_DELAY
MAX_RETRIES = config.MAX_RETRIES
TRANSLATOR_NAME = config.TRANSLATOR_NAME
BATCH_SIZE = config.BATCH_SIZE
