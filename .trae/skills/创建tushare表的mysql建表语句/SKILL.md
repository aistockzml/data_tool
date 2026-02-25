---
name: 创建Tushare表的MySQL建表语句
description: 解析Tushare接口返回字段，自动生成带中文注释的MySQL建表语句
---

# 概要

使用本Skill自动生成Tushare接口输出参数的带中文注释的MySQL建表语句。根据用户提供的接口文档URL，调用文档中的接口获取返回字段，自动映射为MySQL表结构，严格按照工作流要求执行。

# 准备

## Tushare连接配置

```python
import tushare as ts

token = '85de70a887b846af557d7d89c8532be1b9120eb279c949a3689ac20135b1'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'
```

## 常用Tushare接口列表

| 接口名称 | doc_id | 说明 |
|---------|--------|------|
| stock_basic | 25 | 股票列表-基础信息 |
| trade_cal | 26 | 交易日历 |
| daily | 27 | 日线行情 |
| income | 33 | 利润表 |
| balance_sheet | 36 | 资产负债表 |
| cashflow | 44 | 现金流量表 |

# 要求

## 字段处理规则

- MYSQL建表的列名全部来源于调用接口返回的字段名，不要使用接口文档中的「输出参数-名称」中的字段名，因为接口文档中的字段名可能与返回数据中的字段名不同
- 字段名直接作为MySQL表的列名
- 字段的中文注释从接口文档的「输出参数-描述」中获取
- 额外添加`etl_time`字段记录数据加载时间，类型为`datetime`
- **MySQL保留关键字处理**：如果字段名是MySQL保留关键字（如RANK、ORDER、GROUP、KEY、VALUE等），必须用反引号包裹，例如：`` `RANK` ``

## 表命名规范

- 表名格式：`aistockzml_tushare_{接口名称}`
- 示例：`stock_basic`接口对应表名`aistockzml_tushare_stock_basic`

## 类型映射规则

| Tushare类型 | MySQL类型 | 示例 |
|------------|----------|------|
| string | text | ts_code -> text |
| int | int | PB -> int |
| float/decimal | decimal(10,2) | close -> decimal(20,4) |
| date | date | end_date -> date |
| datetime | datetime | update_time -> datetime |

## 异常处理

- 由于接口可能出现网络问题，导致返回数据为空或返回失败，需要在代码中添加异常处理逻辑，然后再次调用接口，直至成功返回数据。


# 工作流

当用户需要生成Tushare接口的MySQL建表语句时，请严格按以下步骤执行：

### step1: 获取接口信息

1. 从用户提供的接口文档URL中提取接口名称、输入参数、输出参数、字段描述等信息
2. 确认该接口所需的输入参数及参数类型
3. 必选参数需要提供示例值用于测试调用，可在用户输入中获取，或接口文档中[接口用法]查看示例值。

### step2: 调用接口获取数据样本


1.先按装tushare第三方库，需要先安装tushare库
```
pip install tushare
```

2.执行以下python代码调用接口获取数据样本，字段名列表存在`columns`变量中。
```python
import tushare as ts

token = '85de70a887b846af557d7d89c8532be1b9120eb279c949a3689ac20135b1'
pro = ts.pro_api(token)
pro._DataApi__token = token
pro._DataApi__http_url = 'http://lianghua.nanyangqiankun.top'

api_name = '接口名称'
# 根据接口要求传入必选参数，或用户提供输入的参数值
kwargs = {}

# 获取1条样本数据用于解析字段结构
data = pro.query(api_name, fields='*', limit=1, **kwargs)
columns = data.columns.tolist()  # 获取字段名列表
```

### step3: 解析字段信息

1. 遍历`columns`字段名列表，获取每个字段名称
2. 确定每个字段的数据类型
3. 记录字段的业务含义（用于生成中文注释）

### step4: 生成MySQL建表语句

表的列名称只包含接口实际返回的字段。
建表语句示例：
```sql
-- 接口名称：stock_basic
-- 股票列表-基础信息
CREATE TABLE IF NOT EXISTS aistockzml_tushare_stock_basic (
    ts_code VARCHAR(20) COMMENT '股票代码',
    trade_date INT COMMENT '交易日期',
    open DECIMAL(10,2) COMMENT '开盘价',
    high DECIMAL(10,2) COMMENT '最高价',
    low DECIMAL(10,2) COMMENT '最低价',
    close DECIMAL(10,2) COMMENT '收盘价',
    pre_close DECIMAL(10,2) COMMENT '前收盘价',
    change DECIMAL(10,2) COMMENT '涨跌幅',
    pct_chg DECIMAL(10,2) COMMENT '涨跌额',
    vol BIGINT COMMENT '成交量',
    amount DECIMAL(20,2) COMMENT '成交额',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ts_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票列表-基础信息';
```

### step5: 写入SQL文件

1. 文件名格式：`init_tushare_table_{接口名称}.sql`
2. 保存路径：当前工程目录下的`sql`文件夹
3. 每个接口的建表语句独立一个文件

# 输出

- SQL文件保存在`{工程目录}/sql/init_tushare_table_{接口名称}.sql`
- 文件内容包含完整的MySQL建表语句，包括表名、字段定义、字段注释、表注释