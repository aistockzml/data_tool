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


@task(name="get_trade_dates")
def get_trade_dates(start_date=None, end_date=None):
    """获取上交所近一周的交易日期，深圳交易所一般和上交所同步"""
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")

    try:
        trade_cal = ts_collector.collect(
            method='trade_cal',
            fields='cal_date',
            start_date=start_date,
            end_date=end_date,
            exchange='SSE',
            is_open='1',
        )

        trade_cal = trade_cal['cal_date'].tolist()

    except Exception as e:
        logger.error(f"获取交易日历失败: {e}")
        trade_cal = []

    return trade_cal


@task(name="check_is_trading_day")
def check_is_trading_day(trade_cal: list):
    """检查今天是否为交易日（仅检查上交所）"""
    today = datetime.now().strftime("%Y%m%d")

    if trade_cal:
        is_trading_day = today in trade_cal
    else:
        is_trading_day = False

    logger.info(f"({today}) 是否为交易日: {is_trading_day}")

    return is_trading_day, today  


@task(name="collect_and_save_stock_basic")
def collect_and_save_stock_basic():
    """采集股票列表并保存到数据库"""
    data = ts_collector.collect(
        method='stock_basic',
        fields='*'
    )

    if data is not None and not data.empty:
        ts_collector.save(
            data,
            target_table='aistockzml_tushare_stock_basic',
            insert_mode='overwrite'
        )
    else:
        logger.warning(f"无数据需要保存(stock_basic)")


@task(name="collect_and_save_stock_hsgt")
def collect_and_save_stock_hsgt(today):
    """采集沪深港通股票列表并保存到数据库"""

    for es_type in ['HK_SZ', 'SZ_HK', 'HK_SH', 'SH_HK']:
        data = ts_collector.collect(
            method='stock_hsgt',
            trade_date=today,
            type=es_type,
            fields='*'
        )

        if data is not None and not data.empty:
            # 每次只采集当前日期的数据，不追加数据
            if es_type == 'HK_SZ':
                insert_mode = 'overwrite'
            else:
                insert_mode = 'incremental'

            ts_collector.save(
                data,
                target_table=f'aistockzml_tushare_stock_hsgt',
                insert_mode=insert_mode
            )
        else:
            logger.warning(f"无数据需要保存(stock_hsgt)({es_type})")   


@task(name="collect_and_save_stock_company")
def collect_and_save_stock_company():
    """采集上市公司基本信息并保存到数据库"""

    for exchange in ['SSE', 'SZSE', 'BSE']:
        data = ts_collector.collect(
            method='stock_company',
            exchange=exchange,
            fields='*'
        )

        if data is not None and not data.empty:
            if exchange == 'SSE':
                insert_mode = 'overwrite'
            else:
                insert_mode = 'incremental'

            ts_collector.save(
                data,
                target_table='aistockzml_tushare_stock_company',
                insert_mode=insert_mode
            )
        else:
            logger.warning(f"无数据需要保存(stock_company)({exchange})")


@flow(name="股票基础信息采集流程")
def stock_basic_flow():
    """股票基础信息采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)

    trade_cal = get_trade_dates()
    is_trading_day, today = check_is_trading_day(trade_cal)

    if is_trading_day:
        collect_and_save_stock_basic()
        collect_and_save_stock_hsgt(today)
        collect_and_save_stock_company()

    logger.info("=" * 50)
    logger.info("定时任务完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    stock_basic_flow()
    print("\n测试完成!")
