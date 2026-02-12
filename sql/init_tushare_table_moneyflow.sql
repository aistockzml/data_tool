-- 个股资金流向表
-- 接口: moneyflow
-- 描述: 获取沪深A股票资金流向数据，分析大单小单成交情况，用于判别资金动向，数据开始于2010年
-- 积分: 用户需要至少2000积分才可以调取
-- 字段数量: 26

CREATE TABLE IF NOT EXISTS `aistockzml_tushare_moneyflow` (
    `ID` varchar(20) NULL COMMENT 'ID',
    `CREATE_TIME` varchar(20) NULL COMMENT '创建时间',
    `CREATE_BY` varchar(20) NULL COMMENT '创建人',
    `UPDATE_TIME` varchar(20) NULL COMMENT '更新时间',
    `UPDATE_BY` varchar(20) NULL COMMENT '更新人',
    `TS_CODE` varchar(20) NOT NULL COMMENT 'TS代码',
    `TRADE_DATE` varchar(20) NOT NULL COMMENT '交易日期',
    `BUY_SM_VOL` int NULL COMMENT '小单买入量（手）',
    `BUY_SM_AMOUNT` decimal(20,6) NULL COMMENT '小单买入金额（万元）',
    `SELL_SM_VOL` int NULL COMMENT '小单卖出量（手）',
    `SELL_SM_AMOUNT` decimal(20,6) NULL COMMENT '小单卖出金额（万元）',
    `BUY_MD_VOL` int NULL COMMENT '中单买入量（手）',
    `BUY_MD_AMOUNT` decimal(20,6) NULL COMMENT '中单买入金额（万元）',
    `SELL_MD_VOL` int NULL COMMENT '中单卖出量（手）',
    `SELL_MD_AMOUNT` decimal(20,6) NULL COMMENT '中单卖出金额（万元）',
    `BUY_LG_VOL` int NULL COMMENT '大单买入量（手）',
    `BUY_LG_AMOUNT` decimal(20,6) NULL COMMENT '大单买入金额（万元）',
    `SELL_LG_VOL` int NULL COMMENT '大单卖出量（手）',
    `SELL_LG_AMOUNT` decimal(20,6) NULL COMMENT '大单卖出金额（万元）',
    `BUY_ELG_VOL` int NULL COMMENT '特大单买入量（手）',
    `BUY_ELG_AMOUNT` decimal(20,6) NULL COMMENT '特大单买入金额（万元）',
    `SELL_ELG_VOL` int NULL COMMENT '特大单卖出量（手）',
    `SELL_ELG_AMOUNT` decimal(20,6) NULL COMMENT '特大单卖出金额（万元）',
    `NET_MF_VOL` int NULL COMMENT '净流入量（手）',
    `NET_MF_AMOUNT` decimal(20,6) NULL COMMENT '净流入额（万元）',
    `TRADE_COUNT` int NULL COMMENT '交易笔数',
    `etl_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    PRIMARY KEY (`TS_CODE`, `TRADE_DATE`),
    KEY `idx_trade_date` (`TRADE_DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股资金流向表';
