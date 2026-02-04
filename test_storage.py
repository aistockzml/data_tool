from pprint import pprint

from storage import MySqlOperator
from collector import TushareConnector, TushareDataCollector
from config import ConfigParser
from logger import LoggerManager

config = ConfigParser(r'E:\2-项目代码\data_tool\config\base_config.yaml')

logger_mge = LoggerManager()
logger_mge.configure(**config.get_section('logger'))
collect_logger = logger_mge.get_logger("collect")
collect_logger.info('leishezhenhao')

mysql = MySqlOperator(**config.get_section('database'))

token = config.get_section('data_sources.tushare.token')
ts_connector = TushareConnector(token=token)
pro_api = ts_connector.get_connection()

ts_collector = TushareDataCollector(
    connector=pro_api,
    collect_name='tushare-数据采集',
    description='股票日线数据采集',
    db_conn=mysql,
    logger=collect_logger)

data = ts_collector.collect(method='income', ts_code='000002.SZ', fields='ts_code,ann_date,f_ann_date,end_date,report_type')





