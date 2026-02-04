from pprint import pprint

from storage import MySqlOperator
from collector import TushareConnector, TushareDataCollector
from config import ConfigParser
from logger import LoggerManager

config = ConfigParser(r'E:\2-项目代码\aistockzml\data_tools\config\base_config.yaml')

logger_mge = LoggerManager()
logger_mge.configure(**config.get_section('logger'))
collect_logger = logger_mge.get_logger("collect")

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

data = ts_collector.collect(method='stock_company', limit=1, fields=[
    "ts_code",
    "com_name",
    "com_id",
    "chairman",
    "manager",
    "secretary",
    "reg_capital",
    "setup_date",
    "province",
    "city",
    "introduction",
    "website",
    "email",
    "office",
    "business_scope",
    "employees",
    "main_business",
    "exchange",
    "ann_date"
])

ts_collector.save(data, target_table='aistockzml_tushare_stock_company_base_info')



