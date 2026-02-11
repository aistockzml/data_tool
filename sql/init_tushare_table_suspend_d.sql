-- ====================================
-- 接口名称：suspend_d
-- 接口说明：每日停复牌信息
-- doc_id: 214
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_suspend_d;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_suspend_d (
    ID INT COMMENT '主键ID',
    TS_CODE VARCHAR(20) COMMENT 'TS代码',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    SUSPEND_TYPE VARCHAR(10) COMMENT '停复牌类型：S-停牌，R-复牌',
    SUSPEND_DATE VARCHAR(8) COMMENT '停复牌日期',
    SUSPEND_TIMING VARCHAR(50) COMMENT '日内停牌时间段',
    UNIQUE_ID VARCHAR(64) COMMENT '唯一标识',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日停复牌信息';
