# -*- coding: utf-8 -*-
"""
财务报表数据采集任务

使用 Prefect 3.0 调度，采集 Tushare 财务报表数据
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


def collect_and_save_financial_report(method: str, report_name: str, 
                                       target_table: str, today: str,
                                       **kwargs):
    """采集并保存财务报表数据的公共函数
    
    Args:
        method: Tushare API 方法名
        report_name: 报表名称（用于日志）
        target_table: 目标数据库表名
        today: 采集日期
        **kwargs: 动态参数
    """
    logger.info(f"开始采集 {report_name} 数据 (日期: {today})")

    params = {
        'method': method,
        'ann_date': today,
        'fields': '*'
    }
    
    # 合并动态参数
    params.update(kwargs)
    logger.info(f"采集参数: {params}")

    data = ts_collector.collect(**params)

    if data is not None and not data.empty:
        data['_UPDATE_TIME_DT'] = pd.to_datetime(data['UPDATE_TIME'], format='%Y-%m-%d %H:%M:%S')
        data = data.sort_values('_UPDATE_TIME_DT', ascending=False).drop_duplicates(
            subset=['TS_CODE', 'END_DATE'], keep='first'
        )
        data = data.drop(columns=['_UPDATE_TIME_DT']).reset_index(drop=True)
        logger.info(f"[{report_name}] 去重后数据: {len(data)} 条")
        
        ts_collector.save(
            data,
            target_table=target_table,
            conflict_columns=['TS_CODE', 'END_DATE'],
            insert_mode='incremental'
        )
    else:
        logger.warning(f"无数据需要保存({report_name})")


@task(name="collect_and_save_income")
def collect_and_save_income(today):
    """采集利润表并保存到数据库"""
    collect_and_save_financial_report(
        method='income_vip',
        report_name='income',
        target_table='aistockzml_tushare_income',
        today=today,
        report_type='1',
    )


@task(name="collect_and_save_balancesheet")
def collect_and_save_balancesheet(today):
    """采集资产负债表并保存到数据库"""
    collect_and_save_financial_report(
        method='balancesheet_vip',
        report_name='balancesheet',
        target_table='aistockzml_tushare_balancesheet',
        today=today,
        report_type='1',
    )


@task(name="collect_and_save_cashflow")
def collect_and_save_cashflow(today):
    """采集现金流量表并保存到数据库"""
    collect_and_save_financial_report(
        method='cashflow_vip',
        report_name='cashflow',
        target_table='aistockzml_tushare_cashflow',
        today=today,
        report_type='1',
    )

@task(name="collect_and_save_forecast")
def collect_and_save_forecast(today):
    """采集业绩预告并保存到数据库"""
    collect_and_save_financial_report(
        method='forecast_vip',
        report_name='forecast',
        target_table='aistockzml_tushare_forecast',
        today=today,
        report_type='1',
    )

@task(name="collect_and_save_express")
def collect_and_save_express(today):
    """采集业绩快报并保存到数据库"""
    collect_and_save_financial_report(
        method='express_vip',
        report_name='express',
        target_table='aistockzml_tushare_express',
        today=today,
        report_type='1',
    )

@task(name="collect_and_save_fina_indicator")
def collect_and_save_fina_indicator(today):
    """采集财务指标并保存到数据库"""
    collect_and_save_financial_report(
        method='fina_indicator_vip',
        report_name='indicator',
        target_table='aistockzml_tushare_fina_indicator',
        today=today
    )


@flow(name="财务报表采集流程")
def financial_report_flow():
    """财务报表采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行财务报表采集任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)

    today = '20260109'

    # collect_and_save_income(today)
    # collect_and_save_balancesheet(today)
    # collect_and_save_cashflow(today)
    # collect_and_save_forecast(today)
    # collect_and_save_express('20260128')
    # collect_and_save_fina_indicator('20260128')

    logger.info("=" * 50)
    logger.info("财务报表采集任务完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("财务报表采集任务 - 本地测试")
    print("=" * 50)
    financial_report_flow()
    print("\n测试完成!")
