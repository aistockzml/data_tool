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

data = ts_collector.collect(method='fina_indicator_vip', period='20250630', fields='*')

if data is not None and not data.empty:
    print(f"原始数据: {len(data)} 条")

    data['UPDATE_TIME'] = pd.to_datetime(data['UPDATE_TIME'], errors='coerce')

    data_unique = (
        data
        .sort_values('UPDATE_TIME', ascending=False)
        .drop_duplicates(subset=['TS_CODE'], keep='first')
    )

    data_unique = data_unique.reset_index(drop=True)
    print(f"去重后数据: {len(data_unique)} 条")

    ts_collector.save(
        data_unique, 
        target_table='aistockzml_tushare_fina_indicator', 
        insert_mode='overwrite'
    )
