from pprint import pprint

from storage import MySqlOperator
from collector import TushareConnector, TushareDataCollector
from config import ConfigParser
from logger import LoggerManager

# 配置解析
config = ConfigParser('config/base_config.yaml')

# 日志配置
logger_mge = LoggerManager()
logger_mge.configure(**config.get_section('logger'))
collect_logger = logger_mge.get_logger("collect")

# 数据库连接
mysql = MySqlOperator(**config.get_section('database'))

# Tushare 连接
token = config.get_section('data_sources.tushare.token')
ts_connector = TushareConnector(token=token)
pro_api = ts_connector.get_connection()

# Tushare 数据采集
ts_collector = TushareDataCollector(
    connector=pro_api,
    collect_name='tushare-数据采集',
    description='股票日线数据采集',
    db_conn=mysql,
    logger=collect_logger)

# 数据采集
data = ts_collector.collect(method='daily', trade_date='20260206', fields='*')

# 数据保存
ts_collector.save(data, target_table='aistockzml_tushare_daily', insert_mode='incremental')



