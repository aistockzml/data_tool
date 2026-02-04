-- 股票基础信息
CREATE TABLE aistockzml_tushare_stock_base_info (
    ts_code VARCHAR(20) NOT NULL COMMENT 'TS代码',
    symbol VARCHAR(20) COMMENT '股票代码',
    name VARCHAR(50) COMMENT '股票名称',
    area VARCHAR(50) COMMENT '地域',
    industry VARCHAR(50) COMMENT '所属行业',
    fullname VARCHAR(200) COMMENT '股票全称',
    enname VARCHAR(200) COMMENT '英文全称',
    cnspell VARCHAR(30) COMMENT '拼音缩写',
    market VARCHAR(20) COMMENT '市场类型',
    exchange VARCHAR(20) COMMENT '交易所代码',
    curr_type VARCHAR(20) COMMENT '交易货币',
    list_status VARCHAR(10) COMMENT '上市状态',
    list_date DATE COMMENT '上市日期',
    delist_date DATE COMMENT '退市日期',
    is_hs VARCHAR(10) COMMENT '是否沪深港通标的',
    act_name VARCHAR(100) COMMENT '实控人名称',
    act_ent_type VARCHAR(50) COMMENT '实控人企业性质',
    PRIMARY KEY (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基础信息';


-- 上市公司基本信息
CREATE TABLE aistockzml_tushare_stock_company_base_info (
    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    com_name VARCHAR(500) COMMENT '公司全称',
    com_id VARCHAR(50) COMMENT '统一社会信用代码',
    exchange VARCHAR(20) COMMENT '交易所代码',
    chairman VARCHAR(50) COMMENT '法人代表',
    manager VARCHAR(50) COMMENT '总经理',
    secretary VARCHAR(50) COMMENT '董秘',
    reg_capital DECIMAL(20,4) COMMENT '注册资本(万元)',
    setup_date DATE COMMENT '注册日期',
    province VARCHAR(50) COMMENT '所在省份',
    city VARCHAR(100) COMMENT '所在城市',
    introduction TEXT COMMENT '公司介绍',
    website VARCHAR(500) COMMENT '公司主页',
    email VARCHAR(200) COMMENT '电子邮件',
    office VARCHAR(500) COMMENT '办公室',
    employees INT COMMENT '员工人数',
    main_business TEXT COMMENT '主要业务及产品',
    business_scope TEXT COMMENT '经营范围',
    PRIMARY KEY (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='上市公司基本信息';


-- 交易日历
CREATE TABLE aistockzml_tushare_trade_cal_base_info (
    exchange VARCHAR(20) NOT NULL COMMENT '交易所',
    cal_date DATE NOT NULL COMMENT '日历日期',
    is_open TINYINT COMMENT '是否交易 0休市 1交易',
    pretrade_date DATE COMMENT '上一个交易日',
    PRIMARY KEY (exchange, cal_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易日历';
