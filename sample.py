import tushare as ts
import pandas as pd

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token 
pro._DataApi__http_url = 'http://lianghua.9vvn.com'

params = {
        'trade_date': '20260213',
        'fields': '*'
    }

df = pro.moneyflow_ind_dc(**params)