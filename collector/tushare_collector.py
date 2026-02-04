# -*- coding: utf-8 -*-
"""
Tushare数据采集器

继承DataCollector类，使用tushare Python库创建链接对象。

功能特性：
- 支持Tushare Pro所有API接口
- 自动Token管理
- 支持批量数据采集
- 支持增量更新

使用示例：
    import tushare as ts
    from collector.tushare_collector import TushareDataCollector
    
    ts.set_token('your_token')
    pro_api = ts.pro_api()
    
    collector = TushareDataCollector(
        connector=pro_api,
        collect_name='stock_daily',
        description='股票日线数据采集',
        db_conn=db_operator,
        token=token,
        logger=your_logger
    )
    
    # 采集股票列表 - 直接调用Tushare的任意接口
    df = collector.collect(method='stock_basic', fields='ts_code,symbol,name,area,industry')
    
    # 采集日线数据
    df = collector.collect(
        method='daily',
        ts_code='000001.SZ',
        start_date='20240101',
        end_date='20240131'
    )
"""

import pandas as pd
from typing import Any, Dict, List, Optional
from .data_collector import DataCollector


class TushareDataCollector(DataCollector):
    """
    Tushare数据采集器类
    
    继承DataCollector类，使用tushare Python库创建链接对象。
    
    Attributes:
        connector: Tushare Pro API对象
        token: Tushare API Token
    """
    
    def __init__(self, connector: Any, collect_name: str,
                 description: str = '', db_conn: Any = None,
                 token: str = None, logger: Any = None):
        """
        初始化Tushare数据采集器
        
        Args:
            connector: Tushare Pro API对象
            collect_name: 数据采集器的唯一标识符
            description: 数据采集器的功能描述
            db_conn: 数据库连接对象
            token: Tushare API Token
            logger: 日志记录器对象
        """
        super().__init__(connector, collect_name, description, db_conn, logger)
        self.token = token
    
    def collect(self, method: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        采集数据
        
        通过方法名动态调用connector的任意接口。
        
        Args:
            method: Tushare接口名，如 'stock_basic', 'daily', 'adj_factor'
            **kwargs: 接口参数
            
        Returns:
            Optional[DataFrame]: 采集到的数据
        """
        func = getattr(self.connector, method, None)
        if func is None:
            self.logger.error(f"Tushare '{method}' 接口不存在")
            return None
        
        self.logger.info(f"开始采集Tushare数据: {method}")
        
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
    
    def __repr__(self) -> str:
        return f"<TushareDataCollector(name={self.collect_name}, token={'*' * 8 if self.token else 'None'})>"
