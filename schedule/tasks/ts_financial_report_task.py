# -*- coding: utf-8 -*-
"""
财务报表数据采集任务

使用 Prefect 3.0 调度,采集 Tushare 财务报表数据

注意:进行去重和upsert操作，一个报告期的财务报表数据只保存一条记录
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime
from typing import List

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from prefect import flow, task
from prefect.task_runners import ThreadPoolTaskRunner
from schedule import logger, ts_collector, get_quarter_end_dates, get_date_range_list


def prefix_log_print(report_name: str, level: str, message: str):
    getattr(logger, level)(f"[{report_name}] {message}")


def _deduplicate_data(data: pd.DataFrame, conflict_columns: List[str]) -> pd.DataFrame:
    data = data.assign(_UPDATE_TIME_DT=pd.to_datetime(data['UPDATE_TIME'], format='%Y-%m-%d %H:%M:%S'))
    data = data.sort_values('_UPDATE_TIME_DT', ascending=False).drop_duplicates(
        subset=conflict_columns, keep='first'
    )
    return data.drop(columns=['_UPDATE_TIME_DT']).reset_index(drop=True)


def collect_and_save_financial_report(
    method: str,
    report_name: str,
    target_table: str,
    max_retries: int = 100,
    retry_interval: int = 5,
    dedup: bool = True,
    conflict_columns: List[str] = None,
    page_size: int = 2000,
    **kwargs
) -> bool:
    """采集并保存财务报表数据
    
    Args:
        method: Tushare API 方法名
        report_name: 报表名称(用于日志)
        target_table: 目标数据库表名
        max_retries: 最大重试次数(默认100次)
        retry_interval: 重试间隔秒数(默认5秒)
        dedup: 是否去重(默认True),按conflict_columns分组后取UPDATE_TIME最新的记录
        conflict_columns: 冲突判断列名列表,用于去重和upsert(默认None则使用TS_CODE, END_DATE)
        page_size: 分页大小(默认5000)
        **kwargs: 动态参数
        
    Returns:
        bool: 是否成功
    """
    if conflict_columns is None:
        conflict_columns = ['TS_CODE', 'END_DATE']

    params = {'method': method, 'fields': '*', **kwargs}
    prefix_log_print(report_name, 'info', f"采集参数: {params}")

    all_data = []
    total_count = 0
    offset = 0
    
    while True:
        for attempt in range(1, max_retries + 1):
            try:
                page_params = {**params, 'limit': page_size, 'offset': offset}
                data = ts_collector.collect(**page_params)
                
                if data is None or data.empty:
                    prefix_log_print(report_name, 'info', f"分页采集完成,共采集 {total_count} 条数据")
                    
                    if not all_data:
                        prefix_log_print(report_name, 'info', "无数据需要保存")
                        return True
                    
                    combined_data = pd.concat(all_data, ignore_index=True)
                    prefix_log_print(report_name, 'info', f"合并后数据: {len(combined_data)} 条")
                    
                    if dedup:
                        combined_data = _deduplicate_data(combined_data, conflict_columns)
                        prefix_log_print(report_name, 'info', f"去重后数据: {len(combined_data)} 条")
                    
                    if ts_collector.save(combined_data, target_table=target_table, conflict_columns=conflict_columns, insert_mode='incremental'):
                        prefix_log_print(report_name, 'info', f"数据保存成功,共保存 {len(combined_data)} 条")
                        return True
                    
                    prefix_log_print(report_name, 'error', "数据保存失败")
                    return False
                
                page_count = len(data)
                prefix_log_print(report_name, 'info', f"第{offset//page_size + 1}页,获取 {page_count} 条数据")
                
                all_data.append(data)
                total_count += page_count
                offset += page_size
                break
                
            except Exception as e:
                prefix_log_print(report_name, 'error', f"第{attempt}次尝试失败: {e}")
            
            if attempt < max_retries:
                prefix_log_print(report_name, 'info', f"等待{retry_interval}秒后进行第{attempt + 1}次重试...")
                time.sleep(retry_interval)
        else:
            prefix_log_print(report_name, 'error', f"已达到最大重试次数({max_retries}),任务失败")
            return False


@task(name="collect_and_save_income")
def collect_and_save_income(period: str):
    """采集利润表并保存到数据库,主键为TS_CODE, END_DATE
    period: 报告期,格式YYYYMMDD,季度末日期,例如20240331
    """
    collect_and_save_financial_report(
        method='income_vip',
        report_name='income',
        target_table='aistockzml_tushare_income',
        period=period,
        report_type='1',
        conflict_columns=['TS_CODE', 'END_DATE'],
    )


@task(name="collect_and_save_balancesheet")
def collect_and_save_balancesheet(period: str):
    """采集资产负债表并保存到数据库,主键为TS_CODE, END_DATE
    period: 报告期,格式YYYYMMDD,季度末日期,例如20240331
    """
    collect_and_save_financial_report(
        method='balancesheet_vip',
        report_name='balancesheet',
        target_table='aistockzml_tushare_balancesheet',
        period=period,
        report_type='1',
        conflict_columns=['TS_CODE', 'END_DATE'],
    )


@task(name="collect_and_save_cashflow")
def collect_and_save_cashflow(period: str):
    """采集现金流量表并保存到数据库"""
    collect_and_save_financial_report(
        method='cashflow_vip',
        report_name='cashflow',
        target_table='aistockzml_tushare_cashflow',
        period=period,
        report_type='1',
        conflict_columns=['TS_CODE', 'END_DATE']
    )


@task(name="collect_and_save_forecast")
def collect_and_save_forecast(period: str):
    """采集业绩预告并保存到数据库"""
    collect_and_save_financial_report(
        method='forecast_vip',
        report_name='forecast',
        target_table='aistockzml_tushare_forecast',
        period=period,
        conflict_columns=['TS_CODE', 'END_DATE']
    )


@task(name="collect_and_save_express")
def collect_and_save_express(period: str):
    """采集业绩快报并保存到数据库"""
    collect_and_save_financial_report(
        method='express_vip',
        report_name='express',
        target_table='aistockzml_tushare_express',
        period=period,
        conflict_columns=['TS_CODE', 'END_DATE']
    )


@task(name="collect_and_save_fina_indicator")
def collect_and_save_fina_indicator(period: str):
    """采集财务指标并保存到数据库"""
    collect_and_save_financial_report(
        method='fina_indicator_vip',
        report_name='fina_indicator',
        target_table='aistockzml_tushare_fina_indicator',
        period=period,
        conflict_columns=['TS_CODE', 'END_DATE']
    )


@task(name="collect_and_save_disclosure_date")
def collect_and_save_disclosure_date(end_date: str):
    """采集财务报表披露日期并保存到数据库"""
    collect_and_save_financial_report(
        method='disclosure_date',
        report_name='disclosure_date',
        target_table='aistockzml_tushare_disclosure_date',
        end_date=end_date, # 注意，接口参数不是period
        conflict_columns=['TS_CODE', 'END_DATE']
    )

@task(name="collect_and_save_financial_dividend")
def collect_and_save_financial_dividend(ann_date: str):
    """采集分红送股并保存到数据库，按照每个公告日期采集"""
    collect_and_save_financial_report(
        method='dividend_vip',
        report_name='dividend',
        target_table='aistockzml_tushare_dividend', 
        ann_date=ann_date,
        dedup=False,
        conflict_columns=['TS_CODE', 'DIV_PROC', 'ANN_DATE']
    )
    time.sleep(0.2)


@flow(name="财务报表采集流程")
def financial_report_flow():
    """财务报表采集主流程"""
    logger.info("=" * 50)
    logger.info("开始执行财务报表采集任务")
    logger.info(f"执行时间: {datetime.now()}")
    logger.info("=" * 50)
    
    today = datetime.now().strftime('%Y%m%d')

    # quarter_end_dates = get_quarter_end_dates(today, periods=40)
    # logger.info(f"当前季度及前3季度末日期列表: {quarter_end_dates}")
    # for period in quarter_end_dates:
    #     collect_and_save_income(period)   
    #     collect_and_save_balancesheet(period)
    #     collect_and_save_cashflow(period)
    #     collect_and_save_forecast(period)
    #     collect_and_save_express(period)
    #     collect_and_save_fina_indicator(period)   
    #     collect_and_save_disclosure_date(end_date=period)

    dividend_dates = get_date_range_list(today, start_days_ago=1825, end_days_ago=0)
    logger.info(f"近10天分红公告日期列表: {dividend_dates}")

    for ann_date in dividend_dates:
        collect_and_save_financial_dividend(ann_date)

    logger.info("=" * 50)
    logger.info("财务报表采集任务完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("财务报表采集任务 - 本地测试")
    print("=" * 50)
    financial_report_flow()
    print("\n测试完成!")
