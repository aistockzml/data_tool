"""
股票其他数据采集任务
使用 Prefect 3.0 调度,采集 Tushare 股票其他数据 
"""

import sys
import os
import time
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


def collect_and_save_others_public(method: str, target_table: str, quotes_name: str, 
                           max_retries: int = 100, retry_interval: int = 5,
                           conflict_columns: List[str] = None, **kwargs):
    """采集股票其他数据并保存到数据库（公共函数）   
    
    Args:
        method: Tushare API 方法名
        target_table: 目标数据库表名
        quotes_name: 行情名称(用于日志)
        max_retries: 最大重试次数(默认100次)
        retry_interval: 重试间隔秒数(默认5秒)
        conflict_columns: 冲突判断列名列表(默认None则使用TS_CODE, TRADE_DATE)
        **kwargs: 动态参数
    """
    if conflict_columns is None:
        conflict_columns = ['TS_CODE', 'TRADE_DATE']
    
    params = {
        'method': method,
        'fields': '*'
    }
    params.update(kwargs)
    logger.info(f"采集参数: {params}")

    for attempt in range(1, max_retries + 1):
        try:
            data = ts_collector.collect(**params)

            if data is not None and not data.empty:
                result = ts_collector.save(
                    data,
                    target_table=target_table,
                    insert_mode='incremental',
                    conflict_columns=conflict_columns
                )
                
                return result is not None and result > 0
            else:
                return True
                
        except Exception as e:
            logger.error(f"[{quotes_name}] 第{attempt}次尝试失败: {e}")
            
        if attempt < max_retries:
            logger.info(f"[{quotes_name}] 等待{retry_interval}秒后进行第{attempt + 1}次重试...")
            time.sleep(retry_interval)
    
    logger.error(f"[{quotes_name}] 已达到最大重试次数({max_retries})，任务失败")
    return False


@task(name="collect_and_save_repurchase")
def collect_and_save_repurchase(trade_date: str, days: int = 30):
    """采集股票回购交易数据并保存到数据库（查询近days天数据）"""
    start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=days)).strftime('%Y%m%d')
    
    return collect_and_save_others_public(
        method='repurchase',
        target_table='aistockzml_tushare_repurchase',
        quotes_name='repurchase',
        start_date=start_date,
        end_date=trade_date,
        conflict_columns=['ID']
    )


@task(name="collect_and_save_block_trade")
def collect_and_save_block_trade(trade_date: str, days: int = 30):
    """采集大宗交易数据并保存到数据库（查询近days天数据）"""
    start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=days)).strftime('%Y%m%d')
    
    return collect_and_save_others_public(
        method='block_trade',
        target_table='aistockzml_tushare_block_trade',
        quotes_name='block_trade',
        start_date=start_date,
        end_date=trade_date,
        conflict_columns=['ID']
    )


@task(name="collect_and_save_stk_holdernumber")
def collect_and_save_stk_holdernumber(trade_date: str, days: int = 30):
    """采集股东人数并保存到数据库（查询近days天数据）"""
    start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=days)).strftime('%Y%m%d')
    
    return collect_and_save_others_public(
        method='stk_holdernumber',
        target_table='aistockzml_tushare_stk_holdernumber',
        quotes_name='stk_holdernumber',
        start_date=start_date,
        end_date=trade_date,
        conflict_columns=['ID']
    )


@task(name="collect_and_save_stk_holdertrade")
def collect_and_save__stk_holdertrade(trade_date: str, days: int = 30):
    """采集股东增减持并保存到数据库（查询近days天数据）"""
    start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=days)).strftime('%Y%m%d')
    
    return collect_and_save_others_public(
        method='stk_holdertrade',
        target_table='aistockzml_tushare_stk_holdertrade',
        quotes_name='stk_holdertrade',
        start_date=start_date,
        end_date=trade_date,
        conflict_columns=['ID']
    )


@flow(name="股票其他数据采集流程")
def others_flow():
    """其他数据采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    today = '20260212'
    # collect_and_save_repurchase(today, days=5)
    # collect_and_save_block_trade(today, days=1)
    # collect_and_save_stk_holdernumber(today, days=1)
    collect_and_save__stk_holdertrade(today, days=3)

    logger.info("=" * 50)
    logger.info("定时任务完成")
    logger.info("=" * 50)   


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    others_flow()
    print("\n测试完成!")