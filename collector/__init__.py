# -*- coding: utf-8 -*-
"""
数据链接器

负责数据源连接，提供统一的连接获取接口，子类可根据需要实现具体的连接逻辑。

功能特性：
- 支持多数据源连接管理
- 支持tushare、akshare等主流数据接口
- 连接信息从配置文件读取，不硬编码
- 支持数据源类型扩展

使用示例：
    # Tushare示例
    connector = DataConnector('tushare', token='your_token')
    pro = connector.get_connection()
    
    # Akshare示例
    connector = DataConnector('akshare')
    ak = connector.get_connection()
"""


from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class DataConnector:
    """
    数据链接器基类
    
    负责数据源连接，提供统一的连接获取接口，子类可根据需要实现具体的连接逻辑。
    
    Attributes:
        source_name: 数据源名称
        token: API密钥或Token
        _connection: 连接对象缓存
    """
    
    def __init__(self, source_name: str, token: str = None):
        """
        初始化数据链接器
        
        Args:
            source_name: 数据源名称，如'tushare'、'akshare'
            token: 可选参数，数据源的API密钥或Token
        """
        self.source_name = source_name
        self.token = token
        self._connection = None
    
    @abstractmethod
    def connect(self) -> Any:
        """
        创建数据源连接
        
        Returns:
            Any: 连接对象
        """
        pass
    
    def get_connection(self) -> Any:
        """
        获取数据源连接
        
        Returns:
            Any: 连接对象
        """
        if self._connection is None:
            self._connection = self.connect()
        return self._connection
    
    def close(self) -> None:
        """
        关闭数据源连接
        """
        self._connection = None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(source={self.source_name})>"
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False


class TushareConnector(DataConnector):
    """
    Tushare数据链接器
    
    使用tushare Python库创建连接。
    
    Attributes:
        token: Tushare API Token
    """
    
    def __init__(self, token: str):
        """
        初始化Tushare连接器
        
        Args:
            token: Tushare API Token，必填参数
        """
        super().__init__('tushare', token)
    
    def connect(self) -> Any:
        """
        创建Tushare连接
        
        Returns:
            Tushare Pro API对象
        """
        try:
            import tushare as ts
            pro_api = ts.pro_api(self.token)
            pro_api._DataApi__token = self.token
            pro_api._DataApi__http_url = 'http://lianghua.9vvn.com'
            return pro_api
        except ImportError:
            raise ImportError("请安装tushare: pip install tushare")
        except Exception as e:
            raise ConnectionError(f"Tushare连接失败: {e}")
    
    def __repr__(self) -> str:
        return f"<TushareConnector(token={'*' * len(self.token) if self.token else 'None'})>"


class AkshareConnector(DataConnector):
    """
    Akshare数据链接器
    
    使用akshare Python库创建连接。
    
    Attributes:
        无需认证信息
    """
    
    def __init__(self):
        """初始化Akshare连接器"""
        super().__init__('akshare', None)
    
    def connect(self) -> Any:
        """
        创建Akshare连接
        
        Returns:
            Akshare对象
        """
        try:
            import akshare as ak
            return ak
        except ImportError:
            raise ImportError("请安装akshare: pip install akshare")
        except Exception as e:
            raise ConnectionError(f"Akshare初始化失败: {e}")
    
    def __repr__(self) -> str:
        return "<AkshareConnector>"


from .data_collector import DataCollector
from .tushare_collector import TushareDataCollector
from .akshare_collector import AkshareDataCollector
