"""
配置模块初始化文件

导出主要的配置类和函数，方便其他模块导入使用

创建时间：2024-12-19
项目：系列技术文章翻译
"""

from .settings import (
    Config,
    config,
    OUTPUT_DIR,
    ORIGIN_DIR,
    TRANS_DIR,
    LOG_LEVEL,
    USER_AGENT,
    REQUEST_DELAY,
    MAX_RETRIES,
    TRANSLATOR_NAME,
    BATCH_SIZE
)

from .logging_config import (
    LoggingConfig,
    ProgressLogger,
    setup_logging,
    get_logger
)

__all__ = [
    # Settings
    'Config',
    'config',
    'OUTPUT_DIR',
    'ORIGIN_DIR',
    'TRANS_DIR',
    'LOG_LEVEL',
    'USER_AGENT',
    'REQUEST_DELAY',
    'MAX_RETRIES',
    'TRANSLATOR_NAME',
    'BATCH_SIZE',

    # Logging Config
    'LoggingConfig',
    'ProgressLogger',
    'setup_logging',
    'get_logger'
]
