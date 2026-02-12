# -*- coding: utf-8 -*-
"""
获取 moneyflow_dc 接口字段
"""

import tushare as ts

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.9vvn.com'

api_name = 'moneyflow_dc'
kwargs = {'trade_date': '20260109'}

data = pro.query(api_name, fields='*', limit=5, **kwargs)
columns = data.columns.tolist()

print(f"接口名称: {api_name}")
print(f"字段数量: {len(columns)}")
print(f"\n字段列表:")
for i, col in enumerate(columns, 1):
    print(f"{i:2d}. {col}")

print(f"\n数据样例:")
print(data.head(3))
