# -*- coding: utf-8 -*-
"""
日志管理器

负责日志的统一管理，提供日志配置和日志器获取接口。

功能特性：
- 支持日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 支持输出方式：控制台、文件
- 支持按天切割日志，保留最近7天
- 支持多进程安全日志写入
- 日志格式：[时间] [日志级别] [模块名] 日志消息

使用示例（单进程）：
    from logger import LoggerManager
    logger = LoggerManager().get_logger("data_collector")
    logger.info("采集开始")

使用示例（多进程）：
    from logger import LoggerManager
    logger_manager = LoggerManager()
    queue = logger_manager.setup_multiprocess_logger()
    logger = logger_manager.get_multiprocess_logger("data_collector", queue)
"""

import os
import sys
import logging
import logging.handlers
import multiprocessing
from multiprocessing import Queue
from typing import Dict


class LoggerManager:
    """
    日志管理器类

    Attributes:
        _loggers: 日志器缓存字典
        _default_config: 默认配置
        _queue: 多进程日志队列
        _listener: 多进程队列监听器
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
        'file_level': 'DEBUG'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config = self._default_config.copy()
            self._queue = None
            self._listener = None

    def setup_multiprocess_logger(self, file_path: str = None,
                                   level: str = 'INFO',
                                   max_bytes: int = 10485760,
                                   backup_days: int = 7,
                                   encoding: str = 'utf-8') -> Queue:
        """
        设置多进程日志模式

        Args:
            file_path: 日志文件路径
            level: 日志级别
            max_bytes: 单个日志文件最大字节数
            backup_days: 保留天数
            encoding: 文件编码

        Returns:
            Queue: 日志队列，用于子进程
        """
        if file_path is None:
            file_path = self._config['file_path']

        self._queue = multiprocessing.Queue()

        log_dir = os.path.dirname(file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        if not file_path.endswith('.log'):
            base_path = file_path
        else:
            base_path = file_path.replace('.log', '')
        log_filename = f'{base_path}_{current_date}.log'

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_filename,
            maxBytes=max_bytes,
            backupCount=backup_days,
            encoding=encoding
        )
        file_handler.setLevel(self._get_log_level(level))

        formatter = logging.Formatter(
            fmt=self._config['format'],
            datefmt=self._config['datefmt']
        )
        file_handler.setFormatter(formatter)

        self._listener = logging.handlers.QueueListener(self._queue, [file_handler])
        self._listener.start()

        return self._queue

    def stop_multiprocess_logger(self) -> None:
        """停止多进程日志监听器"""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

        if self._queue is not None:
            try:
                while not self._queue.empty():
                    self._queue.get_nowait()
            except Exception:
                pass
            self._queue = None

    def get_multiprocess_logger(self, name: str, queue: Queue = None) -> logging.Logger:
        """
        获取多进程日志器实例

        Args:
            name: 日志器名称
            queue: 日志队列

        Returns:
            logging.Logger: 配置好QueueHandler的日志器
        """
        use_queue = queue or self._queue

        if use_queue is None:
            return self.get_logger(name)

        if name in self._loggers:
            logger = self._loggers[name]
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.handlers.QueueHandler):
                    return logger
                logger.removeHandler(handler)
        else:
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            self._loggers[name] = logger

        queue_handler = logging.handlers.QueueHandler(use_queue)
        logger.addHandler(queue_handler)
        logger.propagate = False

        return logger

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
            log_dir = os.path.dirname(self._config['file_path'])
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            from datetime import datetime
            current_date = datetime.now().strftime('%Y%m%d')
            base_path = self._config['file_path']
            if not base_path.endswith('.log'):
                base_path = base_path + '.log'
            log_filename = base_path.replace('.log', f'_{current_date}.log')

            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_filename,
                maxBytes=self._config.get('max_bytes', 10485760),
                backupCount=self._config.get('backup_days', 7),
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
        self.stop_multiprocess_logger()
        self._config = self._default_config.copy()

        for name, logger in self._loggers.items():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(logger)

            new_logger = self._create_logger(name)
            self._loggers[name] = new_logger
