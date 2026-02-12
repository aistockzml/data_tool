-- 每日筹码及胜率表
-- 接口: cyq_perf
-- 描述: 获取A股每日筹码平均成本和胜率情况，每天18~19点左右更新，数据从2018年开始
-- 积分: 5000积分每天20000次，10000积分每天200000次，15000积分每天不限总量
-- 字段数量: 12

CREATE TABLE IF NOT EXISTS `aistockzml_tushare_cyq_perf` (
    `TS_CODE` varchar(20) NOT NULL COMMENT '股票代码',
    `TRADE_DATE` varchar(20) NOT NULL COMMENT '交易日期',
    `TRADE_DATE_STR` varchar(20) NULL COMMENT '交易日期字符串',
    `HIS_LOW` decimal(20,6) NULL COMMENT '历史最低价',
    `HIS_HIGH` decimal(20,6) NULL COMMENT '历史最高价',
    `COST_5PCT` decimal(20,6) NULL COMMENT '5分位成本',
    `COST_15PCT` decimal(20,6) NULL COMMENT '15分位成本',
    `COST_50PCT` decimal(20,6) NULL COMMENT '50分位成本',
    `COST_85PCT` decimal(20,6) NULL COMMENT '85分位成本',
    `COST_95PCT` decimal(20,6) NULL COMMENT '95分位成本',
    `WEIGHT_AVG` decimal(20,6) NULL COMMENT '加权平均成本',
    `WINNER_RATE` decimal(20,6) NULL COMMENT '胜率',
    `etl_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    PRIMARY KEY (`TS_CODE`, `TRADE_DATE`),
    KEY `idx_trade_date` (`TRADE_DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日筹码及胜率表';
