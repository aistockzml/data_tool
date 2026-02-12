-- 同花顺行业资金流向（THS）表
-- 接口: moneyflow_ind_ths
-- 描述: 获取同花顺行业资金流向，每日盘后更新
-- 积分: 5000积分可以调取
-- 字段数量: 18

CREATE TABLE IF NOT EXISTS `aistockzml_tushare_moneyflow_ind_ths` (
    `ID` varchar(20) NULL COMMENT 'ID',
    `CREATE_TIME` varchar(20) NULL COMMENT '创建时间',
    `CREATE_BY` varchar(20) NULL COMMENT '创建人',
    `UPDATE_TIME` varchar(20) NULL COMMENT '更新时间',
    `UPDATE_BY` varchar(20) NULL COMMENT '更新人',
    `INSERT_TIME` varchar(20) NULL COMMENT '插入时间',
    `TRADE_DATE` varchar(20) NOT NULL COMMENT '交易日期',
    `TS_CODE` varchar(20) NOT NULL COMMENT '板块代码',
    `INDUSTRY` varchar(50) NULL COMMENT '板块名称',
    `LEAD_STOCK` varchar(50) NULL COMMENT '领涨股票名称',
    `LATEST` decimal(20,6) NULL COMMENT '领涨股最新价',
    `INDUSTRY_INDEX` decimal(20,6) NULL COMMENT '收盘指数',
    `PCT_CHANGE` decimal(20,6) NULL COMMENT '指数涨跌幅',
    `COMPANY_NUM` int NULL COMMENT '公司数量',
    `PCT_CHANGE_STOCK` decimal(20,6) NULL COMMENT '领涨股涨跌幅',
    `NET_BUY_AMOUNT` decimal(20,6) NULL COMMENT '流入资金(亿元)',
    `NET_SELL_AMOUNT` decimal(20,6) NULL COMMENT '流出资金(亿元)',
    `NET_AMOUNT` decimal(20,6) NULL COMMENT '净额(亿元)',
    `etl_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据采集时间',
    PRIMARY KEY (`TS_CODE`, `TRADE_DATE`),
    KEY `idx_trade_date` (`TRADE_DATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='同花顺行业资金流向（THS）表';
