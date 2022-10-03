// *************************************************************************************************************************************************************************************************************************************************************************
// Acrypto - Weigthed Strategy v1.4.8
// Github: https://github.com/AlbertoCuadra/algo_trading_weighted_strategy
//
//
// You can support the project on https://www.buymeacoffee.com/acuadra
//
// License: © accry - This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License
//                    https://creativecommons.org/licenses/by-nc-sa/4.0/
//
// Last update: 23/04/2022
// *************************************************************************************************************************************************************************************************************************************************************************

// 改造者2
//        _e-e_
//      _(-._.-)_
//   .-(  `---'  )-. 
//  __\ \\\___/// /__
// '-._.'/M\ /M\`._,-`                                           
// © cchao918  
//@version=5
strategy(title='Acrypto Weighted策略 for 3commas', overlay=true,  pyramiding=1, currency=currency.NONE, initial_capital=100, default_qty_type=strategy.cash, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.04)
//precision=2, commission_value=0.075, commission_type=strategy.commission.percent, initial_capital=1000, currency=currency.USD, default_qty_type=strategy.percent_of_equity, default_qty_value=100, slippage=1)

// *************************************************************************************************************************************************************************************************************************************************************************
// 注释
// *************************************************************************************************************************************************************************************************************************************************************************
//1. 汉化
//2. 调整部分界面
//3. 适配3commas 
//4. 调整代码和注释的排版


// *************************************************************************************************************************************************************************************************************************************************************************
// 常量
// *************************************************************************************************************************************************************************************************************************************************************************
 //回测时间初始化
config_FromDay = '2021-01-01T00:00:00'
config_ToDay = '2025-01-01T00:00:00'

//做多机器人id
config_botidlong_all = '000000'
//做多机器人秘钥
config_emailtokenlong_all = '3a88fd59-e606-4654-9316-281522bb7105'
//做空机器人id
config_botidshort_all = '000000'
//做空机器人秘钥
config_emailtokenshort_all = 'c36d904e-532b-4048-9f25-ad4284604918'

//多单减仓机器人id
config_botidlong_part = '000000'
//多单减仓机器人秘钥
config_emailtokenlong_part = '3a88fd59-e606-4654-9316-281522bb7105'
//空单减仓机器人id
config_botidshort_part = '000000'
//空单减仓机器人秘钥
config_emailtokenshort_part = 'c36d904e-532b-4048-9f25-ad4284604918'

// *************************************************************************************************************************************************************************************************************************************************************************
// 输入参数
// *************************************************************************************************************************************************************************************************************************************************************************
// * 订单类型
allow_longs = input.bool(true, '做多', group='交易类型')
allow_shorts = input.bool(true, '做空', group='交易类型')

// * 时间
start = input.time(defval = timestamp(config_FromDay), title = "开始时间")
end = input.time(defval = timestamp(config_ToDay), title = "结束时间")  

// * 3commas设置
targettrick=input.string('BTCUSDT','品种名称',group='机器人设置')

botidlong_all=input.string(config_botidlong_all,'做多机器人id',group='机器人设置')
emailtokenlong_all=input.string(config_emailtokenlong_all,'做多机器人秘钥',group='机器人设置')
botidshort_all=input.string(config_botidshort_all,'做空机器人id',group='机器人设置')
emailtokenshort_all=input.string(config_emailtokenshort_all,'做空机器人秘钥',group='机器人设置')

botidlong_part=input.string(config_botidlong_part,'多单减仓机器人id',group='机器人设置')
emailtokenlong_part=input.string(config_emailtokenlong_part,'多单减仓机器人秘钥',group='机器人设置')
botidshort_part=input.string(config_botidshort_part,'空单减仓机器人id',group='机器人设置')
emailtokenshort_part=input.string(config_emailtokenshort_part,'空单减仓机器人秘钥',group='机器人设置')

// * 止损
stoploss = input.bool(true, '止损开关', group='止损')
movestoploss = input.string('TP-2', '移动止损', options=['None', 'Percentage', 'TP-1', 'TP-2', 'TP-3'], group='止损')
movestoploss_entry = input.bool(false, '移动止损到入口', group='止损')
stoploss_perc = input.float(6.0, '止损百分比', minval=0, maxval=100, group='止损') * 0.01
move_stoploss_factor = input.float(20.0, '移动止损因子(百分比)', group='止损') * 0.01 + 1
stop_source = input.source(hl2, '停止源', group='止损')

// * 止盈
take_profits = input.bool(true, '止盈开关', group='止盈')
// retrade= input.bool(false, 'Retrade', group='止盈')
MAX_TP = input.int(6, '最大TP数', minval=1, maxval=6, group='止盈')
long_profit_perc = input.float(6.8, ' 多单止盈百分比', minval=0.0, maxval=999, step=1, group='止盈') * 0.01
long_profit_qty = input.float(15, '多单止盈仓位占比', minval=0.0, maxval=100, step=1, group='止盈')
short_profit_perc = input.float(13, '空单止盈百分比', minval=0.0, maxval=999, step=1, group='止盈') * 0.01
short_profit_qty = input.float(10, '空单止盈仓位占比', minval=0.0, maxval=100, step=1, group='止盈')

// * 延迟
delay_macd = input.int(1, 'MACD烛线延迟', minval=1, group='延迟')
delay_srsi = input.int(2, 'Stoch RSI 烛线延迟', minval=1, group='延迟')
delay_rsi = input.int(2, ' RSI烛线延迟', minval=1, group='延迟')
delay_super = input.int(1, ' 超级趋势 烛线延迟', minval=1, group='延迟')
delay_cross = input.int(1, ' 均线交叉烛线延迟', minval=1, group='延迟')
delay_exit = input.int(7, '烛线延迟退出', minval=1, group='延迟')

// * 加权策略
str_0 = input.bool(true, '策略0：加权策略', group='权重')
weight_trigger = input.int(2, '重量信号输入 [0, 5]', minval=0, maxval=5, step=1, group='权重')
weight_str1 = input.int(1, '权重策略 1 [0, 5]', minval=0, maxval=5, step=1, group='权重')
weight_str2 = input.int(1, '权重策略 2 [0, 5]', minval=0, maxval=5, step=1, group='权重')
weight_str3 = input.int(1, '权重策略 3 [0, 5]', minval=0, maxval=5, step=1, group='权重')
weight_str4 = input.int(1, '权重策略 4 [0, 5]', minval=0, maxval=5, step=1, group='权重')
weight_str5 = input.int(1, '权重策略 5 [0, 5]', minval=0, maxval=5, step=1, group='权重')

// * 策略1：MACD
str_1 = input.bool(true, '策略1：MACD', group='策略1：MACD')
MA1_period_1 = input.int(16, '均线1', minval=1, maxval=9999, step=1, group='策略1：MACD')
MA1_type_1 = input.string('EMA', '均线1 类型', options=['RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'], group='策略1：MACD')
MA1_source_1 = input.source(hl2, '均线1 数据源', group='策略1：MACD')
MA2_period_1 = input.int(36, 'MA 2', minval=1, maxval=9999, step=1, group='策略1：MACD')
MA2_type_1 = input.string('EMA', '均线2 类型', options=['RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'], group='策略1：MACD')
MA2_source_1 = input.source(high, '均线2 数据源', group='策略1：MACD')

// * 策略 2：Stoch RSI 超卖/超买
str_2 = input.bool(true, '策略2：Stoch RSI 超卖/超买', group='策略2：Stoch RSI 超卖/超买')
long_RSI = input.float(70, '退出 SRSI 多单 (%)', minval=0.0, step=1, group='策略2：Stoch RSI 超卖/超买')
short_RSI = input.float(27, '退出 SRSI 空单 (%)', minval=0.0, step=1, group='策略2：Stoch RSI 超卖/超买')
length_RSI = input.int(14, 'RSI 长度', group='策略2：Stoch RSI 超卖/超买')
length_stoch = input.int(14, 'RSI 随机指标', group='策略2：Stoch RSI 超卖/超买')
smoothK = input.int(3, '平滑 k', group='策略2：Stoch RSI 超卖/超买')

// * RSI 超卖/超买
str_3 = input.bool(true, '策略 3：RSI', group='策略 3：RSI')
long_RSI2 = input.float(77, '退出 RSI 多头 (%)', minval=0.0, step=1, group='策略 3：RSI')
short_RSI2 = input.float(30, '退出 RSI 空头 (%)', minval=0.0, step=1, group='策略 3：RSI')

// * 策略 4：超级趋势
str_4 = input.bool(true, '策略4：超级趋势', group='策略4：超级趋势')
periods_4 = input.int(2, 'ATR 周期', group='策略4：超级趋势')
source_4 = input.source(hl2, '数据源', group='策略4：超级趋势')
multiplier = input.float(2.4, 'ATR 乘数', step=0.1, group='策略4：超级趋势')
change_ATR = input.bool(true, '更改 ATR 计算方法 ?', group='策略4：超级趋势')

// * 策略 5：均线交叉
str_5 = input.bool(true, '策略 5：均线交叉', group='策略 5：均线交叉')
MA1_period_5 = input.int(46, '均线1', minval=1, maxval=9999, step=1, group='策略 5：均线交叉')
MA1_type_5 = input.string('EMA', '均线1 类型', options=['RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'], group='策略 5：均线交叉')
MA1_source_5 = input.source(close, '均线1 数据源', group='策略 5：均线交叉')
MA2_period_5 = input.int(82, '均线2', minval=1, maxval=9999, step=1, group='策略 5：均线交叉')
MA2_type_5 = input.string('EMA', '均线2 类型', options=['RMA', 'SMA', 'EMA', 'WMA', 'HMA', 'DEMA', 'TEMA', 'VWMA'], group='策略 5：均线交叉')
MA2_source_5 = input.source(close, '均线2 数据源', group='策略 5：均线交叉')

// * 潜在顶底
str_6 = input.bool(false, '在潜在顶底平仓', group='潜在顶底')
top_qty = input.float(30, '顶部 - 从剩余位置取 x (%)', minval=0.0, maxval=100, step=1, group='潜在顶底')
bottom_qty = input.float(30, '底部 - 从剩余位置取 x (%)', minval=0.0, maxval=100, step=1, group='潜在顶底') 
source_6_top = input.source(close, '以前的TP-TOP？', group='潜在顶底')
source_6_bottom = input.source(close, '以前的 TP-BOTTOM?', group='潜在顶底')
long_trail_perc = input.float(150, '多头成交量追踪(%)', minval=0.0, step=1, group='潜在顶底') * 0.01
short_trail_perc = input.float(150, '空头成交量追踪(%)', minval=0.0, step=1, group='潜在顶底') * 0.01

// * 标志
FLAG_SIGNALS = input.bool(true, '显示买入/卖出信号?', group='其他')
FLAG_SHADOWS = input.bool(true, '显示阴影满意策略 ?', group='其他')

// *************************************************************************************************************************************************************************************************************************************************************************
// 缩写
// *************************************************************************************************************************************************************************************************************************************************************************
// TP: 止盈
// SL: 止损
// *************************************************************************************************************************************************************************************************************************************************************************
// 全局变量
// *************************************************************************************************************************************************************************************************************************************************************************

var FLAG_FIRST = false
var price_stop_long = 0.
var price_stop_short = 0.
var profit_qty = 0. // 每个 TP 从未平仓头寸平仓的数量
var profit_perc = 0. // 自开仓或最后一个目标以来止盈的百分比
var nextTP = 0. // 止盈的下一个目标
var since_entry = 0 // 自开仓最后一个位置以来的柱数
var since_close = 0 // 自收盘或 TP/STOP 最后位置以来的柱数

// * 计算利润数量和利润百分比
if strategy.position_size > 0
    profit_qty := long_profit_qty
    profit_perc := long_profit_perc
else if strategy.position_size < 0
    profit_qty := short_profit_qty
    profit_perc := short_profit_perc
else
    nextTP := 0. // 下一个获利目标（市场外）


// *************************************************************************************************************************************************************************************************************************************************************************
// 函数
// *************************************************************************************************************************************************************************************************************************************************************************
// * 均线类型
// *************************************************************************************************************************************************************************************************************************************************************************
ma(MAType, MASource, MAPeriod) =>
    if MAType == 'SMA'
        ta.sma(MASource, MAPeriod)
    else if MAType == 'EMA'
        ta.ema(MASource, MAPeriod)
    else if MAType == 'WMA'
        ta.wma(MASource, MAPeriod)
    else if MAType == 'RMA'
        ta.rma(MASource, MAPeriod)
    else if MAType == 'HMA'
        ta.wma(2 * ta.wma(MASource, MAPeriod / 2) - ta.wma(MASource, MAPeriod), math.round(math.sqrt(MAPeriod)))
    else if MAType == 'DEMA'
        e = ta.ema(MASource, MAPeriod)
        2 * e - ta.ema(e, MAPeriod)
    else if MAType == 'TEMA'
        e = ta.ema(MASource, MAPeriod)
        3 * (e - ta.ema(e, MAPeriod)) + ta.ema(ta.ema(e, MAPeriod), MAPeriod)
    else if MAType == 'VWMA'
        ta.vwma(MASource, MAPeriod)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 数字策略
// *************************************************************************************************************************************************************************************************************************************************************************
n_strategies() =>
    var result = 0.
    if str_1
        result := 1.
    if str_2
        result += 1.
    if str_3
        result += 1.
    if str_4
        result += 1.
    if str_5
        result += 1.
// *************************************************************************************************************************************************************************************************************************************************************************
// * 价格止盈
// *************************************************************************************************************************************************************************************************************************************************************************
price_takeProfit(percentage, N) =>
    if strategy.position_size > 0
        strategy.position_avg_price * (1 + N * percentage)
    else
        strategy.position_avg_price * (1 - N * percentage)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 加权值
// *************************************************************************************************************************************************************************************************************************************************************************
weight_values(signal) =>
    if signal
        weight = 1.0
    else
        weight = 0.
// *************************************************************************************************************************************************************************************************************************************************************************
// * 加权总计
// *************************************************************************************************************************************************************************************************************************************************************************
weight_total(signal1, signal2, signal3, signal4, signal5) =>
    weight_str1 * weight_values(signal1) + weight_str2 * weight_values(signal2) + weight_str3 * weight_values(signal3) + weight_str4 * weight_values(signal4) + weight_str5 * weight_values(signal5)

// *************************************************************************************************************************************************************************************************************************************************************************
// * 颜色
// *************************************************************************************************************************************************************************************************************************************************************************
colors(type, value=0) =>
    switch str.lower(type)
        'buy'=> color.new(color.aqua, value)
        'sell' => color.new(color.gray, value)
        'TP' => color.new(color.aqua, value)
        'SL' => color.new(color.gray, value)
        'signal' => color.new(color.orange, value)
        'profit' => color.new(color.teal, value)
        'loss' => color.new(color.red, value)
        'info' => color.new(color.white, value)
        'highlights' => color.new(color.orange, value)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 自上次开仓以来的柱数
// *************************************************************************************************************************************************************************************************************************************************************************
bars_since_entry() =>
    bar_index - strategy.opentrades.entry_bar_index(0)

// *************************************************************************************************************************************************************************************************************************************************************************
// * 自收盘或 TP/STOP 以来的柱数
// *************************************************************************************************************************************************************************************************************************************************************************
bars_since_close() =>
    ta.barssince(ta.change(strategy.closedtrades))

// *************************************************************************************************************************************************************************************************************************************************************************
// 其他全局变量
// *************************************************************************************************************************************************************************************************************************************************************************
// * 计算自上次入场和上次平仓/TP 头寸以来的时间
since_entry := bars_since_entry()
since_close := bars_since_close()
if strategy.opentrades == 0
    since_entry := delay_exit
if strategy.closedtrades == 0
    since_close := delay_exit

// *************************************************************************************************************************************************************************************************************************************************************************
// 策略
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略1：MACD
// *************************************************************************************************************************************************************************************************************************************************************************
MA1 = ma(MA1_type_1, MA1_source_1, MA1_period_1)
MA2 = ma(MA2_type_1, MA2_source_1, MA2_period_1)

MACD = MA1 - MA2
signal = ma('SMA', MACD, 9)
trend= MACD - signal

long = MACD > signal
short = MACD < signal
proportion = math.abs(MACD / signal)

// * 条件
long_signal1 = long and long[delay_macd - 1] and not long[delay_macd]
short_signal1 = short and short[delay_macd - 1] and not short[delay_macd]
close_long1 = short and not long[delay_macd]
close_short1 = long and not short[delay_macd]

// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略2：Stoch RSI 超卖/超买
// *************************************************************************************************************************************************************************************************************************************************************************
rsi = ta.rsi(close, length_RSI)
srsi = ta.stoch(rsi, rsi, rsi, length_stoch)
k = ma('SMA', srsi, smoothK)
isRsiOB = k >= long_RSI
isRsiOS = k <= short_RSI
// * 条件
long_signal2 = isRsiOS[delay_srsi] and not isRsiOB and since_entry >= delay_exit and since_close >= delay_exit
short_signal2 = isRsiOB[delay_srsi] and not isRsiOS and since_entry >= delay_exit and since_close >= delay_exit
close_long2 = short_signal2
close_short2 = long_signal2

// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略 3：RSI
// *************************************************************************************************************************************************************************************************************************************************************************
isRsiOB2 = rsi >= long_RSI2
isRsiOS2 = rsi <= short_RSI2
// * 条件
long_signal3 = isRsiOS2[delay_rsi] and not isRsiOB2 and since_entry >= delay_exit and since_close >= delay_exit
short_signal3 = isRsiOB2[delay_rsi] and not isRsiOS2 and since_entry >= delay_exit and since_close >= delay_exit
close_long3 = short_signal3
close_short3 = long_signal3

// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略4：超级趋势
// *************************************************************************************************************************************************************************************************************************************************************************
atr2 = ma('SMA', ta.tr, periods_4)
atr = change_ATR ? ta.atr(periods_4) : atr2
up = source_4 - multiplier * atr
up1 = nz(up[1], up)
up := close[1] > up1 ? math.max(up, up1) : up

dn = source_4 + multiplier * atr
dn1 = nz(dn[1], dn)
dn := close[1] < dn1 ? math.min(dn, dn1) : dn

trend := 1
trend := nz(trend[1], trend)
trend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend

// * 条件
long4 = trend == 1
short4 = trend == -1
long_signal4 = trend == 1 and trend[delay_super - 1] == 1 and trend[delay_super] == -1
short_signal4 = trend == -1 and trend[delay_super - 1] == -1 and trend[delay_super] == 1
changeCond = trend != trend[1]
close_long4 = short_signal4
close_short4 = short_signal4

// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略 5：均线交叉
// *************************************************************************************************************************************************************************************************************************************************************************
MA12 = ma(MA1_type_5, MA1_source_5, MA1_period_5)
MA22 = ma(MA2_type_5, MA2_source_5, MA2_period_5)

long5 = MA12 > MA22
short5 = MA12 < MA22

// * 条件
long_signal5 = long5 and long5[delay_cross - 1] and not long5[delay_cross]
short_signal5 = short5 and short5[delay_cross - 1] and not short5[delay_cross]
close_long5 = short5 and not long5[delay_cross]
close_short5 = long5 and not short5[delay_cross]

// *************************************************************************************************************************************************************************************************************************************************************************
// * STRATEGY 6: 潜在顶底
// *************************************************************************************************************************************************************************************************************************************************************************
// * 结合 RSI、Stoch RSI、MACD、成交量和加权策略来检测潜在顶底区域
volumeRSI_condition = volume[2] > volume[3] and volume[2] > volume[4] and volume[2] > volume[5]
condition_OB1 = isRsiOB2 and (isRsiOB or volume < ma('SMA', volume, 20) / 2) and volumeRSI_condition
condition_OS1 = isRsiOS2 and (isRsiOS or volume < ma('SMA', volume, 20) / 2) and volumeRSI_condition

condition_OB2 = volume[2] / volume[1] > (1.0 + long_trail_perc) and isRsiOB and volumeRSI_condition
condition_OS2 = volume[2] / volume[1] > (1.0 + short_trail_perc) and isRsiOS and volumeRSI_condition

condition_OB3 = weight_total(MACD < signal, isRsiOB, isRsiOB2, short4, short5) >= weight_trigger
condition_OS3 = weight_total(MACD > signal, isRsiOS, isRsiOS2, long4, long5) >= weight_trigger

condition_OB = (condition_OB1 or condition_OB2)
condition_OS = (condition_OS1 or condition_OS2)
condition_OB_several = condition_OB[1] and condition_OB[2] or condition_OB[1] and condition_OB[3] or condition_OB[1] and condition_OB[4] or condition_OB[1] and condition_OB[5] or condition_OB[1] and condition_OB[6] or condition_OB[1] and condition_OB[7] 
condition_OS_several = condition_OS[1] and condition_OS[2] or condition_OS[1] and condition_OS[3] or condition_OS[1] and condition_OS[4] or condition_OS[1] and condition_OS[5] or condition_OS[1] and condition_OS[6] or condition_OS[1] and condition_OS[7] 



// *************************************************************************************************************************************************************************************************************************************************************************
// 3commas  api 消息初始化
// *************************************************************************************************************************************************************************************************************************************************************************
//开仓平仓消息
botidlong=botidlong_all
emailtokenlong=emailtokenlong_all
botidshort=botidshort_all
emailtokenshort=emailtokenshort_all

string textlongentry = '{' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidlong +',' + '\n' + '  "email_token": "' + emailtokenlong +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'
string textlongexit = '{' + '\n' + '  "action": "close_at_market_price",' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id":  ' + botidlong +',' + '\n' + '  "email_token": "' + emailtokenlong +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'
string textshortentry = '{' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidshort +',' + '\n' + '  "email_token": "' + emailtokenshort +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'
string textshortexit = '{' + '\n' + '  "action": "close_at_market_price",' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidshort +',' + '\n' + '  "email_token": "' + emailtokenshort +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'


//部分平仓与仓位重置
//部分平多
string textshortentry_part = '{' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidshort_part +',' + '\n' + '  "email_token": "' + emailtokenshort_part +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'

//部分平空
string textlongentry_part = '{' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidlong_part +',' + '\n' + '  "email_token": "' + emailtokenshort_part +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'

//重置仓位
string textlongecancel_part = '{' + '\n' + '  "action": "cancel",' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id":  ' + botidlong_part +',' + '\n' + '  "email_token": "' + emailtokenlong_part +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'
string textshortcancel_part = '{' + '\n' + '  "action": "cancel",' + '\n' + '  "message_type": "bot",' + '\n' + '  "bot_id": ' + botidshort_part +',' + '\n' + '  "email_token": "' + emailtokenshort_part +'",' + '\n' + '  "delay_seconds": 0,' + '\n' + '  "pair": "USDT_' + targettrick +'"' + '\n' + '}'


// * 警报
//全部开仓
alarm_label_long = textlongentry
alarm_label_short = textshortentry

//全部平仓
alarm_label_close_long = textlongexit
alarm_label_close_short = textshortexit

//部分平多
alarm_label_TP_long = textshortentry_part
alarm_label_SL_long = textshortentry_part

//部分平空
alarm_label_TP_short = textlongentry_part
alarm_label_SL_short = textlongentry_part



//如果之前部分平仓过了，重置辅助机器人的状态
if strategy.position_size >= 0 and  strategy.position_size > strategy.position_size[1]
    alert(textshortcancel_part, alert.freq_once_per_bar)
if strategy.position_size <= 0 and  strategy.position_size < strategy.position_size[1]
    alert(textlongecancel_part, alert.freq_once_per_bar)

// *************************************************************************************************************************************************************************************************************************************************************************
// * 设置警报 TP 消息
// *************************************************************************************************************************************************************************************************************************************************************************
set_alarm_label_TP() =>
    if strategy.position_size > 0
        alarm_label_TP_long
    else if strategy.position_size < 0
        alarm_label_TP_short 

// *************************************************************************************************************************************************************************************************************************************************************************
// 策略开仓与平仓
// *************************************************************************************************************************************************************************************************************************************************************************
if time >= start and time <= end
    // ***************************************************************************************************************************************************************************
    // * Set Entries
    // ***************************************************************************************************************************************************************************
    if str_0
        if not str_1
            weight_str1 := 0
        if not str_2
            weight_str2 := 0
        if not str_3
            weight_str3 := 0
        if not str_4
            weight_str4 := 0
        if not str_5
            weight_str5 := 0
        if allow_shorts == true
            w_total = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
            if w_total >= weight_trigger
                strategy.entry('Short', strategy.short, alert_message=alarm_label_short)
        if allow_longs == true
            w_total = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
            if w_total >= weight_trigger
                strategy.entry('Long', strategy.long, alert_message=alarm_label_long)
    else
        if allow_shorts == true
            if str_1
                strategy.entry('Short', strategy.short, when=short_signal1, alert_message=alarm_label_short)
            if str_2
                strategy.entry('Short', strategy.short, when=short_signal2, alert_message=alarm_label_short)
            if str_3
                strategy.entry('Short', strategy.short, when=short_signal3, alert_message=alarm_label_short)
            if str_4
                strategy.entry('Short', strategy.short, when=short_signal4, alert_message=alarm_label_short)
            if str_5
                strategy.entry('Short', strategy.short, when=short_signal5, alert_message=alarm_label_short)
        if allow_longs == true
            if str_1
                strategy.entry('Long', strategy.long, when=long_signal1, alert_message=alarm_label_long)
            if str_2
                strategy.entry('Long', strategy.long, when=long_signal2, alert_message=alarm_label_long)
            if str_3
                strategy.entry('Long', strategy.long, when=long_signal3, alert_message=alarm_label_long)
            if str_4
                strategy.entry('Long', strategy.long, when=long_signal4, alert_message=alarm_label_long)
            if str_5
                strategy.entry('Long', strategy.long, when=long_signal5, alert_message=alarm_label_long)

    // ***************************************************************************************************************************************************************************
    // * 设置止盈
    // ***************************************************************************************************************************************************************************
    if strategy.position_size != 0 and take_profits and since_entry == 0
        for i = 1 to MAX_TP
            id = 'TP ' + str.tostring(i)
            strategy.exit(id=id, limit=price_takeProfit(profit_perc, i), qty_percent=profit_qty, comment=id, alert_message=set_alarm_label_TP())

    // ***************************************************************************************************************************************************************************
    // * 设置止损
    // ***************************************************************************************************************************************************************************
    if strategy.position_size > 0
        if since_close == 0
            if high > price_takeProfit(profit_perc, 6) and MAX_TP >= 6
                n = 6
                nextTP := na
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_long := price_takeProfit(profit_perc, n-1)
                else if     movestoploss == 'TP-2'
                    price_stop_long := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_long := price_takeProfit(profit_perc, n-3)
            else if high > price_takeProfit(profit_perc, 5) and MAX_TP >= 5
                n = 5
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_long := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_long := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_long := price_takeProfit(profit_perc, n-3)
            else if high > price_takeProfit(profit_perc, 4) and MAX_TP >= 4
                n = 4
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_long := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_long := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_long := price_takeProfit(profit_perc, n-3)
            else if high > price_takeProfit(profit_perc, 3) and MAX_TP >= 3
                n = 3
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_long := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_long := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
            else if high > price_takeProfit(profit_perc, 2) and MAX_TP >= 2
                n = 2
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_long := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
            else if high > price_takeProfit(profit_perc, 1) and MAX_TP >= 1
                n = 1
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_long := strategy.position_avg_price * (1 + n*profit_perc - stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
                else if movestoploss == 'TP-2' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_long := strategy.position_avg_price
        if since_entry == 0
            n = 0
            nextTP := price_takeProfit(profit_perc, n + 1)
            price_stop_long := strategy.position_avg_price * (1 - stoploss_perc) 
    if strategy.position_size < 0
        if since_close == 0
            if low < price_takeProfit(profit_perc, 6) and MAX_TP >= 6
                n = 6
                nextTP := na
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_short := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_short := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_short := price_takeProfit(profit_perc, n-3)
            else if low < price_takeProfit(profit_perc, 5) and MAX_TP >= 5
                n = 5
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_short := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_short := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_short := price_takeProfit(profit_perc, n-3)
            else if low < price_takeProfit(profit_perc, 4) and MAX_TP >= 4
                n = 4
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_short := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_short := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3'
                    price_stop_short := price_takeProfit(profit_perc, n-3)
            else if low < price_takeProfit(profit_perc, 3) and MAX_TP >= 3
                n = 3
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_short := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2'
                    price_stop_short := price_takeProfit(profit_perc, n-2)
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
            else if low < price_takeProfit(profit_perc, 2) and MAX_TP >= 2
                n = 2
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1'
                    price_stop_short := price_takeProfit(profit_perc, n-1)
                else if movestoploss == 'TP-2' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
            else if low < price_takeProfit(profit_perc, 1) and MAX_TP >= 1
                n = 1 
                nextTP := price_takeProfit(profit_perc, n + 1)
                if movestoploss == 'Percentage'
                    price_stop_short := strategy.position_avg_price * (1 - n*profit_perc + stoploss_perc * move_stoploss_factor)
                else if movestoploss == 'TP-1' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
                else if movestoploss == 'TP-2' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
                else if movestoploss == 'TP-3' and movestoploss_entry
                    price_stop_short := strategy.position_avg_price
        if since_entry == 0
            n = 0
            nextTP := price_takeProfit(profit_perc, n + 1)
            price_stop_short := strategy.position_avg_price * (1 + stoploss_perc)

    // ***************************************************************************************************************************************************************************
    // * 设置出口
    // ***************************************************************************************************************************************************************************
    if allow_longs == true and allow_shorts == false
        if str_0
            w_total = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
            strategy.close('Long', when=w_total>=weight_trigger, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
        else
            if str_1
                strategy.close('Long', when=close_long1, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
            if str_2
                strategy.close('Long', when=close_long2, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
            if str_3
                strategy.close('Long', when=close_long3, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
            if str_4
                strategy.close('Long', when=close_long4, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
            if str_5
                strategy.close('Long', when=close_long5, qty_percent=100, comment='SHORT', alert_message=alarm_label_close_long)
    if allow_longs == false and allow_shorts == true
        if str_0
            w_total = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
            strategy.close('Short', when=w_total>=weight_trigger, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
        else
            if str_1
                strategy.close('Short', when=close_long1, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
            if str_2
                strategy.close('Short', when=close_long2, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
            if str_3
                strategy.close('Short', when=close_long3, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
            if str_4
                strategy.close('Short', when=close_long4, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
            if str_5
                strategy.close('Short', when=close_long5, qty_percent=100, comment='LONG', alert_message=alarm_label_close_short)
    if allow_shorts == true and strategy.position_size < 0 and stoploss and since_entry > 0
        strategy.close('Short', when=stop_source >= price_stop_short, qty_percent=100, comment='STOP', alert_message=alarm_label_close_short)
        if str_6
            if top_qty == 100
                strategy.close('Short', when=condition_OS_several, qty_percent=bottom_qty, comment='STOP', alert_message=alarm_label_SL_short)
            else    
                strategy.exit('Short', when=condition_OS_several, limit=source_6_bottom[1], qty_percent=bottom_qty, comment='TP-B', alert_message=set_alarm_label_TP())
    if allow_longs == true and strategy.position_size > 0 and stoploss and since_entry > 0
        strategy.close('Long', when=stop_source <= price_stop_long, qty_percent=100, comment='STOP', alert_message=alarm_label_close_long)
        if str_6
            if top_qty == 100
                strategy.close('Long', when=condition_OB_several, qty_percent=top_qty, comment='STOP', alert_message=alarm_label_SL_long)
            else
                strategy.exit('Long', when=condition_OB_several, limit=source_6_top[1], qty_percent=top_qty, comment='TP-T', alert_message=set_alarm_label_TP())

// *************************************************************************************************************************************************************************************************************************************************************************
// * 数据窗口 - 调试
// *************************************************************************************************************************************************************************************************************************************************************************
price_stop = strategy.position_size > 0 ? price_stop_long : price_stop_short

plotchar(volume[2] / volume[1], "Volume 2 / Volume 1", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(since_entry, "Since entry [bars]", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(since_close, "Since close/TP [bars]", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(strategy.position_avg_price, "Average position price", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(strategy.position_size, "Position size", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(nextTP, "Next TP target", "", location.top, size = size.tiny, color=color.new(color.teal, 0))
plotchar(price_stop, "STOP Price", "", location.top, size = size.tiny, color=color.new(color.gray, 0))
plotchar(strategy.opentrades, "Open trades", "", location.top, size = size.tiny, color=strategy.position_size > 0 ? color.blue : color.gray)
plotchar(strategy.netprofit, "Net profit [$]", "", location.top, size = size.tiny, color=strategy.netprofit > 0 ? color.blue : color.gray)
plotchar(strategy.grossprofit, "Gross profit [$]", "", location.top, size = size.tiny, color=color.blue) 
plotchar(strategy.grossloss, "Gross loss [$]", "", location.top, size = size.tiny, color=color.gray) 
plotchar(strategy.openprofit, "Unrealized P&L [$]", "", location.top, size = size.tiny, color=strategy.openprofit > 0 ? color.blue : color.gray)
plotchar(strategy.closedtrades, "Closed trades", "", location.top, size = size.tiny, color=color.orange) 
plotchar(strategy.wintrades/strategy.closedtrades*100, "Winrate [%]", "", location.top, size = size.tiny, color=strategy.wintrades/strategy.closedtrades > 60 ? color.blue : color.gray) 

// *************************************************************************************************************************************************************************************************************************************************************************
// PLOTS
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略1：MACD
// *************************************************************************************************************************************************************************************************************************************************************************
plot(trend, 'Trend', style=plot.style_columns, color=MACD > signal ? color.new(color.teal, 30) : color.new(color.gray, 30), display=display.none)
plot(MACD, 'MACD', color=color.new(color.blue, 0), display=display.none)
plot(signal, 'Signal', color=color.new(color.orange, 0), display=display.none)
plotshape(long_signal1 and FLAG_SIGNALS ? up : na, 'Buy MACD', text='MACD', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
plotshape(short_signal1 and FLAG_SIGNALS ? dn : na, 'Sell MACD', text='MACD', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略2：Stoch RSI 超卖/超买
// *************************************************************************************************************************************************************************************************************************************************************************
plotshape(long_signal2 and FLAG_SIGNALS ? up : na, title='Buy Stoch RSI', text='SRSI', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
plotshape(short_signal2 and FLAG_SIGNALS ? dn : na, title='Sell Stoch RSI', text='SRSI', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略 3：RSI
// *************************************************************************************************************************************************************************************************************************************************************************
plotshape(long_signal3 and FLAG_SIGNALS ? up : na, title='Buy RSI', text='RSI', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
plotshape(short_signal3 and FLAG_SIGNALS ? dn : na, title='Sell RSI', text='RSI', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略4：超级趋势
// *************************************************************************************************************************************************************************************************************************************************************************
plotshape(long_signal4 and FLAG_SIGNALS ? up : na, title='Buy Supertrend', text='Supertrend', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
plotshape(short_signal4 and FLAG_SIGNALS ? dn : na, title='Sell Supertrend', text='Supertrend', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
// *************************************************************************************************************************************************************************************************************************************************************************
// * 策略 5：均线交叉
// *************************************************************************************************************************************************************************************************************************************************************************
plotshape(long_signal5 and FLAG_SIGNALS ? up : na, title='Buy MA CROSS', text='MA CROSS', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0), display=display.none)
plotshape(short_signal5 and FLAG_SIGNALS ? dn : na, title='Sell MA CROSS', text='MA CROSS', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0), display=display.none)
// *************************************************************************************************************************************************************************************************************************************************************************
// * STRATEGY 6: 潜在顶底
// *************************************************************************************************************************************************************************************************************************************************************************
plotshape(condition_OB_several ? dn : na, title='Top', text='T', location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
plotshape(condition_OS_several ? up : na, title='Bottom', text='B', location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
// *************************************************************************************************************************************************************************************************************************************************************************
// * 买卖信号
// *************************************************************************************************************************************************************************************************************************************************************************
w_total_long = weight_total(long_signal1, long_signal2, long_signal3, long_signal4, long_signal5)
w_total_short = weight_total(short_signal1, short_signal2, short_signal3, short_signal4, short_signal5)
plotshape(w_total_long >= weight_trigger and FLAG_SIGNALS ? up : na, title='Buy Weigthed strategy', text='Buy', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.teal, 0), textcolor=color.new(color.white, 0))
plotshape(w_total_short >= weight_trigger and FLAG_SIGNALS ? dn : na, title='Sell Weigthed strategy', text='Sell', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.gray, 0), textcolor=color.new(color.white, 0))
// *************************************************************************************************************************************************************************************************************************************************************************
// * 止损 目标
// *************************************************************************************************************************************************************************************************************************************************************************
plot(series=(strategy.position_size > 0) ? price_stop_long : na, color=color.new(color.gray, 30), style=plot.style_cross, linewidth=2, title="Long 止损")
plot(series=(strategy.position_size < 0) ? price_stop_short : na, color=color.new(color.gray, 30), style=plot.style_cross, linewidth=2, title="Short 止损")
// *************************************************************************************************************************************************************************************************************************************************************************
// * 止盈目标
// *************************************************************************************************************************************************************************************************************************************************************************
plot(strategy.position_size > 0 or strategy.position_size < 0 ? nextTP : na, color=color.new(color.aqua, 30), style=plot.style_cross, linewidth=2, title="Next TP")
// *************************************************************************************************************************************************************************************************************************************************************************
// * 所有策略
// *************************************************************************************************************************************************************************************************************************************************************************
mPlot = plot(ohlc4, title='Price ohlc4', style=plot.style_circles, linewidth=0, display=display.none)
upPlot = plot((long_signal1 or long_signal2 or long_signal3 or long_signal4 or long_signal5) and (w_total_long > w_total_short) ? up : na, title='Up Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.aqua, 0), display=display.none)
dnPlot = plot((short_signal1 or short_signal2 or short_signal3 or short_signal4 or short_signal5) and (w_total_short > w_total_long) ? dn : na, title='Down Trend', style=plot.style_linebr, linewidth=2, color=color.new(color.gray, 0), display=display.none)
plotchar(weight_trigger, "Trigger strategies", "", location.top, size = size.tiny, color=color.new(color.orange, 0))
plotchar(w_total_long, "Satisfied Long strategies", "", location.top, size = size.tiny, color=w_total_long >= weight_trigger ? color.orange : color.gray)
plotchar(w_total_short, "Satisfied Short strategies", "", location.top, size = size.tiny, color=w_total_long >= weight_trigger ? color.orange : color.gray)
plotshape((long_signal1 or long_signal2 or long_signal3 or long_signal4 or long_signal5) and (w_total_long > w_total_short) ? up : na, title='UpTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.aqua, 0), display=display.none)
plotshape((short_signal1 or short_signal2 or short_signal3 or short_signal4 or short_signal5) and (w_total_short > w_total_long) ? dn : na, title='DownTrend Begins', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.gray, 0), display=display.none)
fill(mPlot, upPlot, title='UpTrend Highligter', color=colors('buy', FLAG_SHADOWS ? 80:100))
fill(mPlot, dnPlot, title='DownTrend Highligter', color=colors('sell', FLAG_SHADOWS ? 80:100))


// *************************************************************************************************************************************************************************************************************************************************************************
// 月表表现 - 由 @QuantNomad 开发
// *************************************************************************************************************************************************************************************************************************************************************************
show_performance = input.bool(true, 'Show Monthly Performance ?', group='Performance - credits: @QuantNomad')
prec = input(2, 'Return Precision', group='Performance - credits: @QuantNomad')

if show_performance
    new_month = month(time) != month(time[1])
    new_year  = year(time)  != year(time[1])
    
    eq = strategy.equity
    
    bar_pnl = eq / eq[1] - 1
    
    cur_month_pnl = 0.0
    cur_year_pnl  = 0.0
    
    // Current Monthly P&L
    cur_month_pnl := new_month ? 0.0 : 
                     (1 + cur_month_pnl[1]) * (1 + bar_pnl) - 1 
    
    // Current Yearly P&L
    cur_year_pnl := new_year ? 0.0 : 
                     (1 + cur_year_pnl[1]) * (1 + bar_pnl) - 1  
    
    // Arrays to store Yearly and Monthly P&Ls
    var month_pnl  = array.new_float(0)
    var month_time = array.new_int(0)
    
    var year_pnl  = array.new_float(0)
    var year_time = array.new_int(0)
    
    last_computed = false
    
    if (not na(cur_month_pnl[1]) and (new_month or barstate.islastconfirmedhistory))
        if (last_computed[1])
            array.pop(month_pnl)
            array.pop(month_time)
            
        array.push(month_pnl , cur_month_pnl[1])
        array.push(month_time, time[1])
    
    if (not na(cur_year_pnl[1]) and (new_year or barstate.islastconfirmedhistory))
        if (last_computed[1])
            array.pop(year_pnl)
            array.pop(year_time)
            
        array.push(year_pnl , cur_year_pnl[1])
        array.push(year_time, time[1])
    
    last_computed := barstate.islastconfirmedhistory ? true : nz(last_computed[1])
    
    // Monthly P&L Table    
    var monthly_table = table(na)
    
    if (barstate.islastconfirmedhistory)
        monthly_table := table.new(position.bottom_right, columns = 14, rows = array.size(year_pnl) + 1, border_width = 1)
    
        table.cell(monthly_table, 0,  0, "",     bgcolor = #cccccc)
        table.cell(monthly_table, 1,  0, "Jan",  bgcolor = #cccccc)
        table.cell(monthly_table, 2,  0, "Feb",  bgcolor = #cccccc)
        table.cell(monthly_table, 3,  0, "Mar",  bgcolor = #cccccc)
        table.cell(monthly_table, 4,  0, "Apr",  bgcolor = #cccccc)
        table.cell(monthly_table, 5,  0, "May",  bgcolor = #cccccc)
        table.cell(monthly_table, 6,  0, "Jun",  bgcolor = #cccccc)
        table.cell(monthly_table, 7,  0, "Jul",  bgcolor = #cccccc)
        table.cell(monthly_table, 8,  0, "Aug",  bgcolor = #cccccc)
        table.cell(monthly_table, 9,  0, "Sep",  bgcolor = #cccccc)
        table.cell(monthly_table, 10, 0, "Oct",  bgcolor = #cccccc)
        table.cell(monthly_table, 11, 0, "Nov",  bgcolor = #cccccc)
        table.cell(monthly_table, 12, 0, "Dec",  bgcolor = #cccccc)
        table.cell(monthly_table, 13, 0, "Year", bgcolor = #999999)
    
    
        for yi = 0 to array.size(year_pnl) - 1
            table.cell(monthly_table, 0,  yi + 1, str.tostring(year(array.get(year_time, yi))), bgcolor = #cccccc)
            
            y_color = array.get(year_pnl, yi) > 0 ? color.new(color.teal, transp = 40) : color.new(color.gray, transp = 40)
            table.cell(monthly_table, 13, yi + 1, str.tostring(math.round(array.get(year_pnl, yi) * 100, prec)), bgcolor = y_color, text_color=color.new(color.white, 0))
            
        for mi = 0 to array.size(month_time) - 1
            m_row   = year(array.get(month_time, mi))  - year(array.get(year_time, 0)) + 1
            m_col   = month(array.get(month_time, mi)) 
            m_color = array.get(month_pnl, mi) > 0 ? color.new(color.teal, transp = 40) : color.new(color.gray, transp = 40)
            
            table.cell(monthly_table, m_col, m_row, str.tostring(math.round(array.get(month_pnl, mi) * 100, prec)), bgcolor = m_color, text_color=color.new(color.white, 0))