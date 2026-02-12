-- ====================================
-- 接口名称：repurchase
-- 接口说明：股票回购
-- doc_id: 124
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_repurchase;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_repurchase (
    ID INT COMMENT '主键ID',
    TS_CODE VARCHAR(20) COMMENT 'TS代码',
    ANN_DATE VARCHAR(8) COMMENT '公告日期',
    END_DATE VARCHAR(8) COMMENT '截止日期',
    `PROC` VARCHAR(50) COMMENT '进度',
    EXP_DATE VARCHAR(8) COMMENT '过期日期',
    VOL VARCHAR(50) COMMENT '回购数量',
    AMOUNT DECIMAL(20,2) COMMENT '回购金额',
    HIGH_LIMIT DECIMAL(10,2) COMMENT '回购最高价',
    LOW_LIMIT DECIMAL(10,2) COMMENT '回购最低价',
    REPO_GOAL VARCHAR(200) COMMENT '回购目的',
    UPDATE_FLAG VARCHAR(10) COMMENT '更新标识',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票回购';
