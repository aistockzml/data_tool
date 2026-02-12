# -*- coding: utf-8 -*-
"""
检查 moneyflow_ind_ths 接口字段与SQL字段对比
"""

import tushare as ts

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.9vvn.com'

api_name = 'moneyflow_ind_ths'
kwargs = {'trade_date': '20260109'}

data = pro.query(api_name, fields='*', limit=5, **kwargs)
api_fields = set([col.upper() for col in data.columns.tolist()])

print(f"接口返回字段数: {len(api_fields)}")
print(f"\n接口字段列表:")
for i, col in enumerate(sorted(api_fields), 1):
    print(f"{i:2d}. {col}")

# 读取SQL文件中的字段
import re
with open('sql/init_tushare_table_moneyflow_ind_ths.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

sql_fields = set(re.findall(r'`([A-Z_]+)`', sql_content))
sql_fields.discard('ETL_TIME')  # 排除etl_time

print(f"\nSQL文件字段数: {len(sql_fields)}")
print(f"\nSQL字段列表:")
for i, col in enumerate(sorted(sql_fields), 1):
    print(f"{i:2d}. {col}")

# 对比
missing = api_fields - sql_fields
extra = sql_fields - api_fields

print(f"\n对比结果:")
print(f"缺失字段: {missing if missing else '无'}")
print(f"多余字段: {extra if extra else '无'}")
