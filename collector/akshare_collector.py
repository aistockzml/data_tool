# -*- coding: utf-8 -*-
"""
Akshare数据采集器

继承DataCollector类，使用akshare Python库创建链接对象。

功能特性：
- 支持Akshare所有API接口
- 无需认证即可使用
- 支持批量数据采集
- 支持增量更新

使用示例：
    import akshare as ak
    from collector.akshare_collector import AkshareDataCollector
    
    collector = AkshareDataCollector(
        connector=ak,
        collect_name='stock_daily_ak',
        description='股票日线数据采集',
        db_conn=db_operator,
        logger=your_logger
    )
    
    # 采集A股日线数据 - 直接调用akshare的任意方法
    df = collector.collect(method='stock_zh_a_daily', symbol='000001', adjust='')
    
    # 采集ETF实时行情
    df = collector.collect(method='fund_etf_spot_em')
"""

import pandas as pd
from typing import Any, Dict, List, Optional
from .data_collector import DataCollector


class AkshareDataCollector(DataCollector):
    """
    Akshare数据采集器类
    
    继承DataCollector类，使用akshare Python库创建链接对象。
    
    Attributes:
        connector: Akshare对象
    """
    
    def __init__(self, connector: Any, collect_name: str,
                 description: str = '', db_conn: Any = None,
                 logger: Any = None):
        """
        初始化Akshare数据采集器
        
        Args:
            connector: Akshare对象
            collect_name: 数据采集器的唯一标识符
            description: 数据采集器的功能描述
            db_conn: 数据库连接对象
            logger: 日志记录器对象
        """
        super().__init__(connector, collect_name, description, db_conn, logger)
    
    def collect(self, method: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        采集数据
        
        通过方法名动态调用connector的任意方法。
        
        Args:
            method: Akshare方法名，如 'stock_zh_a_daily', 'fund_etf_spot_em'
            **kwargs: 方法参数
            
        Returns:
            Optional[DataFrame]: 采集到的数据
        """
        func = getattr(self.connector, method, None)
        if func is None:
            self.logger.error(f"Akshare '{method}' 方法不存在")
            return None
        
        self.logger.info(f"开始采集Akshare数据: {method}")
        
        try:
            data = func(**kwargs)
            
            if data is not None and not data.empty:
                self.logger.info(f"成功采集{len(data)}条{method}数据")
            elif data is not None:
                self.logger.info(f"成功采集{method}数据，数据为空")
            
            return data
            
        except Exception as e:
            self.logger.error(f"采集{method}数据失败: {e}")
            return None
    
    def get_available_methods(self) -> List[str]:
        """
        获取connector所有可用的方法名
        
        Returns:
            List[str]: 方法名列表
        """
        if self.connector is None:
            return []
        
        return [method for method in dir(self.connector) 
                if not method.startswith('_') and callable(getattr(self.connector, method))]
    
    def __repr__(self) -> str:
        return f"<AkshareDataCollector(name={self.collect_name})>"
