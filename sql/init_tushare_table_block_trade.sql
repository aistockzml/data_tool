-- ====================================
-- 接口名称：block_trade
-- 接口说明：大宗交易
-- doc_id: 161
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_block_trade;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_block_trade (
    ID INT COMMENT '主键ID',
    TS_CODE VARCHAR(20) COMMENT 'TS代码',
    TRADE_DATE VARCHAR(8) COMMENT '交易日历',
    PRICE DECIMAL(10,2) COMMENT '成交价',
    VOL DECIMAL(20,2) COMMENT '成交量（万股）',
    AMOUNT DECIMAL(20,2) COMMENT '成交金额',
    BUYER VARCHAR(200) COMMENT '买方营业部',
    SELLER VARCHAR(200) COMMENT '卖方营业部',
    NUM_TIMES INT COMMENT '次数',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大宗交易';
