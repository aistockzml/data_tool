---
name: "tushare数据唯一性分析"
description: "分析Tushare接口数据的唯一键,帮助确定MySQL建表主键。当用户需要分析新接口数据的唯一性或确定建表主键时调用。"
---

# Tushare 数据唯一性分析

## 功能说明

此技能用于分析 Tushare 接口返回数据的唯一性，帮助确定 MySQL 建表时的主键设计。

## 使用场景

当用户需要：
- 分析新的 Tushare 接口数据结构
- 确定数据库表的主键
- 了解数据是否存在重复记录
- 设计合理的唯一索引

## 分析步骤

### 1. 获取数据样本

使用 Tushare API 获取至少两个不同参数的数据样本：

```python
import sys
sys.path.insert(0, '.')
from schedule import pro_api
import pandas as pd

# 示例：获取两个不同季度的数据
params1 = {'period': '20250630', 'fields': '*'}
data1 = pro_api.income_vip(**params1)

params2 = {'period': '20250331', 'fields': '*'}
data2 = pro_api.income_vip(**params2)

combined = pd.concat([data1, data2])
```

### 2. 分析候选字段

检查可能的唯一键字段：

```python
# 查看字段列表
print('列名:', list(data1.columns))

# 检查各字段唯一值数量
print('TS_CODE 唯一值数量:', data1['TS_CODE'].nunique())
print('END_DATE 唯一值数量:', data1['END_DATE'].nunique())
print('ID 唯一值数量:', data1['ID'].nunique())
```

### 3. 检查组合唯一性

验证各种字段组合是否能唯一标识记录：

```python
# 检查各种组合是否唯一
print('(TS_CODE, END_DATE) 是否唯一:', not combined.duplicated(subset=['TS_CODE', 'END_DATE']).any())
print('(TS_CODE, END_DATE, REPORT_TYPE) 是否唯一:', not combined.duplicated(subset=['TS_CODE', 'END_DATE', 'REPORT_TYPE']).any())
print('(ID) 是否唯一:', not combined.duplicated(subset=['ID']).any())
```

### 4. 分析重复数据

如果存在重复，分析重复原因：

```python
# 找出重复数据
dup = combined[combined.duplicated(subset=['TS_CODE', 'END_DATE'], keep=False)]
print(f'重复数量: {len(dup)}')

# 查看重复数据示例
if not dup.empty:
    sample_ts = dup['TS_CODE'].iloc[0]
    sample_data = combined[combined['TS_CODE'] == sample_ts][['TS_CODE', 'END_DATE', 'REPORT_TYPE', 'ANN_DATE', 'UPDATE_TIME', 'ID']]
    print(sample_data.to_string())
```

## 输出结论

分析完成后，给出以下结论：

1. **唯一主键** - 哪个字段或字段组合可以唯一标识记录
2. **重复原因** - 如果存在重复，解释原因（如数据更新、修正等）
3. **建表建议** - 推荐的主键和唯一索引设计

## 建表建议模板

### 方案1：保留所有历史版本

```sql
CREATE TABLE table_name (
    ID BIGINT PRIMARY KEY COMMENT '主键ID',
    TS_CODE VARCHAR(20) NOT NULL COMMENT '股票代码',
    END_DATE VARCHAR(10) NOT NULL COMMENT '报告期',
    -- 其他字段...
    UPDATE_TIME DATETIME COMMENT '更新时间',
    UNIQUE INDEX uk_ts_code_end_date (TS_CODE, END_DATE)
) COMMENT '表注释';
```

### 方案2：只保留最新版本

```sql
CREATE TABLE table_name (
    ID BIGINT PRIMARY KEY COMMENT '主键ID',
    TS_CODE VARCHAR(20) NOT NULL COMMENT '股票代码',
    END_DATE VARCHAR(10) NOT NULL COMMENT '报告期',
    -- 其他字段...
    UPDATE_TIME DATETIME COMMENT '更新时间',
    UNIQUE INDEX uk_ts_code_end_date (TS_CODE, END_DATE)
) COMMENT '表注释';
```

配合代码中的去重逻辑：按 `UPDATE_TIME` 取最新记录。

## 注意事项

1. **数据量** - 确保获取足够的数据样本进行分析
2. **多参数** - 使用不同参数获取数据，验证唯一性是否稳定
3. **业务理解** - 结合业务场景理解数据更新机制
4. **性能考虑** - 主键设计要考虑查询性能和存储效率
