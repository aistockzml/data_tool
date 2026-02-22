"""
股票其他数据采集任务
使用 Prefect 3.0 调度,采集 Tushare 股票其他数据 
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
from schedule import logger, ts_collector


def prefix_log_print(report_name: str, level: str, message: str):
    getattr(logger, level)(f"[{report_name}] {message}")


def collect_and_save_others_public(method: str, target_table: str, quotes_name: str,
                           conflict_columns: List[str] = None, page_size: int = 2000, **kwargs):
    """采集股票其他数据并保存到数据库（公共函数）   
    
    Args:
        method: Tushare API 方法名
        target_table: 目标数据库表名
        quotes_name: 行情名称(用于日志)
        conflict_columns: 冲突判断列名列表(默认None则使用TS_CODE, TRADE_DATE)
        page_size: 分页大小(默认2000)
        **kwargs: 动态参数
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
            if 'UPDATE_TIME' in combined_data.columns:
                combined_data = combined_data.sort_values('UPDATE_TIME', ascending=False)
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


@task(name="collect_and_save_repurchase", retries=100, retry_delay_seconds=5)
def collect_and_save_repurchase(trade_date: str):
    """采集股票回购并保存到数据库"""
    return collect_and_save_others_public(
        method='repurchase',
        target_table='aistockzml_tushare_repurchase',
        quotes_name='repurchase',
        ann_date=trade_date,
        conflict_columns=['TS_CODE', 'ANN_DATE', 'PROC']
    )


@task(name="collect_and_save_block_trade", retries=100, retry_delay_seconds=5)
def collect_and_save_block_trade(trade_date: str):
    """采集大宗交易并保存到数据库"""
    return collect_and_save_others_public(
        method='block_trade',
        target_table='aistockzml_tushare_block_trade',
        quotes_name='block_trade',
        trade_date=trade_date,
        conflict_columns=['ID']
    )


@task(name="collect_and_save_stk_holdernumber", retries=100, retry_delay_seconds=5)
def collect_and_save_stk_holdernumber(trade_date: str):
    """采集股东人数并保存到数据库"""
    return collect_and_save_others_public(
        method='stk_holdernumber',
        target_table='aistockzml_tushare_stk_holdernumber',
        quotes_name='stk_holdernumber',
        ann_date=trade_date,
        conflict_columns=['TS_CODE', 'ANN_DATE', 'END_DATE']
    )


@task(name="collect_and_save_stk_holdertrade", retries=100, retry_delay_seconds=5)
def collect_and_save_stk_holdertrade(trade_date: str):
    """采集股东增减持并保存到数据库"""
    return collect_and_save_others_public(
        method='stk_holdertrade',
        target_table='aistockzml_tushare_stk_holdertrade',
        quotes_name='stk_holdertrade',
        ann_date=trade_date,
        conflict_columns=['TS_CODE', 'ANN_DATE', 'HOLDER_NAME', 'IN_DE', 'BEGIN_DATE', 'CLOSE_DATE']
    )


@flow(name="股票其他数据采集流程")
def others_flow():
    """其他数据采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    today = '20260212'
    collect_and_save_repurchase(today)
    collect_and_save_block_trade(today)
    collect_and_save_stk_holdernumber(today)
    collect_and_save_stk_holdertrade(today)

    logger.info("=" * 50)
    logger.info("定时任务完成")
    logger.info("=" * 50)   


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    others_flow()
    print("\n测试完成!")