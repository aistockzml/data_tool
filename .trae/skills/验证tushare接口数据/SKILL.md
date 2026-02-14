---
name: "验证tushare接口数据"
description: "验证股票代码在Tushare接口中是否有数据返回。当用户提供股票代码文件、接口名称和参数时调用此skill进行批量验证。"
---

# 验证Tushare接口数据

## 概要

本Skill用于批量验证股票代码在指定Tushare接口中是否有数据返回，帮助用户快速定位哪些股票在接口中存在数据，哪些不存在。

## 准备

### Tushare连接配置

```python
import tushare as ts

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.9vvn.com'
```

## 输入信息

用户提供以下信息：

| 项目 | 说明 | 示例 |
|-----|------|------|
| 股票代码文件 | 存放股票代码的txt文件路径 | `ts_code.txt` |
| 接口名称 | Tushare接口名称 | `disclosure_date` |
| 查询参数 | 接口查询参数（不含ts_code） | `{'end_date': '20250630'}` |

## 工作流

### Step 1: 确认输入信息

向用户确认以下信息：
1. 股票代码文件路径
2. 接口名称
3. 查询参数（JSON格式）

### Step 2: 生成验证脚本

根据用户提供的信息生成Python验证脚本：

```python
import tushare as ts
import pandas as pd

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.9vvn.com'

# 股票代码文件路径
ts_code_file = '{股票代码文件路径}'
# 接口名称
api_name = '{接口名称}'
# 查询参数
query_params = {查询参数}

with open(ts_code_file, 'r', encoding='utf-8') as f:
    ts_codes = [line.strip() for line in f if line.strip()]

print(f"共{len(ts_codes)}个股票代码需要验证\n")

has_data = []
no_data = []

for i, ts_code in enumerate(ts_codes, 1):
    params = {'ts_code': ts_code, **query_params, 'fields': '*'}
    try:
        df = pro.query(api_name, **params)
        if df is not None and len(df) > 0:
            has_data.append(ts_code)
            print(f"[{i}/{len(ts_codes)}] {ts_code}: 有数据 ({len(df)}条)")
        else:
            no_data.append(ts_code)
            print(f"[{i}/{len(ts_codes)}] {ts_code}: 无数据")
    except Exception as e:
        no_data.append(ts_code)
        print(f"[{i}/{len(ts_codes)}] {ts_code}: 查询失败 - {e}")

print("\n" + "="*50)
print(f"有数据的股票: {len(has_data)}个")
print(f"无数据的股票: {len(no_data)}个")

if no_data:
    print("\n无数据的股票代码列表:")
    for code in no_data:
        print(f"  {code}")
```

### Step 3: 执行验证脚本

运行生成的Python脚本，输出验证结果。

### Step 4: 清理临时文件

验证完成后删除临时生成的Python脚本文件。

## 输出

- 控制台输出验证结果统计
- 有数据的股票列表及数据条数
- 无数据的股票代码列表
