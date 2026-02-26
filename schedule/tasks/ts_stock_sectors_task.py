"""
股票板块数据采集任务
使用 Prefect 3.0 调度,采集 Tushare 板块行情数据
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


def collect_and_save_sectors_public(method: str, target_table: str, quotes_name: str,
                           conflict_columns: List[str] = None, page_size: int = 2000, **kwargs):
    """采集板块数据并保存到数据库（公共函数）

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
                return True

            prefix_log_print(quotes_name, 'error', "数据保存失败")
            return False

        page_count = len(data)
        prefix_log_print(quotes_name, 'info', f"第{offset//page_size + 1}页,获取 {page_count} 条数据")

        all_data.append(data)
        offset += page_size


@task(name="collect_and_save_dc_daily", retries=100, retry_delay_seconds=5)
def collect_and_save_dc_daily(trade_date: str):
    """采集东财概念板块行情并保存到数据库
    按照idx_type参数循环采集：概念板块、行业板块、地域板块
    """
    idx_types = ['概念板块', '行业板块', '地域板块']
    for idx_type in idx_types:
        prefix_log_print('dc_daily', 'info', f"开始采集 {idx_type} 数据")
        result = collect_and_save_sectors_public(
            method='dc_daily',
            target_table='aistockzml_tushare_dc_daily',
            quotes_name=f'dc_daily_{idx_type}',
            trade_date=trade_date,
            idx_type=idx_type,
            conflict_columns=['TS_CODE', 'TRADE_DATE']
        )


@task(name="collect_and_save_dc_index", retries=100, retry_delay_seconds=5)
def collect_and_save_dc_index(trade_date: str):
    """采集东方财富概念板块并保存到数据库"""
    return collect_and_save_sectors_public(
        method='dc_index',
        target_table='aistockzml_tushare_dc_index',
        quotes_name='dc_index',
        trade_date=trade_date,
        conflict_columns=['TS_CODE', 'TRADE_DATE']
    )


@task(name="collect_and_save_dc_member", retries=100, retry_delay_seconds=5)
def collect_and_save_dc_member(trade_date: str):
    """采集东方财富行业板块成员并保存到数据库"""
    return collect_and_save_sectors_public(
        method='dc_member',
        target_table='aistockzml_tushare_dc_member',
        quotes_name='dc_member',
        trade_date=trade_date,
        page_size=5000,
        conflict_columns=['TS_CODE', 'TRADE_DATE', 'CON_CODE']
    )



@flow(name="股票板块数据采集流程")
def sectors_flow():
    """板块数据采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")

    today = '20260226'
    # collect_and_save_dc_daily(today)
    # collect_and_save_dc_index(today)
    collect_and_save_dc_member(today)



if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    sectors_flow()
    print("\n测试完成!")
