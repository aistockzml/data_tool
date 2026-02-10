from pprint import pprint
import pandas as pd

from storage import MySqlOperator
from collector import TushareConnector, TushareDataCollector
from config import ConfigParser
from logger import LoggerManager

config = ConfigParser('config/base_config.yaml')

logger_mge = LoggerManager()
logger_mge.configure(**config.get_section('logger'))
logger = logger_mge.get_logger("collect")


mysql = MySqlOperator(**config.get_section('database'))

token = config.get_section('data_sources.tushare.token')
ts_connector = TushareConnector(token=token)
pro_api = ts_connector.get_connection()

ts_collector = TushareDataCollector(
    connector=pro_api,
    collect_name='tushare-数据采集',
    description='股票日线数据采集',
    db_conn=mysql,
    logger=logger)

data = ts_collector.collect(method='cashflow_vip', ann_date='20260109', fields='*')

# data.loc[(data['TS_CODE'] == '920050.BJ') & (data['END_DATE'] == '20250630'), 'UPDATE_FLAG'] = '2222'

ts_collector.save(
    data, 
    target_table='aistockzml_tushare_cashflow', 
    insert_mode='incremental',
    conflict_columns=['TS_CODE', 'END_DATE'],
)
