-- ====================================
-- 接口名称：stk_holdernumber
-- 接口说明：股东人数
-- doc_id: 166
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_stk_holdernumber;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_stk_holdernumber (
    ID INT COMMENT '主键ID',
    TS_CODE VARCHAR(20) COMMENT 'TS股票代码',
    ANN_DATE VARCHAR(8) COMMENT '公告日期',
    END_DATE VARCHAR(8) COMMENT '截止日期',
    HOLDER_NUM INT COMMENT '股东户数',
    HOLDER_TOTAL INT COMMENT '股东总数',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股东人数';
