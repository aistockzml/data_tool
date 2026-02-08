# -*- coding: utf-8 -*-
"""
日志管理器

负责日志的统一管理，提供日志配置和日志器获取接口。

功能特性：
- 支持日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 支持输出方式：控制台、文件、Prefect UI
- 支持按天切割日志，保留最近7天
- 使用 concurrent-log-handler 实现多进程安全日志写入
- 日志格式：[时间] [日志级别] [模块名] 日志消息

使用示例：
    from logger import LoggerManager
    logger = LoggerManager().get_logger("data_collector")
    logger.info("采集开始")
"""

import os
import sys
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from typing import Dict, Optional


class LoggerManager:
    """
    日志管理器类

    Attributes:
        _loggers: 日志器缓存字典
        _default_config: 默认配置
    """

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _default_config = {
        'level': 'INFO',
        'output': 'both',
        'file_path': 'logs/data_collector.log',
        'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
        'encoding': 'utf-8',
        'max_bytes': 10485760,
        'backup_days': 7,
        'console_level': 'INFO',
        'file_level': 'DEBUG',
        'prefect_enabled': True
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = self._default_config.copy()

    def get_logger(self, name: str) -> logging.Logger:
        """
        根据名称获取对应的日志器实例

        Args:
            name: 日志器名称

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

        formatter = logging.Formatter(
            fmt=self._config['format'],
            datefmt=self._config['datefmt']
        )

        output = self._config.get('output', 'console').lower()

        if output in ('console', 'both'):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self._get_log_level(self._config.get('console_level', 'INFO')))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if output in ('file', 'both'):
            logger.addHandler(self._create_file_handler(formatter))

        if self._config.get('prefect_enabled', True):
            self._add_prefect_handler(logger, formatter)

        logger.propagate = False
        return logger

    def _create_file_handler(self, formatter: logging.Formatter) -> ConcurrentRotatingFileHandler:
        """创建文件日志处理器"""
        log_dir = os.path.dirname(self._config['file_path'])
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        base_path = self._config['file_path']
        if not base_path.endswith('.log'):
            base_path = base_path + '.log'
        log_filename = base_path.replace('.log', f'_{current_date}.log')

        file_handler = ConcurrentRotatingFileHandler(
            filename=log_filename,
            maxBytes=self._config.get('max_bytes', 10485760),
            backupCount=self._config.get('backup_days', 7),
            encoding=self._config.get('encoding', 'utf-8')
        )
        file_handler.setLevel(self._get_log_level(self._config.get('file_level', 'DEBUG')))
        file_handler.setFormatter(formatter)
        return file_handler

    def _add_prefect_handler(self, logger: logging.Logger, formatter: logging.Formatter) -> None:
        """添加 Prefect 日志处理器，将日志发送到 Prefect UI"""
        try:
            from prefect.logging.handlers import PrefectLogHandler

            prefect_handler = PrefectLogHandler()
            prefect_handler.setFormatter(formatter)
            logger.addHandler(prefect_handler)
        except ImportError:
            pass

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
            **kwargs: 日志配置参数
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
