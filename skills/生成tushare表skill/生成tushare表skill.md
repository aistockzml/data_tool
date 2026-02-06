---
name: 创建tushare表的mysql建表语句
description: 提供tushare官方数据接口文档的URL中的文档id，按照接口示例方法查询数据后，根据查询结果中的字段名生成mysql建表语句
---

# 概要
提供tushare官方数据接口文档的文档id列表，依次生成完整的官方数据接口文档URL，按照文档接口示例方法查询数据后，根据查询结果中的字段名生成mysql建表语句

# 准备
### 文档id列表
以下是tushare官方数据接口文档的文档id列表，每个文档id对应一个数据接口，例如‘25’对应’股票列表-基础信息‘，完整的URL为https://tushare.pro/document/2?doc_id=25
- 股票列表-基础信息：25
- 交易日历：26
- 沪深港通股票列表：398
- 上市公司基本信息：112
- 利润表：33
- 现金流量表：44
- 业绩预告：45
- 业绩快报：46
- 分红送股：103
- 财务指标数据：79
- 主营业务构成：81
- 财报披露日期表：162
- 日线行情(日k-历史)-未复权行情：27
- 周线行情(周k-历史)-未复权行情：144
- 月线行情(月k-历史)-未复权行情：145
- 周线行情(周k-每日更新)-未复权行情：336
- 月线行情(月k-每日更新)-未复权行情：336
- 周线行情(周k-每日更新)-复权行情：365
- 月线行情(月k-每日更新)-复权行情：365
- 股票每日重要的基本面指标：32
- 港股通每日成交统计：196
- 港股通每月成交统计：197
- 股权质押统计数据：110
- 股权质押明细：111
- 股票回购：124
- 限售股解禁：160
- 大宗交易：161
- 股东人数：166
- 股东增减持：175

### 连接tushare
首先以下python代码连接tushare
```
import tushare as ts

token = 'c26e3f2b758e67f46d3af7cb8273f20c178dc2919ee46318e837fc536f98'
pro = ts.pro_api(token)
pro._DataApi__token = token 
pro._DataApi__http_url = 'http://lianghua.9vvn.com'
```


# 工作流
提供的文档id列表，对列表中的每个文档id，按照以下工作流生成mysql建表语句。
### step1: 获取接口的接口名称和输入参数
1. 根据文档id，生成完整的官方数据接口文档URL，例如https://tushare.pro/document/2?doc_id=25
2. 打开URL，浏览Tushare官方数据接口文档，获得tushare库的接口名称，例如‘股票列表-基础信息’对应的接口名称为‘stock_basic’
3. 从“输入参数”下获取输入参数的参数名、参数类型、必选、默认值、描述等信息，例如‘ts_code’为股票代码，‘start_date’为开始日期，‘end_date’为结束日期等

### step2: 获取接口的输出参数的字段名
使用以下python代码获取接口的输出参数的字段名
```
api_name = '接口名称'

# api_name 为接口名称，例如‘stock_basic’，需要从step1中获取
# limit=1 仅查询一条数据，获取字段名
# fields='*' 表示查询所有字段
# kwargs为接口的参数，例如‘ts_code=000001.SZ’，需要参考Tushare官方文档中的“输入参数”下的内容
data = pro.query(api_name, fields='*', limit=1, **kwargs)
# 从查询结果中获取字段名，例如['ts_code','trade_date','close']
columns = data.columns.tolist()
```
需要注意：
1. 接口参数中，必选参数需要在python代码中添加，例如‘ts_code=000001.SZ’，需要添加到kwargs中



### step3: 生成mysql建表语句
根据接口名称和输出参数的字段名，生成mysql建表语句，例如接口名称为‘stock_basic’，输出参数的字段名包括['ts_code','trade_date','close']，则生成的mysql建表语句。
按照以下规范：
1. 表名中包含接口名称，表名样式`aistockzml_tushare_接口名称`，例如‘stock_basic’对应表名`aistockzml_tushare_stock_basic`
2. 表字段名与输出参数的字段名相同
3. 表字段的类型需要根据输出参数的字段类型和含义，选择合适的mysql字段类型和长度，例如‘ts_code’为varchar(20)，‘trade_date’为date，‘close’为decimal(10,2)等
4. 表字段的描述需要根据输出参数的字段描述和含义，选择合适的描述，例如‘ts_code’为股票代码，‘trade_date’为交易日期，‘close’为收盘价等
5. 每个表需要添加描述，描述内容为接口名称，例如`股票列表-基础信息`
6. 除了输出参数的字段外，需要额外增加数据采集时间字段`create_time`，类型为datetime，描述为数据采集时间
7. 除了输出参数的字段外，需要额外增加数据更新时间字段`update_time`，类型为datetime，描述为数据更新时间

### step4: 建表语句写入sql文件
生成的mysql建表语句写入sql文件`E:\2-项目代码\data_tool\sql\init_tushare_table.sql`

文件内按照以下格式写入：
1. 每个接口的建表语句之间用空行隔开，间隔2行
2. 每个接口的建表语句开头添加注释，注释内容为接口名称，例如‘股票列表-基础信息’对应的建表语句开头添加注释`-- 股票列表-基础信息`

# 其他要求
1. 按照以上步骤执行过程中，若遇到任何问题，需要及时记录到'init_tushare_table.log'文件中