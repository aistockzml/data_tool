[框架介绍]
开发一个通用的金融数据采集Python框架，框架名称为`data_tools`，可集成tushare、akshare等主流数据接口，实现统一的数据采集与管理。框架包含以下核心模块：
- 数据采集模块 ：提供可扩展的API接口，支持用户自定义数据源的采集逻辑。
- 数据存储模块 ：负责采集数据的持久化存储，支持mysql数据库等。
- 日志模块 ：统一管理框架运行日志，包括任务执行日志、错误日志等。
- 配置模块 ：集中管理数据源配置、采集参数等，支持从配置文件中读取配置。
框架设计遵循模块化、可扩展的原则，便于后续接入新的数据源和功能模块。

[框架规范]
1. 代码结构：
    - 采用基类+子类的继承模式，数据采集、数据存储、任务调度、日志、配置五大模块的通用功能在基类中定义，子类继承后实现具体逻辑。
    - 子类可根据需要重写父类方法或扩展新方法，保持核心架构稳定的同时满足个性化需求。
    - 模块间职责清晰、互不干扰，通过标准接口通信，耦合度低。
    - 遵循"只做铲子"原则，框架只提供通用能力，不执行业务逻辑，业务逻辑由用户通过继承和扩展实现。
    - 不要在各个模块中加入logger，模块内不使用日志记录，由用户在主程序中配置日志记录。

2. 代码质量：
    - 代码简洁易懂，避免使用复杂的语法或技巧，优先使用直观的实现方式。
    - 采用Python语言编写，符合Python代码规范。
    - 关键逻辑使用中文注释说明，注释内容简洁准确。
    - 合理使用异常处理机制，确保程序健壮性，对可能出现的异常进行捕获、处理、记录日志等。
   
4. 代码性能：
    - 使用高效的算法和数据结构，避免重复计算和内存占用。

[功能说明]
### 1. 数据采集模块（目前支持tushare和akshare）：
#### 1.1 数据链接器类DataConnector
    职责：负责数据源连接，提供统一的连接获取接口，子类可根据需要实现具体的连接逻辑。
    输入参数：
        - token：字符串，可选参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
    核心属性：
        - token：字符串，可选参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
        - connectors：链接对象
    核心方法：
        -- __init__(self, token: str = None)：构造函数，初始化数据源名称和可选的API密钥或Token。
            * 功能：通过token初始化链接对象，存储在connectors属性中。
            * 参数token：可选参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
            * 返回值：无

#### 1.2 tushare数据采集器类TushareDataCollector
    职责：继承DataCollector类，使用tushare Python库创建链接对象。
    输入参数：
        - token：字符串，必填参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
    核心属性：
        - token：字符串，必填参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
        - connectors：链接对象，用于存储tushare链接对象
    核心方法：
        - __init__(self, token: str = None)：构造函数，初始化数据源名称和必填的API密钥或Token。
            * 功能：创建tushare链接对象，存储在connectors属性中。
            * 参数token：必填参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
            * 返回值：无

#### 1.3 akshare数据采集器类AkshareDataCollector
    职责：继承DataCollector类，使用akshare Python库创建链接对象。
    输入参数：
        无
    核心属性：
        - connectors：链接对象，用于存储akshare链接对象
    核心方法：
        - __init__(self)：构造函数。
            * 功能：创建akshare链接对象，存储在connectors属性中。
            * 参数token：必填参数，数据源的API密钥或Token，用于认证和授权访问数据源API。
            * 返回值：无

#### 1.4 数据采集器类DataCollector
    职责：定义数据采集的通用框架，子类继承后实现具体数据源的采集逻辑。
    输入参数：
        - connector：DataConnector.connectors属性，数据源连接对象
        - collect_name：字符串，数据采集器的唯一标识符，用于任务调度和日志追踪
        - description：字符串，可选参数，数据采集器的功能描述
        - db_conn：数据库连接对象，可选参数，数据采集器采集数据的目标数据库连接对象
    核心属性：
        - connector：数据源连接对象，由构造函数传入
        - collect_name：字符串，数据采集器的唯一标识符，用于任务调度和日志追踪
        - description：字符串，可选参数，数据采集器的功能描述
        - db_conn：数据库连接对象，可选参数，数据采集器采集数据的目标数据库连接对象
    核心方法：
        - collect(**kwargs) -> Optional[pd.DataFrame]：
            * 使用connector调用具体的采集方法，如tushare的stock_basic()或akshare的stock_zh_a_daily()
            * **kwargs支持额外参数传入，如日期范围、股票代码等
            * 返回采集到的数据（DataFrame格式），无数据时返回None
            * 子类必须重写此方法实现具体采集逻辑
            * 支持失败重试机制，配置重试次数、重试间隔、退避策略
            * 支持缓存机制，避免重复采集相同数据
        - save_db(data: pd.DataFrame, target_table: str) -> bool：
            * 功能：将采集到的数据保存到数据库中
            * 参数data：由collect方法返回的DataFrame
            * 参数target_table：字符串，必填参数，数据库表名
            * 返回布尔值，表示保存是否成功
            * 子类必须重写此方法实现具体保存逻辑
            * 若提供db_conn和target_table参数，应使用这两个参数进行数据库操作
        - save_csv(data: pd.DataFrame, filename: str) -> bool：
            * 功能：将采集到的数据保存到CSV文件中
            * 参数data：由collect方法返回的DataFrame
            * 参数filename：字符串，必填参数，CSV文件名
            * 返回布尔值，表示保存是否成功
            * 子类必须重写此方法实现具体保存逻辑
            * 若提供filename参数，应将数据保存到指定的CSV文件中 
        - validate(data: pd.DataFrame) -> tuple[bool, list]：
            * 功能：对采集到的数据进行校验
            * 参数data：由collect方法返回的DataFrame
            * 返回元组(是否有效, 错误信息列表)
            * 子类可选择性重写，添加自定义校验规则
        - transform(data: pd.DataFrame) -> pd.DataFrame：
            * 功能：对采集到的数据进行格式转换和预处理
            * 参数data：由collect方法返回的DataFrame
            * 返回转换后的DataFrame
            * 子类可选择性重写，添加自定义转换逻辑
    使用方法：
        - 新建子类继承DataCollector
        - 重写collect方法，实现具体数据源的采集逻辑
        - 重写save方法，实现具体的数据保存逻辑
        - 可选重写validate、transform方法，添加校验和转换逻辑

### 2. 数据存储模块
#### 2.1 数据库连接类 MySqlOperator
    职责：MySQL 数据库操作类，提供数据库连接和操作方法。
    输入参数：
        - host：字符串，可选参数，数据库主机地址，默认值为 'localhost'
        - port：整数，可选参数，数据库端口号，默认值为 3306
        - user：字符串，可选参数，数据库用户名，默认值为 'root'
        - password：字符串，可选参数，数据库密码，默认值为空字符串
        - database：字符串，可选参数，数据库名，默认值为空字符串
        - charset：字符串，可选参数，数据库字符集，默认值为 'utf8mb4'
        - connect_timeout：整数，可选参数，连接超时时间，默认值为 10 秒
        - read_timeout：整数，可选参数，读取超时时间，默认值为 10 秒
        - write_timeout：整数，可选参数，写入超时时间，默认值为 10 秒
        - pool_size：整数，可选参数，连接池大小，默认值为 10 个连接
    核心属性：
        - connector：数据库连接对象，由pymysql库创建
    核心方法：
        - query(sql: str, params: tuple = None)：执行查询，返回结果列表
        - insert(table: str, data: dict)：插入单条数据，返回插入ID
        - batch_insert(table: str, data_list: list[dict])：批量插入，返回影响行数
        - update(table: str, data: dict, where: str, where_params: tuple)：更新数据，返回影响行数
        - delete(table: str, where: str, where_params: tuple)：删除数据，返回影响行数
        - execute(sql: str, params: tuple = None)：执行原生SQL，返回影响行数
        - close()：关闭数据库连接
    异常处理：
        - 自动重连机制，断开连接后自动重新建立
        - 连接池管理，支持多个连接实例共享连接资源
        - 连接池大小配置，支持自定义连接池数量
        - 连接池超时配置，支持自定义连接超时时间
        - 连接池最大连接数配置，支持自定义最大连接数
        - 参数化查询防止 SQL 注入攻击
        - 支持事务操作，确保数据一致性
        - 执行错误时抛出 `DatabaseOperationError` 异常

### 4. 日志模块：
#### 4.1 日志管理器类LoggerManager
    职责：负责日志的统一管理，提供日志配置和日志器获取接口。
    输入参数：
        - log_level：字符串，可选参数，日志级别，默认值为 'INFO'
        - log_output：字符串，可选参数，日志输出方式，默认值为 'console'，支持 'console' 和 'file'
    核心方法：
        - get_logger(name: str) -> DataLogger：
            * 根据名称获取对应的日志器实例
            * 参数name：日志器名称，建议使用模块名
            * 相同名称返回同一实例
        - configure(**kwargs)：动态修改日志配置
            * 参数kwargs：日志配置参数，包括log_level、log_output等
            * 支持动态修改日志级别和输出方式

#### 4.2 日志记录器类DataLogger
    职责：提供日志记录功能，支持多模块日志追踪和日志分级，使用python的logging模块实现。
    输入参数：
        - name：日志器名称
    核心方法：
        - debug(message: str, **kwargs)：记录调试日志
        - info(message: str, **kwargs)：记录信息日志
        - warning(message: str, **kwargs)：记录警告日志
        - error(message: str, exc_info: bool = False, **kwargs)：记录错误日志
        - critical(message: str, exc_info: bool = False, **kwargs)：记录严重错误日志
    使用方法：
        - 通过LoggerManager获取日志器，例如 logger = LoggerManager().get_logger("data_collector")
        - 使用不同级别记录日志，例如 logger.info("采集开始")

#### 4.3 要求事项：
    - 支持日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
    - 支持输出方式：控制台、文件
    - 支持多目标同时输出：控制台+文件等
    - 日志格式：[时间] [日志级别] [模块名] [任务ID] 日志消息
    - 日志消息为中文，方便阅读和理解
   
### 5.配置模块
#### 5.1 配置解析器类ConfigParser
    职责：使用python pyyaml库解析配置文件，提供配置文件中参数的获取接口。
    输入参数：
        - config_file：配置文件路径
    核心属性：
        - config：字典类型，存储解析后的配置项
    核心方法：
        - __init__(self, config_file: str)：加载配置文件
            * 参数config_file：配置文件路径
            * 异常处理：如果配置文件不存在，抛出FileNotFoundError异常
            * 功能：加载配置文件，解析为字典格式，存储在类属性config中
        - get_config(section: str, option: str) -> Any：
            * 根据section和option获取配置参数
            * 参数section：配置文件中的节名
            * 参数option：配置项名
            * 返回值：字典类型，配置项对应的值
            * 异常处理：如果section或option不存在，抛出KeyError异常

#### 5.2 配置文件（base_config.yaml）
文件格式：YAML
文件名：base_config.yaml
文件描述：数据库配置、日志配置、数据采集器配置都在这个文件中。
文件内容：
(1)数据采集器配置`collect_config`，类型为key-value对象，key为采集器名称，值为采集器的配置，每个采集器的配置包含以下参数：
    - collect_name：采集器名称，建议使用模块名
    - description：采集器描述，用于标识采集任务的功能
    - data_source：数据来源，例如股票API、数据库等
    - api_name：API名称，用于调用数据来源的接口
    - target_table：目标数据库表名，用于存储采集到的数据
    - schedule：采集任务调度配置，包括时间间隔、开始时间、结束时间等
        - interval：采集任务时间间隔，单位为秒，默认值为3600（1小时）
        - cron：采集任务定时表达式，默认值为空字符串
    - enabled：是否启用采集任务，默认值为True

(2)数据库配置`db_config`，类型为字典，包含以下参数：
    - host：数据库主机地址
    - port：数据库端口号
    - user：数据库用户名
    - password：数据库密码
    - database：数据库名称

(3)日志配置`log_config`，类型为字典，包含以下参数：
    - log_level：日志级别，DEBUG/INFO/WARNING/ERROR/CRITICAL
    - log_output：日志输出方式，console/file/both，默认值为console
    - log_file：日志文件名，默认值为`data_collector.log`
    - log_format：日志格式，默认值为`[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s`
    - log_datefmt：日志日期格式，默认值为`%Y-%m-%d %H:%M:%S`
    - log_encoding：日志文件编码，默认值为utf-8
    - log_max_bytes：日志文件最大大小，默认值为10MB
    - log_backup_count：日志文件备份数量，默认值为5
    - log_console_level：控制台日志级别，默认值为INFO
    - log_file_level：文件日志级别，默认值为DEBUG

[其他要求]
- 编写框架使用文档，包含环境配置、依赖说明、类及函数说明、参数说明、返回值说明和调用示例，写在readme.md文件中。
- 提供一个简单的使用示例，演示采集股票数据并存储到数据库的完整流程，放置在项目`example`目录下，包括配置文件、代码文件和运行截图。
- 代码编写目录中`data_tools`模块下。
- 必须包括requirements.txt文件，列出项目依赖的Python库。
