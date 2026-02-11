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


def collect_and_save_quotes(method: str, target_table: str, quotes_name: str, trade_date: str, 
                           max_retries: int = 100, retry_interval: int = 5,
                           conflict_columns: List[str] = None, **kwargs):
    """采集行情数据并保存到数据库（公共函数）
    
    Args:
        method: Tushare API 方法名
        target_table: 目标数据库表名
        quotes_name: 行情名称(用于日志)
        trade_date: 交易日期
        max_retries: 最大重试次数(默认100次)
        retry_interval: 重试间隔秒数(默认5秒)
        conflict_columns: 冲突判断列名列表(默认None则使用TS_CODE, TRADE_DATE)
        **kwargs: 动态参数
    """
    if conflict_columns is None:
        conflict_columns = ['TS_CODE', 'TRADE_DATE']
    
    params = {
        'method': method,
        'trade_date': trade_date,
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


@task(name="collect_and_save_daily")
def collect_and_save_daily(trade_date: str):
    """采集日线行情(日k-历史)-未复权行情并保存到数据库"""
    collect_and_save_quotes(
        method='daily',
        target_table='aistockzml_tushare_daily',
        quotes_name='daily',
        trade_date=trade_date
    )


@task(name="collect_and_save_weekly")
def collect_and_save_weekly(trade_date: str):
    """采集周线行情(周k-历史)-未复权行情并保存到数据库
    ps:只有一周的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='weekly',
        target_table='aistockzml_tushare_weekly',
        quotes_name='weekly',
        trade_date=trade_date
    )


def collect_and_save_monthly(trade_date: str):
    """采集月线行情(月k-历史)-未复权行情并保存到数据库
    ps:只有一个月的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='monthly',
        target_table='aistockzml_tushare_monthly',
        quotes_name='monthly',
        trade_date=trade_date
    )  


@task(name="collect_and_save_stk_weekly_adj")
def collect_and_save_stk_weekly_unadj(trade_date: str):
    """采集周线行情(周k-每日更新)-未复权行情并保存到数据库
    ps:只有一周的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_weekly_monthly',
        target_table='aistockzml_tushare_stk_weekly_unadj',
        quotes_name='stk_weekly_unadj',
        trade_date=trade_date,
        freq='week'
    )  


@task(name="collect_and_save_stk_monthly_unadj")
def collect_and_save_stk_monthly_unadj(trade_date: str):
    """采集月线行情(月k-每日更新)-未复权行情并保存到数据库
    ps:只有一个月的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_weekly_monthly',
        target_table='aistockzml_tushare_stk_monthly_unadj',
        quotes_name='stk_monthly_unadj',
        trade_date=trade_date,
        freq='month'
    )  


@task(name="collect_and_save_stk_weekly_adj")
def collect_and_save_stk_weekly_adj(trade_date: str):
    """采集周线行情-每日更新-复权行情并保存到数据库
    ps:只有一周的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_week_month_adj',
        target_table='aistockzml_tushare_stk_weekly_adj',
        quotes_name='stk_weekly_adj',
        trade_date=trade_date,
        freq='week'
    )  


@task(name="collect_and_save_stk_monthly_adj")
def collect_and_save_stk_monthly_adj(trade_date: str):
    """采集月线行情-每日更新-复权行情并保存到数据库
    ps:只有一个月的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_week_month_adj',
        target_table='aistockzml_tushare_stk_monthly_adj',
        quotes_name='stk_monthly_adj',
        trade_date=trade_date,
        freq='month'
    )  


@task(name="collect_and_save_daily_basic")
def collect_and_save_daily_basic(trade_date: str):
    """采集股票每日重要的基本面指标并保存到数据库"""
    collect_and_save_quotes(
        method='daily_basic',
        target_table='aistockzml_tushare_daily_basic',
        quotes_name='daily_basic',
        trade_date=trade_date
    )  


@task(name="collect_and_save_ggt_daily")
def collect_and_save_ggt_daily(trade_date: str):
    """采集港股通每日成交统计并保存到数据库"""
    collect_and_save_quotes(
        method='ggt_daily',
        target_table='aistockzml_tushare_ggt_daily',
        quotes_name='ggt_daily',
        trade_date=trade_date,
        conflict_columns=['trade_date']
    )  


@flow(name="股票行情采集流程")
def quotes_flow():
    """日线行情采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    today = '20260210'
    # collect_and_save_daily(today)
    # collect_and_save_weekly(today)
    # collect_and_save_monthly(today)
    # collect_and_save_stk_weekly_unadj(today)
    # collect_and_save_stk_monthly_unadj(today)
    # collect_and_save_stk_weekly_adj(today)
    # collect_and_save_stk_monthly_adj(today)
    # collect_and_save_daily_basic(today)
    collect_and_save_ggt_daily(today)

    logger.info("=" * 50)
    logger.info("定时任务完成")
    logger.info("=" * 50)   


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    quotes_flow()
    print("\n测试完成!")

