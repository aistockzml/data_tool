-- ====================================
-- 接口名称：moneyflow_ind_dc
-- 接口说明：东财概念及行业板块资金流向（DC）
-- doc_id: 344
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_moneyflow_ind_dc;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_moneyflow_ind_dc (
    TRADE_DATE VARCHAR(8) COMMENT '交易日期',
    CONTENT_TYPE VARCHAR(20) COMMENT '数据类型',
    INS_CODE VARCHAR(20) COMMENT 'DC板块代码',
    NAME VARCHAR(50) COMMENT '板块名称',
    PCT_CHANGE DECIMAL(10,2) COMMENT '板块涨跌幅（%）',
    LATEST DECIMAL(20,4) COMMENT '板块最新指数',
    BUY_MAIN_AMOUNT DECIMAL(20,2) COMMENT '今日主力净流入净额（元）',
    BUY_MAIN_AMOUNT_RATE DECIMAL(10,2) COMMENT '今日主力净流入净占比%',
    BUY_ELG_AMOUNT DECIMAL(20,2) COMMENT '今日超大单净流入净额（元）',
    BUY_ELG_AMOUNT_RATE DECIMAL(10,2) COMMENT '今日超大单净流入净占比%',
    BUY_LG_AMOUNT DECIMAL(20,2) COMMENT '今日大单净流入净额（元）',
    BUY_LG_AMOUNT_RATE DECIMAL(10,2) COMMENT '今日大单净流入净占比%',
    BUY_MD_AMOUNT DECIMAL(20,2) COMMENT '今日中单净流入净额（元）',
    BUY_MD_AMOUNT_RATE DECIMAL(10,2) COMMENT '今日中单净流入净占比%',
    BUY_SM_AMOUNT DECIMAL(20,2) COMMENT '今日小单净流入净额（元）',
    BUY_SM_AMOUNT_RATE DECIMAL(10,2) COMMENT '今日小单净流入净占比%',
    BUY_SM_AMOUNT_STOCK VARCHAR(20) COMMENT '今日主力净流入最大股',
    `RANK` INT COMMENT '序号',
    INSERT_TIME VARCHAR(19) COMMENT '插入时间',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (TRADE_DATE, INS_CODE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='东财概念及行业板块资金流向（DC）';
