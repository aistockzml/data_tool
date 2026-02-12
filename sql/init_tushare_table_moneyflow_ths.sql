-- 个股资金流向（THS）表
-- 接口: moneyflow_ths
-- 描述: 获取同花顺个股资金流向数据，每日盘后更新
-- 积分: 用户需要至少5000积分才可以调取
-- 字段数量: 19

CREATE TABLE IF NOT EXISTS `aistockzml_tushare_moneyflow_ths` (
    `ID` varchar(20) NULL COMMENT 'ID',
    `CREATE_TIME` varchar(20) NULL COMMENT '创建时间',
    `CREATE_BY` varchar(20) NULL COMMENT '创建人',
    `UPDATE_TIME` varchar(20) NULL COMMENT '更新时间',
    `UPDATE_BY` varchar(20) NULL COMMENT '更新人',
    `INSERT_TIME` varchar(20) NULL COMMENT '插入时间',
    `TRADE_DATE` varchar(20) NOT NULL COMMENT '交易日期',
    `TS_CODE` varchar(20) NOT NULL COMMENT '股票代码',
    `NAME` varchar(50) NULL COMMENT '股票名称',
    `PCT_CHANGE` decimal(20,6) NULL COMMENT '涨跌幅',
    `LATEST` decimal(20,6) NULL COMMENT '最新价',
    `NET_AMOUNT` decimal(20,6) NULL COMMENT '资金净流入(万元)',
    `NET_D5_AMOUNT` decimal(20,6) NULL COMMENT '5日主力净额(万元)',
    `BUY_MAIN_AMOUNT` decimal(20,6) NULL COMMENT '今日主力净流入额(万元)',
    `BUY5_MAIN_AMOUNT` decimal(20,6) NULL COMMENT '5日主力净流入额(万元)',
    `BUY_LG_AMOUNT` decimal(20,6) NULL COMMENT '今日大单净流入额(万元)',
    `BUY_LG_AMOUNT_RATE` decimal(20,6) NULL COMMENT '今日大单净流入占比(%)',
    `BUY_MD_AMOUNT` decimal(20,6) NULL COMMENT '今日中单净流入额(万元)',
    `BUY_MD_AMOUNT_RATE` decimal(20,6) NULL COMMENT '今日中单净流入占比(%)',
    `BUY_SM_AMOUNT` decimal(20,6) NULL COMMENT '今日小单净流入额(万元)',
    `BUY_SM_AMOUNT_RATE` decimal(20,6) NULL COMMENT '今日小单净流入占比(%)',
    `etl_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    PRIMARY KEY (`TS_CODE`, `TRADE_DATE`),
    KEY `idx_trade_date` (`TRADE_DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个股资金流向（THS）表';
