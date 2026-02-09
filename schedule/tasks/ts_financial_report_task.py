# -*- coding: utf-8 -*-
"""
财务报表数据采集任务

使用 Prefect 3.0 调度，采集 Tushare 财务报表数据
"""

import sys
import os
import time
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


def collect_and_save_financial_report(method: str, report_name: str, target_table: str, 
                                       max_retries: int = 100, retry_interval: int = 5, **kwargs):
    """采集并保存财务报表数据的公共函数
    
    Args:
        method: Tushare API 方法名
        report_name: 报表名称（用于日志）
        target_table: 目标数据库表名
        max_retries: 最大重试次数（默认100次）
        retry_interval: 重试间隔秒数（默认5秒）
        **kwargs: 动态参数
    """
    params = {
        'method': method,
        'fields': '*'
    }
    
    # 合并动态参数
    params.update(kwargs)
    logger.info(f"采集参数: {params}")

    for attempt in range(1, max_retries + 1):
        try:
            data = ts_collector.collect(**params)

            if data is not None and not data.empty:
                data['_UPDATE_TIME_DT'] = pd.to_datetime(data['UPDATE_TIME'], format='%Y-%m-%d %H:%M:%S')
                data = data.sort_values('_UPDATE_TIME_DT', ascending=False).drop_duplicates(
                    subset=['TS_CODE', 'END_DATE'], keep='first'
                )
                data = data.drop(columns=['_UPDATE_TIME_DT']).reset_index(drop=True)
                logger.info(f"[{report_name}] 去重后数据: {len(data)} 条")
                
                result = ts_collector.save(
                    data,
                    target_table=target_table,
                    conflict_columns=['TS_CODE', 'END_DATE'],
                    insert_mode='incremental'
                )
                
                if result:
                    logger.info(f"[{report_name}] 数据保存成功")
                    return True
                else:
                    logger.warning(f"[{report_name}] 数据保存返回失败，准备重试")
            else:
                logger.info(f"[{report_name}] 无数据需要保存")
                return True
                
        except Exception as e:
            logger.error(f"[{report_name}] 第{attempt}次尝试失败: {e}")
            
        if attempt < max_retries:
            logger.info(f"[{report_name}] 等待{retry_interval}秒后进行第{attempt + 1}次重试...")
            time.sleep(retry_interval)
    
    logger.error(f"[{report_name}] 已达到最大重试次数({max_retries})，任务失败")
    return False


@task(name="collect_and_save_income")
def collect_and_save_income(start_date: str, end_date: str):
    """采集利润表并保存到数据库"""
    collect_and_save_financial_report(
        method='income_vip',
        report_name='income',
        target_table='aistockzml_tushare_income',
        start_date=start_date,
        end_date=end_date,
        report_type='1',
    )


@task(name="collect_and_save_balancesheet")
def collect_and_save_balancesheet(start_date: str, end_date: str):
    """采集资产负债表并保存到数据库"""
    collect_and_save_financial_report(
        method='balancesheet_vip',
        report_name='balancesheet',
        target_table='aistockzml_tushare_balancesheet',
        start_date=start_date,
        end_date=end_date,
        report_type='1',
    )


@task(name="collect_and_save_cashflow")
def collect_and_save_cashflow(start_date: str, end_date: str):
    """采集现金流量表并保存到数据库"""
    collect_and_save_financial_report(
        method='cashflow_vip',
        report_name='cashflow',
        target_table='aistockzml_tushare_cashflow',
        start_date=start_date,
        end_date=end_date,
        report_type='1',
    )


@task(name="collect_and_save_forecast")
def collect_and_save_forecast(start_date: str, end_date: str):
    """采集业绩预告并保存到数据库"""
    collect_and_save_financial_report(
        method='forecast_vip',
        report_name='forecast',
        target_table='aistockzml_tushare_forecast',
        start_date=start_date,
        end_date=end_date,
        report_type='1',
    )

@task(name="collect_and_save_express")
def collect_and_save_express(start_date: str, end_date: str):
    """采集业绩快报并保存到数据库"""
    collect_and_save_financial_report(
        method='express_vip',
        report_name='express',
        target_table='aistockzml_tushare_express',
        start_date=start_date,
        end_date=end_date,
        report_type='1',
    )


@task(name="collect_and_save_fina_indicator")
def collect_and_save_fina_indicator(period: str):
    """采集财务指标并保存到数据库"""
    collect_and_save_financial_report(
        method='fina_indicator_vip',
        report_name='fina_indicator',
        target_table='aistockzml_tushare_fina_indicator',
        period=period
    )


@flow(name="财务报表采集流程")
def financial_report_flow():
    """财务报表采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行财务报表采集任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    # 执行财务报表采集任务，时间范围为最近一周的日期(包含今天，以及周末的日期)
    # today = '20250624'
    # # today = datetime.now().strftime("%Y%m%d")
    # today_date = datetime.strptime(today, '%Y%m%d')
    # start_date = (today_date - timedelta(days=1)).strftime('%Y%m%d')
    # end_date = (today_date + timedelta(days=1)).strftime('%Y%m%d')
    # logger.info(f"开始采集财务报表数据 (日期范围: {start_date} - {end_date})")

    # collect_and_save_income(start_date, end_date)
    # collect_and_save_balancesheet(start_date, end_date)
    # collect_and_save_cashflow(start_date, end_date)
    # collect_and_save_forecast(start_date, end_date)
    # collect_and_save_express(start_date, end_date)

    # date_list = pd.date_range(start=start_date, end=end_date, freq='D').strftime('%Y%m%d').tolist()

    # for ann_date in date_list:
    #     collect_and_save_fina_indicator(ann_date)   

    # 生成近1年每个季度最后一天日期
    # current_year = datetime.now().year
    # 生成近360天每个季度最后一天日期
    # 生成当前季度以及前3个季度末日期（共4个季度）
    # 生成当前季度末及前3个季度末（共4个季度）
    current_quarter_end = pd.Timestamp.now() + pd.offsets.QuarterEnd(0)
    quarter_end_dates = pd.date_range(
        end=current_quarter_end,
        periods=4,
        freq='QE'
    ).strftime('%Y%m%d').tolist()
    logger.info(f"当前季度及前3季度末日期列表: {quarter_end_dates}")

    for period in quarter_end_dates:
        collect_and_save_fina_indicator(period)   

    logger.info("=" * 50)
    logger.info("财务报表采集任务完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("财务报表采集任务 - 本地测试")
    print("=" * 50)
    financial_report_flow()
    print("\n测试完成!")
