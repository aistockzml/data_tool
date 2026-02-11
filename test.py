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

# data_unique = [{"TS_CODE": "001281.SZ", "col1": "2", "col2": "a"}]
# mysql.batch_upsert('test_inst', data_unique, conflict_columns=['TS_CODE', 'col1'])


mysql.query('desc aistockzml_tushare_stk_monthly_adj')