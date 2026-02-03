# -*- coding: utf-8 -*-
"""
日志记录器

提供日志记录功能，支持多模块日志追踪和日志分级。

功能特性：
- 支持日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
- 支持任务ID追踪
- 支持额外参数记录
- 日志消息为中文

使用示例：
    logger = LoggerManager().get_logger("data_collector")
    logger.info("采集开始", task_id="task_001")
"""


import logging
from typing import Any, Dict, Optional


class DataLogger:
    """
    日志记录器类
    
    提供日志记录功能，支持多模块日志追踪和日志分级。
    
    Attributes:
        _logger: 底层logging.Logger实例
        _default_task_id: 默认任务ID
    """
    
    def __init__(self, name: str = "data_logger", task_id: str = None):
        """
        初始化日志记录器
        
        Args:
            name: 日志器名称
            task_id: 默认任务ID
        """
        from . import LoggerManager
        
        self._logger = LoggerManager().get_logger(name)
        self._default_task_id = task_id
    
    def _log(self, level: int, message: str, 
             exc_info: bool = False, task_id: str = None, 
             extra: Dict = None, **kwargs) -> None:
        """
        通用日志记录方法
        
        Args:
            level: 日志级别
            message: 日志消息
            exc_info: 是否包含异常信息
            task_id: 任务ID
            extra: 额外字段
            **kwargs: 其他参数
        """
        log_extra = {
            'task_id': task_id or self._default_task_id or 'N/A'
        }
        
        if extra:
            log_extra.update(extra)
        
        self._logger.log(level, message, exc_info=exc_info, extra=log_extra, **kwargs)
    
    def debug(self, message: str, task_id: str = None, **kwargs) -> None:
        """
        记录调试日志
        
        Args:
            message: 日志消息
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.DEBUG, message, task_id=task_id, **kwargs)
    
    def info(self, message: str, task_id: str = None, **kwargs) -> None:
        """
        记录信息日志
        
        Args:
            message: 日志消息
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.INFO, message, task_id=task_id, **kwargs)
    
    def warning(self, message: str, task_id: str = None, **kwargs) -> None:
        """
        记录警告日志
        
        Args:
            message: 日志消息
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.WARNING, message, task_id=task_id, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, 
              task_id: str = None, **kwargs) -> None:
        """
        记录错误日志
        
        Args:
            message: 日志消息
            exc_info: 是否包含异常堆栈
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.ERROR, message, exc_info=exc_info, task_id=task_id, **kwargs)
    
    def critical(self, message: str, exc_info: bool = False, 
                 task_id: str = None, **kwargs) -> None:
        """
        记录严重错误日志
        
        Args:
            message: 日志消息
            exc_info: 是否包含异常堆栈
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.CRITICAL, message, exc_info=exc_info, task_id=task_id, **kwargs)
    
    def exception(self, message: str, task_id: str = None, **kwargs) -> None:
        """
        记录异常日志（自动包含异常堆栈）
        
        Args:
            message: 日志消息
            task_id: 任务ID
            **kwargs: 其他参数
        """
        self._log(logging.ERROR, message, exc_info=True, task_id=task_id, **kwargs)
    
    def log_collect_start(self, collect_name: str, task_id: str = None) -> None:
        """
        记录采集任务开始
        
        Args:
            collect_name: 采集任务名称
            task_id: 任务ID
        """
        message = f"采集任务开始: {collect_name}"
        self.info(message, task_id=task_id)
    
    def log_collect_end(self, collect_name: str, success: bool, 
                        record_count: int, task_id: str = None) -> None:
        """
        记录采集任务结束
        
        Args:
            collect_name: 采集任务名称
            success: 是否成功
            record_count: 记录数
            task_id: 任务ID
        """
        status = "成功" if success else "失败"
        message = f"采集任务结束: {collect_name}, 状态: {status}, 记录数: {record_count}"
        
        if success:
            self.info(message, task_id=task_id)
        else:
            self.warning(message, task_id=task_id)
    
    def log_collect_error(self, collect_name: str, error: str, 
                          task_id: str = None) -> None:
        """
        记录采集任务错误
        
        Args:
            collect_name: 采集任务名称
            error: 错误信息
            task_id: 任务ID
        """
        message = f"采集任务错误: {collect_name}, 错误: {error}"
        self.error(message, task_id=task_id)
    
    def log_save_start(self, table_name: str, record_count: int, 
                       task_id: str = None) -> None:
        """
        记录保存任务开始
        
        Args:
            table_name: 表名
            record_count: 记录数
            task_id: 任务ID
        """
        message = f"保存任务开始: {table_name}, 记录数: {record_count}"
        self.info(message, task_id=task_id)
    
    def log_save_end(self, table_name: str, success: bool, 
                     affected_rows: int, task_id: str = None) -> None:
        """
        记录保存任务结束
        
        Args:
            table_name: 表名
            success: 是否成功
            affected_rows: 影响行数
            task_id: 任务ID
        """
        status = "成功" if success else "失败"
        message = f"保存任务结束: {table_name}, 状态: {status}, 影响行数: {affected_rows}"
        
        if success:
            self.info(message, task_id=task_id)
        else:
            self.error(message, task_id=task_id)
    
    def log_save_error(self, table_name: str, error: str, 
                       task_id: str = None) -> None:
        """
        记录保存任务错误
        
        Args:
            table_name: 表名
            error: 错误信息
            task_id: 任务ID
        """
        message = f"保存任务错误: {table_name}, 错误: {error}"
        self.error(message, task_id=task_id)
    
    def set_task_id(self, task_id: str) -> None:
        """
        设置默认任务ID
        
        Args:
            task_id: 任务ID
        """
        self._default_task_id = task_id
    
    def get_logger(self) -> logging.Logger:
        """
        获取底层日志器
        
        Returns:
            logging.Logger: 底层日志器实例
        """
        return self._logger
