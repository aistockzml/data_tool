# -*- coding: utf-8 -*-
"""
data_tools - 金融数据采集框架

可集成tushare、akshare等主流数据接口，实现统一的数据采集与管理。

核心模块：
- config: 配置模块，提供配置解析功能
- logger: 日志模块，提供日志记录功能
- storage: 存储模块，提供MySQL数据库操作
- collector: 采集模块，提供数据采集功能

使用示例：
    from data_tools.config import ConfigParser
    from data_tools.logger import LoggerManager
    from data_tools.storage import MySqlOperator
    from data_tools.collector import TushareDataCollector
    
    # 加载配置
    config = ConfigParser('config.yaml')
    
    # 获取日志器
    logger = LoggerManager().get_logger("app")
    
    # 创建数据库连接
    db = MySqlOperator(
        host=config.get_config('database', 'host'),
        user=config.get_config('database', 'user'),
        password=config.get_config('database', 'password'),
        database=config.get_config('database', 'database')
    )
"""


__version__ = '1.0.0'
__author__ = 'data_tools'

from .config import ConfigParser
from .logger import LoggerManager, DataLogger

try:
    from .storage import MySqlOperator
    _STORAGE_AVAILABLE = True
except ImportError:
    MySqlOperator = None
    _STORAGE_AVAILABLE = False

from .collector import DataConnector, TushareConnector, AkshareConnector
from .collector import DataCollector, TushareDataCollector, AkshareDataCollector

__all__ = [
    'ConfigParser',
    'LoggerManager',
    'DataLogger',
    'MySqlOperator',
    'DataConnector',
    'TushareConnector',
    'AkshareConnector',
    'DataCollector',
    'TushareDataCollector',
    'AkshareDataCollector',
]
