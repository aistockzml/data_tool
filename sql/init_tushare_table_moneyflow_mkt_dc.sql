-- ====================================
-- 接口名称：moneyflow_mkt_dc
-- 接口说明：大盘资金流向（DC）
-- doc_id: 345
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_moneyflow_mkt_dc;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_moneyflow_mkt_dc (
    ID INT COMMENT '主键ID',
    TRADE_DATE VARCHAR(8) COMMENT '交易日期',
    CLOSE_SH DECIMAL(10,2) COMMENT '上证收盘价（点）',
    CHANGE_SH DECIMAL(10,2) COMMENT '上证涨跌幅(%)',
    CLOSE_SZ DECIMAL(10,2) COMMENT '深证收盘价（点）',
    CHANGE_SZ DECIMAL(10,2) COMMENT '深证涨跌幅(%)',
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
    INSERT_TIME VARCHAR(19) COMMENT '插入时间',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大盘资金流向（DC）';
