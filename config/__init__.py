# -*- coding: utf-8 -*-
"""
配置解析器

使用python pyyaml库解析配置文件，提供配置文件中参数的获取接口。

功能特性：
- 支持YAML格式配置文件
- 支持节(section)和配置项(option)获取
- 支持配置热加载
- 支持默认配置值

使用示例：
    config = ConfigParser('config.yaml')
    db_config = config.get_config('database', 'host')
    tasks = config.get_config('scheduler', 'jobs')
"""


import os
from typing import Any, Dict, List, Optional
import yaml


class ConfigParserError(Exception):
    """配置解析异常"""
    pass


class ConfigParser:
    """
    配置解析器类
    
    负责解析YAML配置文件，提供配置参数获取接口。
    
    Attributes:
        config_file (str): 配置文件路径
        config_data (Dict): 配置数据缓存
    """
    
    def __init__(self, config_file: str):
        """
        初始化配置解析器
        
        Args:
            config_file: 配置文件路径
            
        Raises:
            ConfigParserError: 配置文件不存在或解析失败
        """
        if not os.path.exists(config_file):
            raise ConfigParserError(f"配置文件不存在: {config_file}")
        
        self.config_file = config_file
        self.config_data: Dict = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigParserError(f"YAML解析失败: {e}")
        except IOError as e:
            raise ConfigParserError(f"读取配置文件失败: {e}")
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._load_config()
    
    def get_config(self, section: str, option: str = None, default: Any = None) -> Any:
        """
        获取配置参数
        
        根据section和option获取配置参数。
        支持嵌套配置，使用点号分隔层级。
        
        Args:
            section: 配置文件中的节名，支持嵌套如'database.connections'
            option: 配置项名，为None时返回整个section
            default: 默认值，当配置不存在时返回
            
        Returns:
            Any: 配置项对应的值
            
        Examples:
            # 获取数据库主机
            host = parser.get_config('database', 'host')
            
            # 获取整个数据库配置
            db_config = parser.get_config('database')
            
            # 获取嵌套配置
            pool_size = parser.get_config('database.pool', 'size')
        """
        keys = section.split('.')
        data = self.config_data
        
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return default
            data = data[key]
        
        if option is None:
            return data
        
        if isinstance(data, dict):
            return data.get(option, default)
        
        return default
    
    def get_section(self, section: str) -> Optional[Dict]:
        """
        获取整个配置节
        
        Args:
            section: 节名，支持嵌套
            
        Returns:
            Dict: 配置节数据，不存在返回None
        """
        return self.get_config(section)
    
    def get_list(self, section: str, option: str) -> List:
        """
        获取配置列表
        
        Args:
            section: 节名
            option: 配置项名
            
        Returns:
            List: 配置列表，默认返回空列表
        """
        result = self.get_config(section, option, [])
        if isinstance(result, list):
            return result
        return []
    
    def get_int(self, section: str, option: str, default: int = 0) -> int:
        """
        获取整数配置
        
        Args:
            section: 节名
            option: 配置项名
            default: 默认值
            
        Returns:
            int: 配置值
        """
        value = self.get_config(section, option)
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    
    def get_float(self, section: str, option: str, default: float = 0.0) -> float:
        """
        获取浮点数配置
        
        Args:
            section: 节名
            option: 配置项名
            default: 默认值
            
        Returns:
            float: 配置值
        """
        value = self.get_config(section, option)
        if value is None:
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    
    def get_bool(self, section: str, option: str, default: bool = False) -> bool:
        """
        获取布尔配置
        
        Args:
            section: 节名
            option: 配置项名
            default: 默认值
            
        Returns:
            bool: 配置值
        """
        value = self.get_config(section, option)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)
    
    def get_all_sections(self) -> List[str]:
        """
        获取所有顶层配置节
        
        Returns:
            List[str]: 配置节名称列表
        """
        return list(self.config_data.keys()) if isinstance(self.config_data, dict) else []
    
    def has_section(self, section: str) -> bool:
        """
        检查配置节是否存在
        
        Args:
            section: 节名
            
        Returns:
            bool: 是否存在
        """
        keys = section.split('.')
        data = self.config_data
        
        for key in keys:
            if not isinstance(data, dict) or key not in data:
                return False
            data = data[key]
        
        return isinstance(data, dict)
    
    def has_option(self, section: str, option: str) -> bool:
        """
        检查配置项是否存在
        
        Args:
            section: 节名
            option: 配置项名
            
        Returns:
            bool: 是否存在
        """
        section_data = self.get_section(section)
        if not isinstance(section_data, dict):
            return False
        return option in section_data
