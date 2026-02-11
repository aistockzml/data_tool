import tushare as ts

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.9vvn.com'

api_name = 'suspend_d'
# 根据接口要求传入必选参数
kwargs = {
    'suspend_type': 'S',
    'trade_date': '20200312'
}

# 获取样本数据用于解析字段结构
data = pro.query(api_name, fields='*', limit=1, **kwargs)
columns = data.columns.tolist()  # 获取字段名列表

print("=== 字段名列表 ===")
print(columns)

print("\n=== 数据类型 ===")
print(data.dtypes)

print("\n=== 样本数据 ===")
print(data)
