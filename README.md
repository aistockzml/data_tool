# data_tools - 金融数据采集框架

开发一个通用的金融数据采集Python框架，框架名称为`data_tools`，可集成tushare、akshare等主流数据接口，实现统一的数据采集与管理。

## 框架特性

- **模块化设计**：采用基类+子类的继承模式，五大核心模块职责清晰
- **易扩展**：支持自定义数据源采集逻辑，便于后续接入新的数据源
- **高可靠性**：支持失败重试、增量采集、缓存机制
- **完善日志**：统一日志管理，支持任务追踪和错误记录
- **配置灵活**：支持YAML配置文件，易于管理和部署

## 核心模块

| 模块 | 说明 | 主要类 |
|------|------|--------|
| 配置模块 | 解析YAML配置文件 | ConfigParser |
| 日志模块 | 统一日志管理 | LoggerManager, DataLogger |
| 存储模块 | MySQL数据库操作 | MySqlOperator |
| 采集模块 | 数据采集框架 | DataCollector, TushareDataCollector, AkshareDataCollector |

## 快速开始

### 1. 安装依赖

```bash
pip install -r data_tools/requirements.txt

# 可选：安装数据源
pip install tushare akshare
```

### 2. 配置数据源

编辑 `data_tools/example/base_config.yaml`：

```yaml
database:
  host: localhost
  port: 3306
  user: root
  password: your_password
  database: stock_data

data_sources:
  tushare:
    token: your_tushare_token
  akshare: {}
```

### 3. 创建采集器

```python
# -*- coding: utf-8 -*-
import pandas as pd
from data_tools.config import ConfigParser
from data_tools.storage import MySqlOperator
from data_tools.collector import TushareDataCollector

class StockDailyCollector(TushareDataCollector):
    """股票日线数据采集器"""
    
    def __init__(self, connector, collect_config, db_operator):
        super().__init__(
            connector=connector,
            collect_name=collect_config.get('collect_name', 'stock_daily'),
            description=collect_config.get('description', ''),
            db_conn=db_operator,
            target_table=collect_config.get('target_table', 'stock_daily')
        )
    
    def save(self, data: pd.DataFrame) -> bool:
        """保存数据到数据库"""
        if data is None or data.empty:
            return False
        
        data_list = data.to_dict('records')
        affected = self.db_conn.batch_upsert(
            self.target_table,
            data_list,
            conflict_columns=['ts_code', 'trade_date']
        )
        return affected > 0

# 使用示例
config = ConfigParser('base_config.yaml')
db = MySqlOperator(**config.get_section('database'))

import tushare as ts
ts.set_token(config.get_config('data_sources.tushare.token'))
pro_api = ts.pro_api()

collector = StockDailyCollector(
    connector=pro_api,
    collect_config={'collect_name': 'stock_daily', 'target_table': 'stock_daily'},
    db_operator=db
)

# 执行采集
success, count, error = collector.run(
    ts_code='000001.SZ',
    start_date='20240101',
    end_date='20240131'
)
```

## API文档

### ConfigParser

配置解析器，负责解析YAML配置文件。

```python
from data_tools.config import ConfigParser

# 初始化
config = ConfigParser('config.yaml')

# 获取配置
host = config.get_config('database', 'host')
port = config.get_config('database', 'port')

# 获取整个配置节
db_config = config.get_section('database')

# 获取列表配置
collectors = config.get_list('collectors', '')

# 类型转换
port = config.get_int('database', 'port')
enabled = config.get_bool('collectors', 'enabled')

# 检查配置
has_host = config.has_option('database', 'host')
```

### LoggerManager

日志管理器，负责日志的统一管理。

```python
from data_tools.logger import LoggerManager

# 获取日志器
logger = LoggerManager().get_logger("module_name")

# 记录日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 采集任务日志
logger.log_collect_start("task_name")
logger.log_collect_end("task_name", True, 100)
logger.log_collect_error("task_name", "错误信息")

# 动态配置
LoggerManager().configure(level='DEBUG', output='both')
```

### MySqlOperator

MySQL数据库操作类。

```python
from data_tools.storage import MySqlOperator

# 初始化
db = MySqlOperator(
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='stock_data'
)

# 查询
results = db.query("SELECT * FROM table WHERE id = %s", (1,))

# 插入
inserted_id = db.insert('table', {'name': 'test', 'value': 100})

# 批量插入
affected = db.batch_insert('table', [
    {'name': 'item1', 'value': 100},
    {'name': 'item2', 'value': 200}
])

# 更新
affected = db.update('table', {'value': 200}, 'name = %s', ('item1',))

# 删除
affected = db.delete('table', 'name = %s', ('item1',))

# Upsert
affected = db.upsert('table', {'name': 'item1', 'value': 300}, ['name'])

# 批量Upsert
affected = db.batch_upsert('table', [
    {'name': 'item1', 'value': 300},
    {'name': 'item2', 'value': 400}
], ['name'])

# 上下文管理器
with MySqlOperator(**config) as db:
    db.execute("UPDATE table SET value = 100")
```

### DataCollector

数据采集器基类，定义数据采集的通用框架。

```python
from data_tools.collector import DataCollector

class MyCollector(DataCollector):
    
    def __init__(self, connector, collect_name, description=''):
        super().__init__(connector, collect_name, description)
    
    def collect(self, **kwargs) -> pd.DataFrame:
        """采集数据"""
        # 实现具体采集逻辑
        pass
    
    def save(self, data: pd.DataFrame) -> bool:
        """保存数据"""
        # 实现保存逻辑
        pass

# 使用
collector = MyCollector(connector, 'my_collector', '我的采集器')

# 执行采集流程
success, count, error = collector.run(**kwargs)

# 带重试采集
data = collector.collect_with_retry(**kwargs)

# 增量采集
data = collector.collect_incremental(last_date='2023-12-31', date_column='date')

# 获取状态
status = collector.get_status()
```

## 测试

运行所有测试：

```bash
python data_tools/test/run_tests.py
```

单独运行测试：

```bash
python data_tools/test/test_config.py
python data_tools/test/test_logger.py
python data_tools/test/test_storage.py
python data_tools/test/test_collector.py
```

## 项目结构

```
data_tools/
├── __init__.py              # 主模块入口
├── requirements.txt          # 依赖列表
├── config/
│   └── __init__.py          # 配置模块
├── logger/
│   ├── __init__.py          # 日志模块
│   └── data_logger.py       # 日志记录器
├── storage/
│   └── __init__.py          # 存储模块
├── collector/
│   ├── __init__.py          # 采集模块
│   ├── data_collector.py     # 数据采集器基类
│   ├── tushare_collector.py  # Tushare采集器
│   └── akshare_collector.py  # Akshare采集器
├── example/
│   ├── base_config.yaml      # 基础配置示例
│   └── stock_collector_example.py  # 使用示例
└── test/
    ├── run_tests.py          # 测试运行脚本
    ├── test_config.py        # 配置模块测试
    ├── test_logger.py        # 日志模块测试
    ├── test_storage.py       # 存储模块测试
    └── test_collector.py     # 采集模块测试
```

## 依赖列表

```
pymysql>=1.0.0      # MySQL数据库驱动
pyyaml>=6.0         # YAML配置文件解析
pandas>=1.5.0       # 数据处理
DBUtils>=3.0.0      # 数据库连接池

# 可选依赖
tushare>=1.2.0      # Tushare数据接口
akshare>=1.0.0      # Akshare数据接口
```

## 许可

MIT License
