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
from schedule import logger, ts_collector, get_week_friday, get_month_last_day, get_date_range_list


def prefix_log_print(report_name: str, level: str, message: str):
    getattr(logger, level)(f"[{report_name}] {message}")


@task(name="get_last_trade_date", retries=100, retry_delay_seconds=10)
def get_last_trade_date(base_date: str, freq: str = 'week') -> str:
    """获取指定日期所在周/月的最后一个交易日
    
    Args:
        base_date: 基准日期,格式为 'YYYYMMDD'
        freq: 周期类型, 'week' 或 'month'
        
    Returns:
        最后一个交易日日期,格式为 'YYYYMMDD'，如果没有交易日则返回 None
        
    Example:
        >>> get_last_trade_date('20260213', freq='week')
        '20260213'  # 本周最后一个交易日
        >>> get_last_trade_date('20260213', freq='month')
        '20260227'  # 本月最后一个交易日
    """
    base = datetime.strptime(base_date, '%Y%m%d')
    
    if freq == 'week':
        week_start = base - timedelta(days=base.weekday())
        week_end = week_start + timedelta(days=6)
        start_date = week_start.strftime('%Y%m%d')
        end_date = week_end.strftime('%Y%m%d')
    elif freq == 'month':
        month_start = base.replace(day=1)
        month_end = month_start + pd.offsets.MonthEnd(0)
        start_date = month_start.strftime('%Y%m%d')
        end_date = month_end.strftime('%Y%m%d')
    else:
        return None
    
    trade_cal = ts_collector.collect(
        method='trade_cal',
        fields='cal_date',
        start_date=start_date,
        end_date=end_date,
        exchange='SSE',
        is_open='1',
    )
    
    if trade_cal is not None and not trade_cal.empty:
        trade_dates = trade_cal['cal_date'].sort_values().tolist()
        return trade_dates[-1]
    
    return None


def collect_and_save_quotes(method: str, target_table: str, quotes_name: str, trade_date: str,
                           conflict_columns: List[str] = None, page_size: int = 2000, **kwargs) -> bool:
    """采集行情数据并保存到数据库（公共函数）
    
    Args:
        method: Tushare API 方法名
        target_table: 目标数据库表名
        quotes_name: 行情名称(用于日志)
        trade_date: 交易日期
        conflict_columns: 冲突判断列名列表(默认None则使用TS_CODE, TRADE_DATE)
        page_size: 分页大小(默认2000)
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
            prefix_log_print(quotes_name, 'info', f"采集完成,共 {len(combined_data)} 条数据")
            
            if ts_collector.save(combined_data, target_table=target_table, insert_mode='incremental', conflict_columns=conflict_columns):
                prefix_log_print(quotes_name, 'info', f"数据保存成功(incremental),共 {len(combined_data)} 条")
                return True
            
            prefix_log_print(quotes_name, 'error', "数据保存失败")
            return False
        
        page_count = len(data)
        prefix_log_print(quotes_name, 'info', f"第{offset//page_size + 1}页,获取 {page_count} 条数据")
        
        all_data.append(data)
        offset += page_size


@task(name="collect_and_save_daily", retries=100, retry_delay_seconds=10)
def collect_and_save_daily(trade_date: str):
    """采集日线行情(日k-历史)-未复权行情并保存到数据库"""
    collect_and_save_quotes(
        method='daily',
        target_table='aistockzml_tushare_daily',
        quotes_name='daily',
        trade_date=trade_date
    )


@task(name="collect_and_save_weekly", retries=100, retry_delay_seconds=10)
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


@task(name="collect_and_save_monthly", retries=100, retry_delay_seconds=10)
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


@task(name="collect_and_save_stk_weekly_unadj", retries=100, retry_delay_seconds=10)
def collect_and_save_stk_weekly_unadj(trade_date: str):
    """采集周线行情(周k-每日更新)-未复权行情并保存到数据库
    ps:只有一周的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_weekly_monthly',
        target_table='aistockzml_tushare_stk_weekly_unadj',
        quotes_name='stk_weekly_unadj',
        trade_date=trade_date,
        freq='week',
        page_size=6000 # 接口规定最多返回6000条,设置6000一次性返回全部,因为接口翻页功能有bug
    )


@task(name="collect_and_save_stk_monthly_unadj", retries=100, retry_delay_seconds=10)
def collect_and_save_stk_monthly_unadj(trade_date: str):
    """采集月线行情(月k-每日更新)-未复权行情并保存到数据库
    ps:只有一个月的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_weekly_monthly',
        target_table='aistockzml_tushare_stk_monthly_unadj',
        quotes_name='stk_monthly_unadj',
        trade_date=trade_date,
        freq='month',
        page_size=6000 # 接口规定最多返回6000条,设置6000一次性返回全部,因为接口翻页功能有bug
    )


@task(name="collect_and_save_stk_weekly_adj", retries=100, retry_delay_seconds=10)
def collect_and_save_stk_weekly_adj(trade_date: str):
    """采集周线行情-每日更新-复权行情并保存到数据库
    ps:只有一周的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_week_month_adj',
        target_table='aistockzml_tushare_stk_weekly_adj',
        quotes_name='stk_weekly_adj',
        trade_date=trade_date,
        freq='week',
        page_size=6000 # 接口规定最多返回6000条,设置6000一次性返回全部,因为接口翻页功能有bug
    )


@task(name="collect_and_save_stk_monthly_adj", retries=100, retry_delay_seconds=10)
def collect_and_save_stk_monthly_adj(trade_date: str):
    """采集月线行情-每日更新-复权行情并保存到数据库
    ps:只有一个月的最后一个交易日才会有数据
    """
    collect_and_save_quotes(
        method='stk_week_month_adj',
        target_table='aistockzml_tushare_stk_monthly_adj',
        quotes_name='stk_monthly_adj',
        trade_date=trade_date,
        freq='month',
        page_size=6000 # 接口规定最多返回6000条,设置6000一次性返回全部,因为接口翻页功能有bug
    )


@task(name="collect_and_save_daily_basic", retries=100, retry_delay_seconds=10)
def collect_and_save_daily_basic(trade_date: str):
    """采集日线行情-基础指标并保存到数据库"""
    collect_and_save_quotes(
        method='daily_basic',
        target_table='aistockzml_tushare_daily_basic',
        quotes_name='daily_basic',
        trade_date=trade_date
    )


@task(name="collect_and_save_ggt_daily", retries=100, retry_delay_seconds=10)
def collect_and_save_ggt_daily(trade_date: str):
    """采集港股通每日成交统计并保存到数据库"""
    collect_and_save_quotes(
        method='ggt_daily',
        target_table='aistockzml_tushare_ggt_daily',
        quotes_name='ggt_daily',
        trade_date=trade_date,
        conflict_columns=['TRADE_DATE']
    )


@task(name="collect_and_save_suspend_d", retries=100, retry_delay_seconds=10)
def collect_and_save_suspend_d(trade_date: str):
    """采集股票每日暂停交易信息并保存到数据库"""
    collect_and_save_quotes(
        method='suspend_d',
        target_table='aistockzml_tushare_suspend_d',
        quotes_name='suspend_d',
        trade_date=trade_date,
        conflict_columns=['UNIQUE_ID']
    )


@task(name="collect_and_save_bak_daily", retries=100, retry_delay_seconds=10)
def collect_and_save_bak_daily(trade_date: str):
    """采集股票每日行情-历史数据并保存到数据库"""
    collect_and_save_quotes(
        method='bak_daily',
        target_table='aistockzml_tushare_bak_daily',
        quotes_name='bak_daily',
        trade_date=trade_date
    )


@task(name="collect_and_save_stk_factor_pro", retries=100, retry_delay_seconds=10)
def collect_and_save_stk_factor_pro(trade_date: str):
    """采集日线行情-股票技术面因子表(专业版)并保存到数据库"""
    collect_and_save_quotes(
        method='stk_factor_pro',
        target_table='aistockzml_tushare_stk_factor_pro',
        quotes_name='stk_factor_pro',
        trade_date=trade_date
    )


@task(name="collect_and_save_cyq_perf", retries=100, retry_delay_seconds=10)
def collect_and_save_cyq_perf(trade_date: str):
    """采集每日筹码及胜率表并保存到数据库"""
    collect_and_save_quotes(
        method='cyq_perf',
        target_table='aistockzml_tushare_cyq_perf',
        quotes_name='cyq_perf',
        trade_date=trade_date,
        conflict_columns=['TS_CODE','TRADE_DATE_STR']
    )  


@flow(name="股票行情采集流程")
def quotes_flow():
    """日线行情采集主流程"""
    prefix_log_print('quotes', 'info', "=" * 50)
    prefix_log_print('quotes', 'info', f"执行时间: {datetime.now()}")

    base_date = '20260213'

    date_range_list = get_date_range_list(base_date, start_days_ago=365, end_days_after=0)

    for today in date_range_list:

        # 获取本周和本月最后一个交易日
        week_last_trade_date = get_last_trade_date(today, freq='week')
        month_last_trade_date = get_last_trade_date(today, freq='month')
        
        prefix_log_print('quotes', 'info', f"本周最后交易日: {week_last_trade_date}")
        prefix_log_print('quotes', 'info', f"本月最后交易日: {month_last_trade_date}")

        friday_date = get_week_friday(today)
        month_last_date = get_month_last_day(today)
        prefix_log_print('quotes', 'info', f"本周周五: {friday_date}")
        prefix_log_print('quotes', 'info', f"本月最后自然日: {month_last_date}")
        
        # 每日行情(未赋权), 只采集今天的数据
        collect_and_save_daily(today)

        # 周线和月线行情(非每天更新-未赋权),每周或每月最后一个交易日期(交易日)
        collect_and_save_weekly(week_last_trade_date)
        collect_and_save_monthly(month_last_trade_date)
        
        # 周线和月线行情(每天更新-未赋权),每周周五和每月最后一个天(自然日)
        collect_and_save_stk_weekly_unadj(friday_date)
        collect_and_save_stk_monthly_unadj(month_last_date)

        # 周线和月线行情(每天更新-赋权),每周周五和每月最后一个天(自然日)
        collect_and_save_stk_weekly_adj(friday_date)
        collect_and_save_stk_monthly_adj(month_last_date)

        # 每日指标, 只采集今天的数据
        collect_and_save_daily_basic(today)

        # 每日停复牌信息, 只采集今天的数据
        collect_and_save_suspend_d(today)

        # 备用行情
        collect_and_save_bak_daily(today)

        # 港股通每日成交统计, 只采集今天的数据
        collect_and_save_ggt_daily(today)

        # 每日筹码及胜率表, 只采集今天的数据
        collect_and_save_cyq_perf(today)

        # 股票技术面因子表(专业版), 只采集今天的数据
        collect_and_save_stk_factor_pro(today)


if __name__ == "__main__":
    print("=" * 50)
    print("定时任务 - 本地测试")
    print("=" * 50)
    quotes_flow()
    print("\n测试完成!")

