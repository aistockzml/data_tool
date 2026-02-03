# -*- coding: utf-8 -*-
"""
日志管理器

负责日志的统一管理，提供日志配置和日志器获取接口。

功能特性：
- 支持日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 支持输出方式：控制台、文件
- 支持多目标同时输出：控制台+文件等
- 日志格式：[时间] [日志级别] [模块名] [任务ID] 日志消息
- 日志消息为中文，方便阅读和理解

使用示例：
    logger_manager = LoggerManager()
    logger = logger_manager.get_logger("data_collector")
    logger.info("采集开始")
"""


import os
import logging
import logging.handlers
from typing import Dict, Optional

from .data_logger import DataLogger


class TaskIdFilter(logging.Filter):
    """日志过滤器，确保task_id字段总是存在"""
    
    def filter(self, record):
        if not hasattr(record, 'task_id'):
            record.task_id = 'N/A'
        return True


class LoggerManager:
    """
    日志管理器类
    
    负责日志的统一管理，提供日志配置和日志器获取接口。
    
    Attributes:
        _loggers: 日志器缓存字典
        _default_config: 默认配置
    """
    
    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _default_config = {
        'level': 'INFO',
        'output': 'console',
        'file_path': 'logs/data_collector.log',
        'format': '[%(asctime)s] [%(levelname)s] [%(name)s] [%(task_id)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'encoding': 'utf-8',
        'max_bytes': 10485760,
        'backup_count': 5,
        'console_level': 'INFO',
        'file_level': 'DEBUG'
    }
    
    def __new__(cls):
        """
        单例模式，确保只有一个LoggerManager实例
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化日志管理器"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = self._default_config.copy()
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        根据名称获取对应的日志器实例
        
        Args:
            name: 日志器名称，建议使用模块名
            
        Returns:
            logging.Logger: 日志器实例
        """
        if name in self._loggers:
            return self._loggers[name]
        
        logger = self._create_logger(name)
        self._loggers[name] = logger
        return logger
    
    def _create_logger(self, name: str) -> logging.Logger:
        """
        创建日志器
        
        Args:
            name: 日志器名称
            
        Returns:
            logging.Logger: 配置好的日志器
        """
        logger = logging.getLogger(name)
        logger.setLevel(self._get_log_level(self._config['level']))
        
        if logger.handlers:
            return logger
        
        logger.addFilter(TaskIdFilter())
        
        formatter = logging.Formatter(
            fmt=self._config['format'],
            datefmt=self._config['datefmt']
        )
        
        output = self._config.get('output', 'console').lower()
        
        if output in ('console', 'both'):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._get_log_level(self._config.get('console_level', 'INFO')))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        if output in ('file', 'both'):
            log_dir = os.path.dirname(self._config['file_path'])
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self._config['file_path'],
                maxBytes=self._config.get('max_bytes', 10485760),
                backupCount=self._config.get('backup_count', 5),
                encoding=self._config.get('encoding', 'utf-8')
            )
            file_handler.setLevel(self._get_log_level(self._config.get('file_level', 'DEBUG')))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        logger.propagate = False
        return logger
    
    def _get_log_level(self, level: str) -> int:
        """
        获取日志级别
        
        Args:
            level: 级别名称
            
        Returns:
            int: logging级别
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(level.upper(), logging.INFO)
    
    def configure(self, **kwargs) -> None:
        """
        动态修改日志配置
        
        Args:
            **kwargs: 日志配置参数，包括log_level、log_output等
        """
        self._config.update(kwargs)
        
        for name, logger in self._loggers.items():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            
            new_logger = self._create_logger(name)
            self._loggers[name] = new_logger
    
    def reset(self) -> None:
        """重置日志配置为默认值"""
        self._config = self._default_config.copy()
        
        for name, logger in self._loggers.items():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(logger)
            
            new_logger = self._create_logger(name)
            self._loggers[name] = new_logger
