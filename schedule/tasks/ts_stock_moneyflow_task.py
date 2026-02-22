"""
股票资金流数据采集任务
使用 Prefect 3.0 调度,采集 Tushare 股票资金流数据
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from prefect import flow, task
from prefect.task_runners import ThreadPoolTaskRunner
from schedule import logger, ts_collector, get_date_range_list


def prefix_log_print(report_name: str, level: str, message: str):
    getattr(logger, level)(f"[{report_name}] {message}")


def collect_and_save_moneyflow_public(method: str, target_table: str, quotes_name: str,
                           conflict_columns: List[str] = None, page_size: int = 2000, **kwargs):
    """采集股票资金流数据并保存到数据库（公共函数）
    
    Args:
        method: Tushare API 方法名
        target_table: 目标数据库表名
        quotes_name: 行情名称(用于日志)
        conflict_columns: 冲突判断列名列表(默认None则使用TS_CODE, TRADE_DATE)
        page_size: 分页大小(默认2000)
        **kwargs: 动态参数(包括trade_date等)
    """
    if conflict_columns is None:
        conflict_columns = ['TS_CODE', 'TRADE_DATE']
    
    params = {
        'method': method,
        'fields': '*'
    }
    params.update(kwargs)
    prefix_log_print(quotes_name, 'info', f"采集参数: {params}")

    all_data = []
    offset = 0
    
    while True:
        page_params = {**params, 'limit': page_size, 'offset': offset}
        
        data = ts_collector.collect(**page_params)
        
        if data is None or data.empty:
            if not all_data:
                prefix_log_print(quotes_name, 'info', "无数据需要保存")
                return True
            
            combined_data = pd.concat(all_data, ignore_index=True)
            before_dedup = len(combined_data)
            combined_data = combined_data.drop_duplicates(subset=conflict_columns, keep='first')
            after_dedup = len(combined_data)
            prefix_log_print(quotes_name, 'info', f"采集完成,共 {before_dedup} 条数据, 去重后 {after_dedup} 条")
            
            if ts_collector.save(combined_data, target_table=target_table, insert_mode='incremental', conflict_columns=conflict_columns):
                prefix_log_print(quotes_name, 'info', f"数据保存成功(incremental),共 {len(combined_data)} 条")
                return True
            
            prefix_log_print(quotes_name, 'error', "数据保存失败")
            return False
        
        page_count = len(data)
        prefix_log_print(quotes_name, 'info', f"第{offset//page_size + 1}页,获取 {page_count} 条数据")
        
        all_data.append(data)
        offset += page_size


@task(name="collect_and_save_moneyflow", retries=100, retry_delay_seconds=5)
def collect_and_save_moneyflow(trade_date: str):
    """采集股票资金流数据并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow',
        target_table='aistockzml_tushare_moneyflow',
        quotes_name='moneyflow',
        trade_date=trade_date
    )


@task(name="collect_and_save_moneyflow_dc", retries=100, retry_delay_seconds=5)
def collect_and_save_moneyflow_dc(trade_date: str):
    """采集股票资金流数据_东方财富并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_dc',
        target_table='aistockzml_tushare_moneyflow_dc',
        quotes_name='moneyflow_dc',
        trade_date=trade_date
    )


@task(name="collect_and_save_moneyflow_ind_dc", retries=100, retry_delay_seconds=5)
def collect_and_save_moneyflow_ind_dc(trade_date: str):
    """采集东财概念及行业板块资金流向（DC）并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_ind_dc',
        target_table='aistockzml_tushare_moneyflow_ind_dc',
        quotes_name='moneyflow_ind_dc',
        trade_date=trade_date,
        conflict_columns=['INS_CODE', 'TRADE_DATE', 'CONTENT_TYPE']
    )
    

@task(name="collect_and_save_moneyflow_mkt_dc", retries=100, retry_delay_seconds=5)
def collect_and_save_moneyflow_mkt_dc(trade_date: str):
    """采集大盘资金流向（DC）并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_mkt_dc',
        target_table='aistockzml_tushare_moneyflow_mkt_dc',
        quotes_name='moneyflow_mkt_dc',
        trade_date=trade_date,
        conflict_columns=['TRADE_DATE']
    )


@task(name="collect_and_save_moneyflow_hsgt", retries=100, retry_delay_seconds=5)
def collect_and_save_moneyflow_hsgt(trade_date: str):
    """采集沪深港通资金流向并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_hsgt',
        target_table='aistockzml_tushare_moneyflow_hsgt',
        quotes_name='moneyflow_hsgt',
        trade_date=trade_date,
        conflict_columns=['TRADE_DATE']
    )


@flow(name="股票资金流数据采集流程")
def moneyflow_flow():
    """资金流数据采集主流程"""
    prefix_log_print('moneyflow', 'info', "=" * 50)
    prefix_log_print('moneyflow', 'info', "开始执行定时任务")
    prefix_log_print('moneyflow', 'info', f"执行时间: {datetime.now()}")
    
    base_date = '20260213'
    date_range_list = get_date_range_list(base_date, start_days_ago=30, end_days_after=0)
    prefix_log_print('moneyflow', 'info', f"日期范围: {date_range_list}")

    for trade_date in date_range_list:
        collect_and_save_moneyflow(trade_date)
        collect_and_save_moneyflow_dc(trade_date)
        collect_and_save_moneyflow_ind_dc(trade_date)    
        collect_and_save_moneyflow_mkt_dc(trade_date)
        collect_and_save_moneyflow_hsgt(trade_date)


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    moneyflow_flow()
    print("\n测试完成!")
