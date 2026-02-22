# -*- coding: utf-8 -*-
"""
数据采集器

定义数据采集的通用框架，子类继承后实现具体数据源的采集逻辑。

功能特性：
- 统一的采集接口设计
- 支持数据校验和转换
- 支持失败重试机制
- 支持增量采集
- 支持超时控制
- 支持批量采集

使用示例：
    class StockDailyCollector(DataCollector):
        def __init__(self, connector, collect_name, description, db_conn=None):
            super().__init__(connector, collect_name, description, db_conn)
        
        def collect(self, **kwargs):
            # 实现具体采集逻辑
            pass
        
        def save(self, data, target_table=None):
            # 实现保存逻辑
            pass
    
    collector = StockDailyCollector(connector, 'stock_daily', '股票日线数据采集')
    df = collector.collect(ts_code='000001.SZ', start_date='20240101', end_date='20240131')
"""


import pandas as pd
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from . import DataConnector


class DataCollectorError(Exception):
    """数据采集异常"""
    pass


class DataCollector(ABC):
    """
    数据采集器基类
    
    定义数据采集的通用框架，子类继承后实现具体数据源的采集逻辑。
    
    Attributes:
        connector: 数据源连接对象
        collect_name: 数据采集器的唯一标识符
        description: 数据采集器的功能描述
        db_conn: 数据库连接对象
        logger: 日志记录器
        _retry_config: 重试配置
        _cache: 缓存字典
    """
    
    def __init__(self, connector: Any, collect_name: str, 
                 description: str = '', db_conn: Any = None,
                 logger: Any = None):
        """
        初始化数据采集器
        
        Args:
            connector: 数据源连接对象
            collect_name: 数据采集器的唯一标识符
            description: 数据采集器的功能描述
            db_conn: 数据库连接对象，可选
            logger: 日志记录器对象，可选
        """
        self.connector = connector
        self.collect_name = collect_name
        self.description = description
        self.db_conn = db_conn
        self.logger = logger
        
        self._retry_config = {
            'max_retries': 3,
            'retry_interval': 60,
            'backoff_factor': 2
        }
        self._cache: Dict[str, pd.DataFrame] = {}
    
    def set_retry_config(self, max_retries: int = 3, 
                         retry_interval: int = 60,
                         backoff_factor: float = 2) -> None:
        """
        设置重试配置
        
        Args:
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            backoff_factor: 退避因子
        """
        self._retry_config = {
            'max_retries': max_retries,
            'retry_interval': retry_interval,
            'backoff_factor': backoff_factor
        }
    
    def enable_cache(self, cache_dir: str = None, 
                     expire_seconds: int = 3600) -> None:
        """
        启用缓存机制
        
        Args:
            cache_dir: 缓存目录
            expire_seconds: 缓存过期时间
        """
        self._cache_dir = cache_dir
        self._cache_expire = expire_seconds
    
    def disable_cache(self) -> None:
        """禁用缓存机制"""
        self._cache.clear()
    
    @abstractmethod
    def collect(self, method: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        采集数据
        
        通过方法名动态调用connector的任意方法。
        
        Args:
            method: 方法名
            **kwargs: 方法参数
            
        Returns:
            Optional[DataFrame]: 采集到的数据
        """
        pass
    
    def save(self, data: pd.DataFrame, target_table: str = None, 
             conflict_columns: List[str] = None, insert_mode: str = 'incremental') -> bool:
        """
        保存数据到数据库
        
        Args:
            data: 采集到的数据
            target_table: 目标数据库表名
            conflict_columns: 冲突判断列名列表（用于upsert）
            insert_mode: 插入模式，可选值：
                - 'incremental': 增量插入（默认），追加新数据
                - 'overwrite': 覆盖存储，先清空表再插入
            
        Returns:
            bool: 保存是否成功
        """
        if data is None or data.empty:
            return False
        
        if self.db_conn is None or target_table is None:
            self.logger.warning("未配置数据库连接或目标表，跳过保存")
            return False
        
        if insert_mode not in ('incremental', 'overwrite'):
            self.logger.warning(f"不支持的插入模式: {insert_mode}，使用默认增量模式")
            insert_mode = 'incremental'
        
        try:
            data = data.assign(etl_time=datetime.now())
            data_list = data.to_dict('records')
            
            if self.db_conn.table_exists(target_table):
                if insert_mode == 'overwrite':
                    self.logger.info(f"覆盖模式：清空表 {target_table}")
                    self.db_conn.execute(f"TRUNCATE TABLE {target_table}")

                if conflict_columns:
                    affected = self.db_conn.batch_upsert(
                        target_table,
                        data_list,
                        conflict_columns
                    )
                    self.logger.info(f"upsert 受影响 {affected} 行")
                else:
                    affected = self.db_conn.batch_insert(
                        target_table,
                        data_list
                    )
            else:
                raise DataCollectorError(f"目标表 {target_table} 不存在，请先创建表")
            
            self.logger.info(f"保存 {affected} 条数据到{target_table}，模式: {insert_mode}")
            return affected > 0
            
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            return False

    def update(self, data: pd.DataFrame, target_table: str,
              where_columns: List[str]) -> int:
        """
        更新DataFrame数据到数据库（整行更新）

        Args:
            data: 更新数据DataFrame
            target_table: 目标数据库表名
            where_columns: WHERE条件列名列表，用于定位要更新的行

        Returns:
            int: 更新的行数
        """
        if data is None or data.empty:
            self.logger.warning("更新数据为空，跳过")
            return 0

        if self.db_conn is None:
            self.logger.warning("未配置数据库连接，跳过更新")
            return 0

        if not where_columns:
            self.logger.warning("未指定WHERE条件列，跳过更新")
            return 0

        try:
            data_list = data.to_dict('records')
            total_affected = 0

            for row in data_list:
                where_clause = ' AND '.join([f"`{col}` = %s" for col in where_columns])
                where_params = tuple(row[col] for col in where_columns)

                update_data = {k: v for k, v in row.items() if k not in where_columns}

                if update_data:
                    affected = self.db_conn.update(
                        target_table,
                        update_data,
                        where_clause,
                        where_params
                    )
                    total_affected += affected

            self.logger.info(f"更新表 {target_table}，更新行数: {total_affected}")
            return total_affected

        except Exception as e:
            self.logger.error(f"更新数据失败: {e}")
            return 0
    
    def _create_table_from_df(self, table_name: str, df: pd.DataFrame) -> None:
        """
        根据DataFrame创建表
        
        Args:
            table_name: 表名
            df: 数据
        """
        column_types = {
            'int64': 'BIGINT',
            'int32': 'INT',
            'float64': 'DECIMAL(20,4)',
            'float32': 'DECIMAL(20,4)',
            'object': 'TEXT',
            'datetime64[ns]': 'DATETIME',
            'bool': 'TINYINT(1)',
        }
        
        columns = {}
        for col, dtype in df.dtypes.items():
            sql_type = column_types.get(str(dtype), 'TEXT')
            columns[col] = sql_type
        
        self.db_conn.create_table(table_name, columns)
    
    def validate(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        对采集到的数据进行校验
        
        Args:
            data: 采集到的数据
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        if data is None or data.empty:
            return False, ["数据为空"]
        
        if 'date' in data.columns:
            invalid_dates = data[~pd.to_datetime(data['date'], errors='coerce').notna()]
            if not invalid_dates.empty:
                errors.append(f"存在{len(invalid_dates)}条无效日期数据")
        
        if 'ts_code' in data.columns:
            invalid_codes = data[~data['ts_code'].astype(str).str.match(r'^\d{6}\.(SZ|SH)$')]
            if not invalid_codes.empty:
                errors.append(f"存在{len(invalid_codes)}条无效股票代码")
        
        return len(errors) == 0, errors
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        对采集到的数据进行格式转换和预处理
        
        Args:
            data: 原始数据
            
        Returns:
            DataFrame: 转换后的数据
        """
        if data is None or data.empty:
            return data
        
        df = data.copy()
        
        date_columns = self.get_config('date_columns', [])
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        numeric_columns = self.get_config('numeric_columns', [])
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取采集器配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        return getattr(self, f'_{key}', default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        设置采集器配置
        
        Args:
            key: 配置键
            value: 配置值
        """
        setattr(self, f'_{key}', value)
    
    def run(self, **kwargs) -> Tuple[bool, int, str]:
        """
        执行完整采集流程
        
        Args:
            **kwargs: 采集参数
            
        Returns:
            Tuple[bool, int, str]: (是否成功, 记录数, 错误信息)
        """
        self.logger.log_collect_start(self.collect_name)
        start_time = time.time()
        
        try:
            data = self.collect(**kwargs)
            
            if data is None or data.empty:
                self.logger.log_collect_end(self.collect_name, False, 0)
                return False, 0, "未采集到数据"
            
            data = self.transform(data)
            
            is_valid, errors = self.validate(data)
            if not is_valid:
                error_msg = "; ".join(errors)
                self.logger.log_collect_error(self.collect_name, error_msg)
                self.logger.log_collect_end(self.collect_name, False, len(data))
                return False, len(data), error_msg
            
            success = self.save(data, kwargs.get('target_table'))
            
            elapsed = time.time() - start_time
            self.logger.info(f"采集完成，耗时: {elapsed:.2f}秒")
            self.logger.log_collect_end(self.collect_name, success, len(data))
            
            return success, len(data), ""
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log_collect_error(self.collect_name, error_msg)
            self.logger.log_collect_end(self.collect_name, False, 0)
            return False, 0, error_msg
    
    def collect_with_retry(self, **kwargs) -> Optional[pd.DataFrame]:
        """
        带重试的采集
        
        Args:
            **kwargs: 采集参数
            
        Returns:
            Optional[DataFrame]: 采集到的数据
        """
        max_retries = self._retry_config['max_retries']
        retry_interval = self._retry_config['retry_interval']
        backoff_factor = self._retry_config['backoff_factor']
        
        for attempt in range(max_retries):
            try:
                return self.collect(**kwargs)
            except Exception as e:
                self.logger.warning(f"采集尝试{attempt + 1}/{max_retries}失败: {e}")
                if attempt < max_retries - 1:
                    sleep_time = retry_interval * (backoff_factor ** attempt)
                    time.sleep(sleep_time)
        
        self.logger.error(f"采集重试{max_retries}次后放弃")
        return None
    
    def collect_incremental(self, last_date: str = None, 
                            date_column: str = 'date',
                            **kwargs) -> Optional[pd.DataFrame]:
        """
        增量采集
        
        Args:
            last_date: 上次采集的最后日期
            date_column: 日期列名
            **kwargs: 其他参数
            
        Returns:
            Optional[DataFrame]: 新增数据
        """
        cache_key = f"incremental_{last_date}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        data = self.collect(**kwargs)
        
        if data is None or data.empty:
            return None
        
        if last_date and date_column in data.columns:
            data = data[data[date_column] > last_date]
        
        if not data.empty:
            self._cache[cache_key] = data
        
        return data
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取采集器状态
        
        Returns:
            Dict: 状态信息
        """
        return {
            'collect_name': self.collect_name,
            'description': self.description,
            'connector': str(self.connector),
            'retry_config': self._retry_config
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.collect_name})>"
