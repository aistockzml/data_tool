-- ====================================
-- 接口名称：moneyflow_hsgt
-- 接口说明：沪深港通资金流向
-- doc_id: 47
-- 生成时间：2026-02-12
-- 说明：基于实际返回数据生成
-- ====================================

DROP TABLE IF EXISTS aistockzml_tushare_moneyflow_hsgt;

CREATE TABLE IF NOT EXISTS aistockzml_tushare_moneyflow_hsgt (
    TRADE_DATE VARCHAR(8) COMMENT '交易日期',
    GGT_SS VARCHAR(20) COMMENT '港股通（上海）',
    GGT_SZ VARCHAR(20) COMMENT '港股通（深圳）',
    HGT VARCHAR(20) COMMENT '沪股通（百万元）',
    SGT VARCHAR(20) COMMENT '深股通（百万元）',
    NORTH_MONEY VARCHAR(20) COMMENT '北向资金（百万元）',
    SOUTH_MONEY VARCHAR(20) COMMENT '南向资金（百万元）',
    hisvalid INT COMMENT '有效标识',
    hcreate_time VARCHAR(19) COMMENT '创建时间',
    hcreate_by VARCHAR(50) COMMENT '创建者',
    hupdate_time VARCHAR(19) COMMENT '更新时间',
    hupdate_by VARCHAR(50) COMMENT '更新者',
    etl_time DATETIME COMMENT '数据加载时间',
    PRIMARY KEY (TRADE_DATE)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='沪深港通资金流向';
