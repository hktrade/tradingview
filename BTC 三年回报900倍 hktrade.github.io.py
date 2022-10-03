// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/

// © wielkieef



//@version=5

strategy('三年回报9000%的策略', overlay=true, pyramiding=1, initial_capital=10, default_qty_type=strategy.cash, default_qty_value=10, calc_on_order_fills=false, slippage=0, commission_type=strategy.commission.percent, commission_value=0.04)




long_               =                   input(true,                             title="Longs",                                                                                                                              group= "BACKTEST")
short_              =                   input(true,                             title="Shorts",                                                                                                                             group= "BACKTEST")


config_FromDay = '2021-01-01T00:00:00'
config_ToDay = '2025-01-01T00:00:00'
starttime = input.time(defval = timestamp(config_FromDay), title = "开始时间")
finishtime = input.time(defval = timestamp(config_ToDay), title = "结束时间")
window()  => time >= starttime and time <= finishtime ? true : false       





//订单当前信息
var table perfTable = table.new(position.top_center, 1, 200, border_width=2, bgcolor = color.new(color.white,100), frame_width = 5, frame_color =color.new(color.lime,50))  
table.cell(perfTable, 0, 2, 'curent position size : ' + str.tostring(strategy.position_size))




//SOURCE ==================================================================================================================================================================================================================================================================



src = input(close)



// INPUTS ==================================================================================================================================================================================================================================================================



//ADX -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Act_ADX = input(true, title='AVERAGE DIRECTIONAL INDEX')

ADX_options = input.string('MASANAKAMURA', title='ADX OPTION', options=['CLASSIC', 'MASANAKAMURA'])

ADX_len = input.int(14, title='ADX LENGTH', minval=1)

th = input.float(15.5, title='ADX THRESHOLD', minval=0, step=0.5)



//Range Filter----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



length0 = input(6, title='Range Filter lenght')

mult = input(4, title='Range Filter mult')



//SAR-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



start = input.float(title='SAR Start', step=0.001, defval=0.046)

increment = input.float(title='SAR Increment', step=0.001, defval=0.02)

maximum = input.float(title='SAR Maximum', step=0.01, defval=0.11)

width = input.int(title='SAR Point Width', minval=1, defval=1)



//RSI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



len_3 = input.int(131, minval=1, title='RSI lenght')

src_3 = input(hl2, 'RSI Source')



//TWAP Trend --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



smoothing = input(title='TWAP Smoothing', defval=11)

resolution = input('0', 'TWAP Timeframe')



//JMA------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



inp = input(title='JMA Source', defval=hlc3)

reso = input.timeframe(title='JMA Resolution', defval='')

rep = input(title='JMA Allow Repainting?', defval=false)

src0 = request.security(syminfo.tickerid, reso, inp[rep ? 0 : barstate.isrealtime ? 1 : 0])[rep ? 0 : barstate.isrealtime ? 0 : 1]

lengths = input.int(title='JMA Length', defval=8, minval=1)



//MACD------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



fast_length = input(title='MACD Fast Length', defval=5)

slow_length = input(title='MACD Slow Length', defval=21)

signal_length = input.int(title='MACD Signal Smoothing', minval=1, maxval=50, defval=31)



//Volume Delta -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



periodMa = input.int(title='Delta Length', minval=1, defval=16)



//Volume weight------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



maLength = input.int(title='Volume Weight Length', defval=59, minval=1)

maType = input.string(title='Volume Weight Type', defval='SMA', options=['EMA', 'SMA', 'HMA', 'WMA', 'DEMA'])

rvolTrigger = input.float(title='Volume To Trigger Signal', defval=1.1, step=0.1, minval=0.1)



//MA----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



length = input.int(50, minval=1, title='MA Length')

matype = input.int(5, minval=1, maxval=5, title='AvgType')



//INDICATORS ==============================================================================================================================================================================================================================================================



//ADX----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



calcADX(_len) =>

    up = ta.change(high)

    down = -ta.change(low)

    plusDM = na(up) ? na : up > down and up > 0 ? up : 0

    minusDM = na(down) ? na : down > up and down > 0 ? down : 0

    truerange = ta.rma(ta.tr, _len)

    _plus = fixnan(100 * ta.rma(plusDM, _len) / truerange)

    _minus = fixnan(100 * ta.rma(minusDM, _len) / truerange)

    sum = _plus + _minus

    _adx = 100 * ta.rma(math.abs(_plus - _minus) / (sum == 0 ? 1 : sum), _len)

    [_plus, _minus, _adx]



calcADX_Masanakamura(_len) =>

    SmoothedTrueRange = 0.0

    SmoothedDirectionalMovementPlus = 0.0

    SmoothedDirectionalMovementMinus = 0.0

    TrueRange = math.max(math.max(high - low, math.abs(high - nz(close[1]))), math.abs(low - nz(close[1])))

    DirectionalMovementPlus = high - nz(high[1]) > nz(low[1]) - low ? math.max(high - nz(high[1]), 0) : 0

    DirectionalMovementMinus = nz(low[1]) - low > high - nz(high[1]) ? math.max(nz(low[1]) - low, 0) : 0

    SmoothedTrueRange := nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1]) / _len + TrueRange

    SmoothedDirectionalMovementPlus := nz(SmoothedDirectionalMovementPlus[1]) - nz(SmoothedDirectionalMovementPlus[1]) / _len + DirectionalMovementPlus

    SmoothedDirectionalMovementMinus := nz(SmoothedDirectionalMovementMinus[1]) - nz(SmoothedDirectionalMovementMinus[1]) / _len + DirectionalMovementMinus

    DIP = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100

    DIM = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100

    DX = math.abs(DIP - DIM) / (DIP + DIM) * 100

    adx = ta.sma(DX, _len)

    [DIP, DIM, adx]



[DIPlusC, DIMinusC, ADXC] = calcADX(ADX_len)

[DIPlusM, DIMinusM, ADXM] = calcADX_Masanakamura(ADX_len)

DIPlus = ADX_options == 'CLASSIC' ? DIPlusC : DIPlusM

DIMinus = ADX_options == 'CLASSIC' ? DIMinusC : DIMinusM

ADX = ADX_options == 'CLASSIC' ? ADXC : ADXM



ADX_color = DIPlus > DIMinus and ADX > th ? color.green : DIPlus < DIMinus and ADX > th ? color.red : color.orange

barcolor(color=Act_ADX ? ADX_color : na, title='ADX')



//Range Filter---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



out = 0.

cma = 0.

cts = 0.

Var = ta.variance(src, length0) * mult

sma = ta.sma(src, length0)



secma = math.pow(nz(sma - cma[1]), 2)

sects = math.pow(nz(src - cts[1]), 2)

ka = Var < secma ? 1 - Var / secma : 0

kb = Var < sects ? 1 - Var / sects : 0



cma := ka * sma + (1 - ka) * nz(cma[1], src)

cts := kb * src + (1 - kb) * nz(cts[1], src)



css = cts > cma ? color.green : color.red

a = plot(cts, 'CTS', color.new(color.gray, 0), 2)

b = plot(cma, 'CMA', color.new(color.gray, 0), 2)

fill(a, b, color=css, transp=80)



rangegood = cts > cma

rangebad = cts < cma



//SAR-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



psar = ta.sar(start, increment, maximum)

dir = psar < close ? 1 : -1



psarColor = dir == 1 ? color.green : color.red

psarPlot = plot(psar, title='PSAR', style=plot.style_circles, linewidth=width, color=psarColor, transp=0)



var color longColor = color.green

var color shortColor = color.red



sargood = dir == 1

sarbad = dir == -1



//RSI---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



up_3 = ta.rma(math.max(ta.change(src_3), 0), len_3)

down_3 = ta.rma(-math.min(ta.change(src_3), 0), len_3)

rsi_3 = down_3 == 0 ? 100 : up_3 == 0 ? 0 : 100 - 100 / (1 + up_3 / down_3)



rsiob = rsi_3 < 70

rsios = rsi_3 > 30



//TWAP Trend --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



res = resolution != '0' ? resolution : timeframe.period

weight = ta.barssince(ta.change(request.security(syminfo.tickerid, res, time, lookahead=barmerge.lookahead_on)))

price = 0.

price := weight == 0 ? src : src + nz(price[1])

twap = price / (weight + 1)

ma_ = smoothing < 2 ? twap : ta.sma(twap, smoothing)

bullish = smoothing < 2 ? src >= ma_ : src > ma_

disposition = bullish ? color.lime : color.red

basis = plot(src, 'OHLC4', disposition, linewidth=1, transp=100)

work = plot(ma_, 'TWAP', disposition, linewidth=2, transp=20)

fill(basis, work, disposition, transp=65)



//JMA------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



jsa = (src0 + src0[lengths]) / 2

sig = src0 > jsa ? 1 : src0 < jsa ? -1 : 0



jsaColor = sig > 0 ? color.green : sig < 0 ? color.red : color.orange

plot(jsa, color=jsaColor, linewidth=2)



jmagood = sig > 0

jmabad = sig < 0



//MACD------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



fast_ma = ta.ema(src, fast_length)

slow_ma = ta.ema(src, slow_length)

macd = fast_ma - slow_ma

signal = ta.sma(macd, signal_length)



macdgood = macd > signal

macdbad = macd < signal



//Volume Delta -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



iff_1 = close[1] < open ? math.max(high - close[1], close - low) : math.max(high - open, close - low)

iff_2 = close[1] > open ? high - low : math.max(open - close[1], high - low)

iff_3 = close[1] < open ? math.max(high - close[1], close - low) : high - open

iff_4 = close[1] > open ? high - low : math.max(open - close[1], high - low)

iff_5 = close[1] < open ? math.max(open - close[1], high - low) : high - low

iff_6 = close[1] > open ? math.max(high - open, close - low) : iff_5

iff_7 = high - close < close - low ? iff_4 : iff_6

iff_8 = high - close > close - low ? iff_3 : iff_7

iff_9 = close > open ? iff_2 : iff_8

bullPower = close < open ? iff_1 : iff_9

iff_10 = close[1] > open ? math.max(close[1] - open, high - low) : high - low

iff_11 = close[1] > open ? math.max(close[1] - low, high - close) : math.max(open - low, high - close)

iff_12 = close[1] > open ? math.max(close[1] - open, high - low) : high - low

iff_13 = close[1] > open ? math.max(close[1] - low, high - close) : open - low

iff_14 = close[1] < open ? math.max(open - low, high - close) : high - low

iff_15 = close[1] > open ? math.max(close[1] - open, high - low) : iff_14

iff_16 = high - close < close - low ? iff_13 : iff_15

iff_17 = high - close > close - low ? iff_12 : iff_16

iff_18 = close > open ? iff_11 : iff_17

bearPower = close < open ? iff_10 : iff_18



bullVolume = bullPower / (bullPower + bearPower) * volume

bearVolume = bearPower / (bullPower + bearPower) * volume



delta = bullVolume - bearVolume

cvd = ta.cum(delta)

cvdMa = ta.sma(cvd, periodMa)



deltagood = cvd > cvdMa

deltabad = cvd < cvdMa



//Volume weight------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



getMA0(length) =>

    maPrice = ta.ema(volume, length)

    if maType == 'SMA'

        maPrice := ta.sma(volume, length)

        maPrice

    if maType == 'HMA'

        maPrice := ta.hma(volume, length)

        maPrice

    if maType == 'WMA'

        maPrice := ta.wma(volume, length)

        maPrice

    if maType == 'DEMA'

        e1 = ta.ema(volume, length)

        e2 = ta.ema(e1, length)

        maPrice := 2 * e1 - e2

        maPrice

    maPrice



ma = getMA0(maLength)

rvol = volume / ma



volumegood = volume > rvolTrigger * ma



//MA----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



ma5 = ta.sma(close, 5)

ma10 = ta.sma(close, 10)

ma30 = ta.sma(close, 30)



magood = ma5 > ma30

mabad = ma5 < ma30



simplema = ta.sma(src, length)

exponentialma = ta.ema(src, length)

hullma = ta.wma(2 * ta.wma(src, length / 2) - ta.wma(src, length), math.round(math.sqrt(length)))

weightedma = ta.wma(src, length)

volweightedma = ta.vwma(src, length)

avgval = matype == 1 ? simplema : matype == 2 ? exponentialma : matype == 3 ? hullma : matype == 4 ? weightedma : matype == 5 ? volweightedma : na

MA_speed = (avgval / avgval[1] - 1) * 100



masgood = MA_speed > 0

masbad = MA_speed < 0



//STRATEGY===============================================================================================================================================================================================================================================================



Long = DIPlus > DIMinus and ADX > th and volumegood and sargood and rsiob and macdgood and deltagood and magood and masgood and bullish and jmagood and rangegood

Short = DIPlus < DIMinus and ADX > th and volumegood and sarbad and rsios and macdbad and deltabad and mabad and masbad and jmabad and rangebad



//Signals======================================================================================================================================================================================================================



if Long and window() and long_

    strategy.entry('L', strategy.long,comment="long:2")

if Short and window() and short_

    strategy.entry('S', strategy.short,comment="short:2")

per(pcnt) =>

    strategy.position_size != 0 ? math.round(pcnt / 100 * strategy.position_avg_price / syminfo.mintick) : float(na)

stoploss = input.float(title=' stop loss', defval=9, minval=0.01)

los = per(stoploss)

q = input.int(title=' qty percent', defval=100, minval=1)



tp = input.float(title=' Take profit', defval=1.3, minval=0.01)



strategy.exit('tp', qty_percent=q, profit=per(tp),loss=los,comment="cover_long:2")

//strategy.exit('tp', qty_percent=q, loss=los,comment="cover_short")




// *************************************************************************************************************************************************************************************************************************************************************************
// 月表表现 - 由 @QuantNomad 开发
// *************************************************************************************************************************************************************************************************************************************************************************
show_performance = input.bool(true, '月度报告', group='Performance - credits: @QuantNomad')
prec = input(2, '返回精度', group='Performance - credits: @QuantNomad')

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
        table.cell(monthly_table, 1,  0, "1月",  bgcolor = #cccccc)
        table.cell(monthly_table, 2,  0, "2月",  bgcolor = #cccccc)
        table.cell(monthly_table, 3,  0, "3月",  bgcolor = #cccccc)
        table.cell(monthly_table, 4,  0, "4月",  bgcolor = #cccccc)
        table.cell(monthly_table, 5,  0, "5月",  bgcolor = #cccccc)
        table.cell(monthly_table, 6,  0, "6月",  bgcolor = #cccccc)
        table.cell(monthly_table, 7,  0, "7月",  bgcolor = #cccccc)
        table.cell(monthly_table, 8,  0, "8月",  bgcolor = #cccccc)
        table.cell(monthly_table, 9,  0, "9月",  bgcolor = #cccccc)
        table.cell(monthly_table, 10, 0, "10月",  bgcolor = #cccccc)
        table.cell(monthly_table, 11, 0, "11月",  bgcolor = #cccccc)
        table.cell(monthly_table, 12, 0, "12月",  bgcolor = #cccccc)
        table.cell(monthly_table, 13, 0, "全年", bgcolor = #999999)

    
        for yi = 0 to array.size(year_pnl) - 1
            table.cell(monthly_table, 0,  yi + 1, str.tostring(year(array.get(year_time, yi))), bgcolor = #cccccc)
            
            y_color = array.get(year_pnl, yi) > 0 ? color.new(color.teal, transp = 40) : color.new(color.gray, transp = 40)
            table.cell(monthly_table, 13, yi + 1, str.tostring(math.round(array.get(year_pnl, yi) * 100, prec)), bgcolor = y_color, text_color=color.new(color.white, 0))
            
        for mi = 0 to array.size(month_time) - 1
            m_row   = year(array.get(month_time, mi))  - year(array.get(year_time, 0)) + 1
            m_col   = month(array.get(month_time, mi)) 
            m_color = array.get(month_pnl, mi) > 0 ? color.new(color.teal, transp = 40) : color.new(color.gray, transp = 40)
            
            table.cell(monthly_table, m_col, m_row, str.tostring(math.round(array.get(month_pnl, mi) * 100, prec)), bgcolor = m_color, text_color=color.new(color.white, 0))
