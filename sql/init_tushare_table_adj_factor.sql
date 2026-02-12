-- 复权因子表
-- 接口: adj_factor
-- 描述: 获取股票复权因子，可提取单只股票全部历史复权因子，也可以提取单日全部股票的复权因子
-- 积分要求: 2000积分起，5000以上可高频调取

CREATE TABLE IF NOT EXISTS `aistockzml_tushare_adj_factor` (
    `ID` varchar(20) NULL COMMENT 'ID',
    `CREATE_TIME` varchar(20) NULL COMMENT '创建时间',
    `CREATE_BY` varchar(20) NULL COMMENT '创建人',
    `UPDATE_TIME` varchar(20) NULL COMMENT '更新时间',
    `UPDATE_BY` varchar(20) NULL COMMENT '更新人',
    `TS_CODE` varchar(20) NOT NULL COMMENT '股票代码',
    `TRADE_DATE` varchar(20) NOT NULL COMMENT '交易日期',
    `ADJ_FACTOR` decimal(20,6) NULL COMMENT '复权因子',
    `etl_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    PRIMARY KEY (`TS_CODE`, `TRADE_DATE`),
    KEY `idx_trade_date` (`TRADE_DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='复权因子表';
