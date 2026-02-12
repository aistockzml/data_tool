-- ====================================
-- 接口名称：stk_holdertrade
-- 接口说明：股东增减持
-- doc_id: 175
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_stk_holdertrade;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_stk_holdertrade (
    ID INT COMMENT '主键ID',
    TS_CODE VARCHAR(20) COMMENT 'TS代码',
    ANN_DATE VARCHAR(8) COMMENT '公告日期',
    HOLDER_NAME VARCHAR(100) COMMENT '股东名称',
    HOLDER_TYPE VARCHAR(10) COMMENT '股东类型G高管P个人C公司',
    IN_DE VARCHAR(10) COMMENT '类型IN增持DE减持',
    CHANGE_VOL DECIMAL(20,2) COMMENT '变动数量',
    CHANGE_RATIO DECIMAL(10,4) COMMENT '占流通比例（%）',
    AFTER_SHARE DECIMAL(20,2) COMMENT '变动后持股',
    AFTER_RATIO DECIMAL(10,4) COMMENT '变动后占流通比例（%）',
    AVG_PRICE DECIMAL(10,4) COMMENT '平均价格',
    TOTAL_SHARE DECIMAL(20,2) COMMENT '持股总数',
    BEGIN_DATE VARCHAR(8) COMMENT '增减持开始日期',
    CLOSE_DATE VARCHAR(8) COMMENT '增减持结束日期',
    UPDATE_FLAG VARCHAR(10) COMMENT '更新标识',
    CREATE_TIME VARCHAR(19) COMMENT '创建时间',
    CREATE_BY VARCHAR(50) COMMENT '创建者',
    UPDATE_TIME VARCHAR(19) COMMENT '更新时间',
    UPDATE_BY VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股东增减持';
