from pprint import pprint

from storage import MySqlOperator
from collector import TushareConnector, TushareDataCollector
from config import ConfigParser

config = ConfigParser(r'E:\2-项目代码\aistockzml\data_tools\config\base_config.yaml')

mysql = MySqlOperator(**config.get_section('database'))

token = config.get_section('data_sources.tushare.token')
ts_connector = TushareConnector(token=token)
pro_api = ts_connector.get_connection()

ts_collector = TushareDataCollector(
    connector=pro_api,
    collect_name='stock_daily',
    description='股票日线数据采集',
    db_conn=mysql
)

print(ts_collector.collect(method='income', ts_code='000001.SZ', fields='ts_code,ts_date,revenue,profit,net_profit'))
