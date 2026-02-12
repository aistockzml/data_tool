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


def collect_and_save_moneyflow_public(method: str, target_table: str, quotes_name: str, trade_date: str, 
                           max_retries: int = 100, retry_interval: int = 5,
                           conflict_columns: List[str] = None, **kwargs):
    """采集股票资金流数据并保存到数据库（公共函数）
    
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


@task(name="collect_and_save_moneyflow")
def collect_and_save_moneyflow(trade_date: str):
    """采集股票资金流数据并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow',
        target_table='aistockzml_tushare_moneyflow',
        quotes_name='moneyflow',
        trade_date=trade_date
    )


@task(name="collect_and_save_moneyflow_ths")
def collect_and_save_moneyflow_ths(trade_date: str):
    """采集股票资金流数据_同花顺并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_ths',
        target_table='aistockzml_tushare_moneyflow_ths',
        quotes_name='moneyflow_ths',
        trade_date=trade_date
    )


@task(name="collect_and_save_moneyflow_dc")
def collect_and_save_moneyflow_dc(trade_date: str):
    """采集股票资金流数据_东方财富并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_dc',
        target_table='aistockzml_tushare_moneyflow_dc',
        quotes_name='moneyflow_dc',
        trade_date=trade_date
    )

@task(name="collect_and_save_moneyflow_cnt_ths")
def collect_and_save_moneyflow_cnt_ths(trade_date: str):
    """采集同花顺概念板块资金流向(THS)并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_cnt_ths',
        target_table='aistockzml_tushare_moneyflow_cnt_ths',
        quotes_name='moneyflow_cnt_ths',
        trade_date=trade_date
    )


@task(name="collect_and_save_moneyflow_ind_ths")
def collect_and_save_moneyflow_ind_ths(trade_date: str):
    """采集同花顺行业板块资金流向(THS)并保存到数据库"""
    return collect_and_save_moneyflow_public(
        method='moneyflow_ind_ths',
        target_table='aistockzml_tushare_moneyflow_ind_ths',
        quotes_name='moneyflow_ind_ths',
        trade_date=trade_date
    )


@flow(name="股票资金流数据采集流程")
def moneyflow_flow():
    """资金流数据采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行定时任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    today = '20260211'
    # collect_and_save_moneyflow(today)
    # collect_and_save_moneyflow_ths(today)
    # collect_and_save_moneyflow_dc(today)
    # collect_and_save_moneyflow_cnt_ths(today)
    collect_and_save_moneyflow_ind_ths(today)

    logger.info("=" * 50)
    logger.info("定时任务完成")
    logger.info("=" * 50)   


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    moneyflow_flow()
    print("\n测试完成!")

