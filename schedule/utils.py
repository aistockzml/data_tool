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


def get_date_range_list(base_date: str, start_days_ago: int = 10, end_days_after: int = 0) -> List[str]:
    """获取日期范围列表
    
    Args:
        base_date: 基准日期,格式为 'YYYYMMDD'
        start_days_ago: 开始日期距基准日期天数(默认10天前,往过去推)
        end_days_after: 结束日期距基准日期天数(默认基准日期当天,往未来推)
        
    Returns:
        日期列表,格式为 'YYYYMMDD'
        
    Example:
        >>> get_date_range_list('20260213', start_days_ago=3, end_days_after=0)
        ['20260210', '20260211', '20260212', '20260213']
        >>> get_date_range_list('20260213', start_days_ago=2, end_days_after=2)
        ['20260211', '20260212', '20260213', '20260214', '20260215']
        >>> get_date_range_list('20260213', start_days_ago=7, end_days_after=3)
        ['20260206', '20260207', ..., '20260213', '20260214', '20260215', '20260216']
    """
    base = datetime.strptime(base_date, '%Y%m%d')
    start_date = base - timedelta(days=start_days_ago)
    end_date = base + timedelta(days=end_days_after)
    
    return pd.date_range(
        start=start_date.strftime('%Y%m%d'),
        end=end_date.strftime('%Y%m%d'),
        freq='D'
    ).strftime('%Y%m%d').tolist()


def get_week_friday(date_str: str) -> str:
    """获取输入日期当周的周五日期
    
    Args:
        date_str: 日期字符串,格式为 'YYYYMMDD'
        
    Returns:
        当周周五日期,格式为 'YYYYMMDD'
        
    Example:
        >>> get_week_friday('20260213')  # 周五
        '20260213'
        >>> get_week_friday('20260211')  # 周三
        '20260213'
        >>> get_week_friday('20260216')  # 周日
        '20260213'
    """
    date = datetime.strptime(date_str, '%Y%m%d')
    weekday = date.weekday()
    friday = date + timedelta(days=(4 - weekday))
    return friday.strftime('%Y%m%d')


def get_month_last_day(date_str: str) -> str:
    """获取输入日期当月的最后一天
    
    Args:
        date_str: 日期字符串,格式为 'YYYYMMDD'
        
    Returns:
        当月最后一天日期,格式为 'YYYYMMDD'
        
    Example:
        >>> get_month_last_day('20260213')
        '20260228'
        >>> get_month_last_day('20260115')
        '20260131'
        >>> get_month_last_day('20240215')  # 闰年
        '20240229'
    """
    date = datetime.strptime(date_str, '%Y%m%d')
    next_month = date.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    return last_day.strftime('%Y%m%d')


