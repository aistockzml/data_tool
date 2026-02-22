# -*- coding: utf-8 -*-
"""
股票基础信息采集任务

使用 Prefect 3.0 调度，每天 17:00 采集 Tushare 股票基础信息
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

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


def collect_and_save_basic_data(
    method: str,
    report_name: str,
    target_table: str,
    insert_mode_overwrite: str = None,
    page_size: int = 2000,
    **kwargs
) -> bool:
    """采集并保存基础数据
    
    Args:
        method: Tushare API 方法名
        report_name: 报表名称(用于日志)
        target_table: 目标数据库表名
        insert_mode_overwrite: 需要使用覆盖模式的exchange值，传入None表示始终增量
        page_size: 分页大小(默认2000)
        **kwargs: 传递给collect的其他参数
        
    Returns:
        bool: 是否成功
    """
    params = {'method': method, 'fields': '*', **kwargs}
    prefix_log_print(report_name, 'info', f"采集参数: {params}")

    all_data = []
    offset = 0
    
    while True:
        page_params = {**params, 'limit': page_size, 'offset': offset}
        data = ts_collector.collect(**page_params)
        
        if data is None or data.empty:
            if not all_data:
                prefix_log_print(report_name, 'info', "无数据需要保存")
                return True
            
            combined_data = pd.concat(all_data, ignore_index=True)
            prefix_log_print(report_name, 'info', f"采集完成,共 {len(combined_data)} 条数据")
            
            if insert_mode_overwrite is not None:
                insert_mode = 'overwrite'
            else:
                insert_mode = 'incremental'
            
            if ts_collector.save(combined_data, target_table=target_table, insert_mode=insert_mode):
                prefix_log_print(report_name, 'info', f"数据保存成功,共 {len(combined_data)} 条，插入模式: {insert_mode}")
                return True
            
            prefix_log_print(report_name, 'error', "数据保存失败")
            return False
        
        page_count = len(data)
        prefix_log_print(report_name, 'info', f"第{offset//page_size + 1}页,获取 {page_count} 条数据")
        
        all_data.append(data)
        offset += page_size


@task(name="collect_and_save_stock_basic", retries=3, retry_delay_seconds=10)
def collect_and_save_stock_basic():
    """采集股票列表并保存到数据库"""
    collect_and_save_basic_data(
        method='stock_basic',
        report_name='stock_basic',
        target_table='aistockzml_tushare_stock_basic',
        insert_mode_overwrite='stock_basic'
    )


@task(name="collect_and_save_stock_hsgt", retries=3, retry_delay_seconds=10)
def collect_and_save_stock_hsgt(today):
    """采集沪深港通股票列表并保存到数据库"""
    for es_type in ['HK_SZ', 'SZ_HK', 'HK_SH', 'SH_HK']:
        collect_and_save_basic_data(
            method='stock_hsgt',
            report_name=f'stock_hsgt_{es_type}',
            target_table='aistockzml_tushare_stock_hsgt',
            insert_mode_overwrite='HK_SZ' if es_type == 'HK_SZ' else None,
            trade_date=today,
            type=es_type
        )   


@task(name="collect_and_save_stock_company", retries=3, retry_delay_seconds=10)
def collect_and_save_stock_company():
    """采集上市公司基本信息并保存到数据库"""
    for exchange in ['SSE', 'SZSE', 'BSE']:
        collect_and_save_basic_data(
            method='stock_company',
            report_name=f'stock_company_{exchange}',
            target_table='aistockzml_tushare_stock_company',
            insert_mode_overwrite='SSE' if exchange == 'SSE' else None,
            exchange=exchange
        )


@flow(name="股票基础信息采集流程")
def stock_basic_flow():
    """股票基础信息采集主流程"""
    prefix_log_print('stock_basic', 'info', "=" * 50)
    prefix_log_print('stock_basic', 'info', "开始执行定时任务")
    prefix_log_print('stock_basic', 'info', f"执行时间: {datetime.now()}")

    today = '20260213'
    # 采集股票基础信息
    collect_and_save_stock_basic()
    # 采集沪深港通股票信息
    collect_and_save_stock_hsgt(today)
    # 采集上市公司基本信息  
    collect_and_save_stock_company()


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    stock_basic_flow()
    print("\n测试完成!")
