# -*- coding: utf-8 -*-
import os
import logging
import tushare as ts
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DOC_ID_MAP = {
    '25': '股票列表-基础信息',
    '26': '交易日历',
    '36': '资产负债表',
    '398': '沪深港通股票列表',
    '112': '上市公司基本信息',
    '33': '利润表',
    '44': '现金流量表',
    '45': '业绩预告',
    '46': '业绩快报',
    '103': '分红送股',
    '79': '财务指标数据',
    '81': '主营业务构成',
    '162': '财报披露日期表',
    '27': '日线行情-未复权行情',
    '144': '周线行情-历史-未复权行情',
    '145': '月线行情-历史-未复权行情',
    '336_w': '周线行情-每日更新-未复权行情',
    '336_m': '月线行情-每日更新-未复权行情',
    '365_w': '周线行情-每日更新-复权行情',
    '365_m': '月线行情-每日更新-复权行情',
    '32': '股票每日基本面指标',
    '196': '港股通每日成交统计',
    '197': '港股通每月成交统计',
    '110': '股权质押统计数据',
    '111': '股权质押明细',
    '124': '股票回购',
    '160': '限售股解禁',
    '161': '大宗交易',
    '166': '股东人数',
    '175': '股东增减持',
}

PRO_API_URL = 'http://lianghua.9vvn.com'

TOKEN = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'

API_NAME_MAP = {
    '25': 'stock_basic',
    '26': 'trade_cal',
    '36': 'balancesheet',
    '398': 'stock_hsgt',
    '112': 'stock_company',
    '33': 'income',
    '44': 'cashflow',
    '45': 'forecast',
    '46': 'express',
    '103': 'dividend',
    '79': 'fina_indicator',
    '81': 'fina_mainbz',
    '162': 'disclosure_date',
    '27': 'daily',
    '144': 'weekly',
    '145': 'monthly',
    '336_w': 'weekly',
    '336_m': 'monthly',
    '365_w': 'weekly',
    '365_m': 'monthly',
    '32': 'daily_basic',
    '196': 'ggt_daily',
    '197': 'ggt_monthly',
    '110': 'pledge_stat',
    '111': 'pledge_detail',
    '124': 'repurchase',
    '160': 'share_float',
    '161': 'block_trade',
    '166': 'stk_holdernumber',
    '175': 'stk_holdertrade',
}

API_PARAMS = {
    'balancesheet': {'ts_code': '000001.SZ', 'report_type': '1'},
    'income': {'ts_code': '000001.SZ', 'report_type': '1'},
    'cashflow': {'ts_code': '000001.SZ', 'report_type': '1'},
    'forecast': {'ts_code': '000001.SZ'},
    'dividend': {'ts_code': '000001.SZ'},
    'fina_indicator': {'ts_code': '000001.SZ'},
    'fina_mainbz': {'ts_code': '000001.SZ'},
    'fina_audit': {'ts_code': '000001.SZ'},
    'weekly': {'ts_code': '000001.SZ'},
    'monthly': {'ts_code': '000001.SZ'},
    'pledge_detail': {'ts_code': '000723.SZ'},
    'repurchase': {'ann_date': '20260101'},
    'shareholder': {'ts_code': '000001.SZ'},
    'shareholder_trade': {'ts_code': '000001.SZ'},
}

PY_TYPE_TO_MYSQL = {
    'int64': 'bigint(20)',
    'int32': 'int(11)',
    'float64': 'decimal(20,4)',
    'float32': 'decimal(20,4)',
    'str': 'varchar(255)',
    'object': 'text',
    'bool': 'tinyint(1)',
    'datetime64[ns]': 'datetime',
    'datetime': 'datetime',
    'date': 'date',
    'timestamp': 'timestamp',
}

FIELD_DESCRIPTIONS = {
    'ts_code': '股票代码',
    'trade_date': '交易日期',
    'open': '开盘价',
    'high': '最高价',
    'low': '最低价',
    'close': '收盘价',
    'pre_close': '昨收价',
    'change': '涨跌额',
    'pct_chg': '涨跌幅',
    'vol': '成交量(手)',
    'amount': '成交额(千元)',
    'adj_factor': '复权因子',
    'open_interest': '持仓量',
    'settlement': '结算价',
    'pre_settlement': '昨结算',
    'margin': '持仓量',
    'etl_time': '数据采集时间',
}


def get_mysql_type(python_type: str, field_name: str) -> str:
    if python_type in PY_TYPE_TO_MYSQL:
        return PY_TYPE_TO_MYSQL[python_type]
    
    if 'int' in python_type.lower():
        return 'bigint(20)'
    if 'float' in python_type.lower():
        return 'decimal(20,4)'
    if 'str' in python_type or 'object' in python_type:
        if 'code' in field_name.lower() or 'ts_code' in field_name.lower():
            return 'varchar(20)'
        if 'date' in field_name.lower() or field_name.endswith('_at'):
            return 'varchar(50)'
        return 'varchar(255)'
    if 'date' in python_type.lower() or 'time' in python_type.lower():
        return 'datetime'
    
    return 'text'


def get_field_description(field_name: str, doc_url: str) -> str:
    if field_name in FIELD_DESCRIPTIONS:
        return FIELD_DESCRIPTIONS[field_name]
    
    if field_name.endswith('_date'):
        return field_name.replace('_date', '').replace('_', ' ') + '日期'
    if field_name.endswith('_at'):
        return field_name.replace('_at', '').replace('_', ' ') + '时间'
    if 'code' in field_name.lower():
        return field_name.replace('_', ' ').title() + '代码'
    if 'name' in field_name.lower():
        return field_name.replace('_', ' ').title() + '名称'
    if 'amt' in field_name.lower() or 'amount' in field_name.lower():
        return field_name.replace('_', ' ').title() + '(金额)'
    if 'num' in field_name.lower() or 'count' in field_name.lower():
        return field_name.replace('_', ' ').title() + '(数量)'
    if 'rate' in field_name.lower() or 'pct' in field_name.lower():
        return field_name.replace('_', ' ').title() + '(比率)'
    
    return field_name.replace('_', ' ').title()


def get_api_fields(pro, api_name: str, params: Dict = None) -> Tuple[List[str], Dict[str, str]]:
    try:
        query_params = params or {}
        data = pro.query(api_name, fields='*', limit=1, **query_params)
        columns = data.columns.tolist()
        dtype_map = {}
        for col in columns:
            dtype_map[col] = str(data[col].dtype)
        return columns, dtype_map
    except Exception as e:
        logger.error(f"获取接口 {api_name} 字段失败: {e}")
        return [], {}


def generate_create_table_sql(table_name: str, table_desc: str,
                               columns: List[str], dtype_map: Dict[str, str],
                               doc_url: str) -> str:
    sql_lines = []
    sql_lines.append(f"-- {table_desc}")
    sql_lines.append(f"CREATE TABLE IF NOT EXISTS aistockzml_tushare_{table_name} (")
    
    field_lines = []
    for col in columns:
        mysql_type = get_mysql_type(dtype_map.get(col, 'str'), col)
        desc = get_field_description(col, doc_url)
        field_lines.append(f"    `{col}` {mysql_type} COMMENT '{desc}'")
    
    field_lines.append("    `etl_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间'")
    
    sql_lines.append(',\n'.join(field_lines))
    sql_lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='" + table_desc + "';")
    sql_lines.append("")
    
    return '\n'.join(sql_lines)


def main():
    logger.info("开始生成 Tushare 建表语句...")
    
    pro = ts.pro_api(TOKEN)
    pro._DataApi__token = TOKEN
    pro._DataApi__http_url = PRO_API_URL
    
    sql_dir = os.path.join(os.path.dirname(__file__), 'sql')
    os.makedirs(sql_dir, exist_ok=True)
    sql_file = os.path.join(sql_dir, 'init_tushare_table.sql')
    
    all_sql = []
    
    for doc_id, api_name in API_NAME_MAP.items():
        table_name = api_name
        table_desc = DOC_ID_MAP.get(doc_id, api_name)
        
        if doc_id in ['336_w', '336_m', '365_w', '365_m']:
            table_name = f"{api_name}_{doc_id.split('_')[0]}"
        
        logger.info(f"处理文档ID {doc_id}: {table_desc}, 接口名: {api_name}")
        
        doc_url = f"https://tushare.pro/document/2?doc_id={doc_id.split('_')[0]}"
        
        params = API_PARAMS.get(api_name, {})
        
        try:
            columns, dtype_map = get_api_fields(pro, api_name, params)
            
            if columns:
                sql = generate_create_table_sql(table_name, table_desc, columns, dtype_map, doc_url)
                all_sql.append(sql)
                logger.info(f"  成功获取 {len(columns)} 个字段")
            else:
                logger.warning(f"  无法获取接口 {api_name} 的字段信息")
                all_sql.append(f"-- {table_desc} (接口: {api_name}) - 获取字段失败\n")
        except Exception as e:
            logger.error(f"  处理接口 {api_name} 时出错: {e}")
            all_sql.append(f"-- {table_desc} (接口: {api_name}) - 处理出错: {e}\n")
    
    final_sql = []
    for i, sql in enumerate(all_sql):
        final_sql.append(sql)
        if i < len(all_sql) - 1:
            final_sql.append("")
            final_sql.append("")
    
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_sql))
    
    logger.info(f"建表语句已写入: {sql_file}")


if __name__ == '__main__':
    main()
