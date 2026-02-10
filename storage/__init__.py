# -*- coding: utf-8 -*-
"""
数据库操作类

MySQL 数据库操作类，提供数据库连接和操作方法。

功能特性：
- 支持数据库连接和操作
- 支持查询、插入、更新、删除操作
- 支持批量操作
- 支持连接池管理
- 支持事务操作
- 参数化查询防止SQL注入

使用示例：
    db = MySqlOperator(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        database='stock_data'
    )
    
    # 查询数据
    results = db.query("SELECT * FROM stock_daily WHERE ts_code = %s", ('000001.SZ',))
    
    # 插入数据
    db.insert('stock_daily', {
        'ts_code': '000001.SZ',
        'trade_date': '20240101',
        'open': 100.5,
        'close': 101.2
    })
    
    db.close()
"""


import pymysql
from pymysql.cursors import DictCursor
from typing import Any, Dict, List, Optional, Tuple
import threading
import math

try:
    from dbutils.pooled_db import PooledDB
    _DBUTILS_AVAILABLE = True
except ImportError:
    PooledDB = None
    _DBUTILS_AVAILABLE = False


class DatabaseOperationError(Exception):
    """数据库操作异常"""
    pass


class MySqlOperator:
    """
    MySQL 数据库操作类
    
    提供数据库连接和操作方法。
    
    Attributes:
        pool: 数据库连接池
        _lock: 线程锁
    """
    
    _pools: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    def __init__(self, host: str = 'localhost', port: int = 3306,
                 user: str = 'root', password: str = '',
                 database: str = '', charset: str = 'utf8mb4',
                 connect_timeout: int = 10, read_timeout: int = 10,
                 write_timeout: int = 10, pool_size: int = 10,
                 pool_recycle: int = None):
        """
        初始化MySQL操作类
        
        Args:
            host: 数据库主机地址，默认值为 'localhost'
            port: 数据库端口号，默认值为 3306
            user: 数据库用户名，默认值为 'root'
            password: 数据库密码，默认值为空字符串
            database: 数据库名，默认值为空字符串
            charset: 数据库字符集，默认值为 'utf8mb4'
            connect_timeout: 连接超时时间，默认值为 10 秒
            read_timeout: 读取超时时间，默认值为 10 秒
            write_timeout: 写入超时时间，默认值为 10 秒
            pool_size: 连接池大小，默认值为 10 个连接
            pool_recycle: 连接回收时间（秒），默认 None 表示不回收
        """
        if PooledDB is None:
            raise ImportError("请安装DBUtils: pip install DBUtils")
        
        self._config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': charset,
            'connect_timeout': connect_timeout,
            'read_timeout': read_timeout,
            'write_timeout': write_timeout
        }
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle
        self._pool = self._get_pool()
    
    def _get_pool(self) -> PooledDB:
        """
        获取数据库连接池
        
        Returns:
            PooledDB: 连接池实例
        """
        pool_key = f"{self._config['host']}:{self._config['port']}:{self._config['database']}"
        
        with self._lock:
            if pool_key not in self._pools:
                valid_params = {
                    'host', 'port', 'user', 'password', 'database', 'charset',
                    'connect_timeout', 'read_timeout', 'write_timeout'
                }
                pool_config = {k: v for k, v in self._config.items() if k in valid_params}
                
                self._pools[pool_key] = PooledDB(
                    creator=pymysql,
                    maxconnections=self._pool_size,
                    mincached=2,
                    maxcached=5,
                    blocking=True,
                    **pool_config
                )
            return self._pools[pool_key]
    
    def get_connection(self):
        """
        获取数据库连接，确保连接是健康的
        
        Returns:
            Connection: 数据库连接对象
        """
        conn = self._pool.connection()
        try:
            conn.ping(reconnect=True)
        except Exception:
            conn.close()
            conn = self._pool.connection()
            conn.ping(reconnect=True)
        return conn
    
    def query(self, sql: str, params: Tuple = None) -> List[Dict]:
        """
        执行查询，返回结果列表
        
        Args:
            sql: SQL查询语句
            params: 参数元组
            
        Returns:
            List[Dict]: 查询结果列表
            
        Raises:
            DatabaseOperationError: 查询失败
        """
        try:
            conn = self.get_connection()
            try:
                with conn.cursor(DictCursor) as cursor:
                    cursor.execute(sql, params)
                    result = cursor.fetchall()
                    return result
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"查询失败: {e}")
    
    def insert(self, table: str, data: Dict) -> int:
        """
        插入单条数据
        
        Args:
            table: 表名
            data: 数据字典
            
        Returns:
            int: 插入记录的ID
            
        Raises:
            DatabaseOperationError: 插入失败
        """
        if not data:
            raise DatabaseOperationError("插入数据不能为空")
        
        columns = ', '.join([f'`{col}`' for col in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql, tuple(data.values()))
                    conn.commit()
                    return cursor.lastrowid
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"插入失败: {e}")
    
    def batch_insert(self, table: str, data_list: List[Dict]) -> int:
        """
        批量插入数据
        
        Args:
            table: 表名
            data_list: 数据字典列表
            
        Returns:
            int: 影响行数
            
        Raises:
            DatabaseOperationError: 批量插入失败
        """
        if not data_list:
            return 0
        
        if len(data_list) == 1:
            return self.insert(table, data_list[0])
        
        columns = list(data_list[0].keys())
        column_names = ', '.join([f'`{col}`' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"

        def convert_nan_to_none(value):
            """将NaN值转换为None"""
            if value is None:
                return None
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return value

        values_list = [
            tuple(convert_nan_to_none(data[col]) for col in columns)
            for data in data_list
        ]
        
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.executemany(sql, values_list)
                conn.commit()
                return len(data_list)
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"批量插入失败: {e}")
    
    def update(self, table: str, data: Dict, 
               where: str, where_params: Tuple = None) -> int:
        """
        更新数据
        
        Args:
            table: 表名
            data: 更新数据字典
            where: WHERE条件语句
            where_params: WHERE条件参数
            
        Returns:
            int: 影响行数
            
        Raises:
            DatabaseOperationError: 更新失败
        """
        if not data:
            raise DatabaseOperationError("更新数据不能为空")
        
        set_clause = ', '.join([f"`{key}` = %s" for key in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    params = tuple(data.values())
                    if where_params:
                        params = params + where_params
                    affected = cursor.execute(sql, params)
                    conn.commit()
                    return affected
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"更新失败: {e}")
    
    def delete(self, table: str, where: str, 
               where_params: Tuple = None) -> int:
        """
        删除数据
        
        Args:
            table: 表名
            where: WHERE条件语句
            where_params: WHERE条件参数
            
        Returns:
            int: 影响行数
            
        Raises:
            DatabaseOperationError: 删除失败
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    affected = cursor.execute(sql, where_params)
                    conn.commit()
                    return affected
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"删除失败: {e}")
    
    def execute(self, sql: str, params: Tuple = None) -> int:
        """
        执行原生SQL
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            int: 影响行数
            
        Raises:
            DatabaseOperationError: 执行失败
        """
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    affected = cursor.execute(sql, params)
                    conn.commit()
                    return affected
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"执行失败: {e}")
    
    def upsert(self, table: str, data: Dict,
               conflict_columns: List[str] = None) -> int:
        """
        插入或更新（Upsert）

        Args:
            table: 表名
            data: 数据字典
            conflict_columns: 冲突判断列名列表（主键/唯一索引列，这些列在冲突时不更新）

        Returns:
            int: 影响行数

        Raises:
            DatabaseOperationError: 执行失败
        """
        if not data:
            raise DatabaseOperationError("数据不能为空")

        columns = ', '.join([f'`{col}`' for col in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))

        if conflict_columns:
            update_columns = [col for col in data.keys() if col not in conflict_columns]
        else:
            update_columns = list(data.keys())

        update_clause = ', '.join([f"`{key}` = VALUES(`{key}`)" for key in update_columns])

        sql = (f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
               f"ON DUPLICATE KEY UPDATE {update_clause}")
        
        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    affected = cursor.execute(sql, tuple(data.values()))
                    conn.commit()
                    return affected
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"Upsert失败: {e}")
    
    def batch_upsert(self, table: str, data_list: List[Dict],
                     conflict_columns: List[str] = None) -> int:
        """
        批量插入或更新（Upsert）

        Args:
            table: 表名
            data_list: 数据字典列表
            conflict_columns: 冲突判断列名列表（主键/唯一索引列，这些列在冲突时不更新）

        Returns:
            int: 总影响行数

        Raises:
            DatabaseOperationError: 执行失败
        """
        if not data_list:
            return 0

        columns = list(data_list[0].keys())
        column_names = ', '.join([f'`{col}`' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))

        if conflict_columns:
            update_columns = [col for col in columns if col not in conflict_columns]
        else:
            update_columns = columns

        update_clause = ', '.join([f"`{key}` = VALUES(`{key}`)" for key in update_columns])

        sql = (f"INSERT INTO {table} ({column_names}) VALUES ({placeholders}) "
               f"ON DUPLICATE KEY UPDATE {update_clause}")

        def convert_nan_to_none(value):
            """将NaN值转换为None"""
            if value is None:
                return None
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                return None
            return value

        BATCH_SIZE = 500
        total_affected = 0

        try:
            conn = self.get_connection()
            try:
                with conn.cursor() as cursor:
                    for i in range(0, len(data_list), BATCH_SIZE):
                        batch = data_list[i:i + BATCH_SIZE]
                        values_list = [
                            tuple(convert_nan_to_none(data[col]) for col in columns)
                            for data in batch
                        ]
                        cursor.executemany(sql, values_list)
                        total_affected += len(batch)
                    conn.commit()
                return total_affected
            except Exception as e:
                conn.rollback()
                raise DatabaseOperationError(f"批量Upsert失败: {e}")
            finally:
                conn.close()
        except pymysql.Error as e:
            raise DatabaseOperationError(f"批量Upsert失败: {e}")
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 是否存在
        """
        sql = "SHOW TABLES LIKE %s"
        try:
            result = self.query(sql, (table_name,))
            return len(result) > 0
        except DatabaseOperationError:
            return False
    
    def create_table(self, table_name: str, columns: Dict[str, str],
                     primary_key: str = None, indexes: List[str] = None) -> bool:
        """
        创建表
        
        Args:
            table_name: 表名
            columns: 列定义字典，键为列名，值为类型定义
            primary_key: 主键列名
            indexes: 索引列名列表
            
        Returns:
            bool: 是否创建成功
            
        Raises:
            DatabaseOperationError: 创建失败
        """
        column_defs = []
        for col_name, col_type in columns.items():
            column_defs.append(f"{col_name} {col_type}")
        
        if primary_key:
            column_defs.append(f"PRIMARY KEY ({primary_key})")
        
        if indexes:
            for idx_col in indexes:
                column_defs.append(f"INDEX idx_{idx_col} ({idx_col})")
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (" + ', '.join(column_defs) + ")"
        
        try:
            self.execute(sql)
            return True
        except DatabaseOperationError as e:
            raise DatabaseOperationError(f"创建表失败: {e}")
    
    def get_table_count(self, table_name: str, where: str = None,
                        where_params: Tuple = None) -> int:
        """
        获取表记录数
        
        Args:
            table_name: 表名
            where: WHERE条件
            where_params: 条件参数
            
        Returns:
            int: 记录数
        """
        sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
        if where:
            sql += f" WHERE {where}"
        
        try:
            result = self.query(sql, where_params)
            if result:
                return result[0].get('cnt', 0)
            return 0
        except DatabaseOperationError:
            return 0
    
    def close(self) -> None:
        """关闭数据库连接"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
