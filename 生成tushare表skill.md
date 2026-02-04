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
