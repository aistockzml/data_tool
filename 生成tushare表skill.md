<<<<<<< HEAD
---
name: tushare-table
description: 生成tushare表
---

# 生成建MYSQL表语句
从Tushare官方文档中的“输出参数”下的内容，生成对应的mysql建表语句

## 拼接Tushare官方数据接口文档URL
### 文档id列表
Tushare官方数据接口文档URL形式为https://tushare.pro/document/2?doc_id={doc_id},其中{doc_id}为文档id，例如‘25’对应’股票列表-基础信息‘，形成完整的URL，为https://tushare.pro/document/2?doc_id=25

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



=======
# 表格
|  网址   | 表英文名称  | 表中文名  |
|  ----  | ----  | ---- |
| https://tushare.pro/document/2?doc_id=25  | aistockzml_tushare_stock_base_info | 股票基础信息 |
| https://tushare.pro/webclient/  | aistockzml_tushare_stock_company_base_info | 上市公司基本信息 |
| https://tushare.pro/document/2?doc_id=26  | aistockzml_tushare_trade_cal_base_info | 交易日历 |
表格注解：
- 网址：Tushare官方文档地址
- 表英文名称：数据库中的表名，用于建表时的表名
- 表中文名：数据库中的表的中文名称，用于建表时的表注释

# 概述
逐行根据上述的表格中的网址，从Tushare官方文档中的“输出参数”下的内容，生成对应的mysql建表语句

# 要求
1. 所有建表语句存放在同一个sql文件中，文件名为init_tushare_table.sql，建表语句之间间隔2行空行
2. 所有建表语句的表名都必须是小写
3. 建表语句开头需要注释，注释内容为表中文名
4. Tushare官方文档中的“输出参数”下的字段“类型”对应mysql的字段类型，并判断选择合适的字段类型，避免出现类型不匹配的情况，或者字段类型过小的情况
>>>>>>> cf7a5fa711d1326e63d083e1f9f24151ee8bf590
