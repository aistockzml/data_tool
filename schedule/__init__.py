import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .utils import get_quarter_end_dates, get_date_range_list

from logger import LoggerManager
from config import ConfigParser
from collector import TushareConnector, TushareDataCollector
from storage import MySqlOperator


config = ConfigParser('config/base_config.yaml')
logger_mge = LoggerManager()
logger_mge.configure(**config.get_section('logger'))
logger = logger_mge.get_logger("tushare-collect")
mysql = MySqlOperator(**config.get_section('database'))
ts_connector = TushareConnector(token=config.get_section('data_sources.tushare.token'))
pro_api = ts_connector.get_connection()
ts_collector = TushareDataCollector(
    connector=pro_api,
    collect_name='tushare-数据采集',
    description='采集tushare的接口数据',
    db_conn=mysql,
    logger=logger)
