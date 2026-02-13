# -*- coding: utf-8 -*-
"""
公共工具函数
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List


def get_quarter_end_dates(base_date: str, periods: int = 4) -> List[str]:
    """获取季度末日期列表
    
    Args:
        base_date: 基准日期,格式为 'YYYYMMDD'
        periods: 获取的季度数量(默认4个)
        
    Returns:
        季度末日期列表,格式为 'YYYYMMDD'
        
    Example:
        >>> get_quarter_end_dates('20250213', 4)
        ['20250930', '20250630', '20250331', '20241231']
        >>> get_quarter_end_dates('20250115', 2)
        ['20241231', '20240930']
    """
    current_quarter_end = pd.Timestamp(base_date) + pd.offsets.QuarterEnd(0)
    return pd.date_range(
        end=current_quarter_end,
        periods=periods,
        freq='QE'
    ).strftime('%Y%m%d').tolist()


def get_date_range_list(base_date: str, start_days_ago: int = 10, end_days_ago: int = 0) -> List[str]:
    """获取日期范围列表
    
    Args:
        base_date: 基准日期,格式为 'YYYYMMDD'
        start_days_ago: 开始日期距基准日期天数(默认10天前)
        end_days_ago: 结束日期距基准日期天数(默认基准日期当天)
        
    Returns:
        日期列表,格式为 'YYYYMMDD'
        
    Example:
        >>> get_date_range_list('20260213', start_days_ago=3, end_days_ago=0)
        ['20260210', '20260211', '20260212', '20260213']
        >>> get_date_range_list('20260201', start_days_ago=2, end_days_ago=0)
        ['20260130', '20260131', '20260201']
    """
    base = datetime.strptime(base_date, '%Y%m%d')
    start_date = base - timedelta(days=start_days_ago)
    end_date = base - timedelta(days=end_days_ago)
    return pd.date_range(
        start=start_date.strftime('%Y%m%d'),
        end=end_date.strftime('%Y%m%d'),
        freq='D'
    ).strftime('%Y%m%d').tolist()
