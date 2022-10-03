//@version=4
// 16.9 40%
strategy(title = "QQQ_HOUR", shorttitle="QQQ_HOUR",overlay=true)

// 1 hour for QQQ
config_FromDay = '2022-06-01T00:00:00'
config_ToDay = '2025-01-01T00:00:00'
starttime = input(defval = timestamp(config_FromDay), title = "开始时间")
finishtime = input(defval = timestamp(config_ToDay), title = "结束时间")
window()  => time >= starttime and time <= finishtime ? true : false

periodK = input(9, title="K", minval=1)
periodD = input(3, title="D", minval=1)
smoothK = input(3, title="Smooth", minval=1)

k = sma(stoch(close, high, low, periodK), smoothK)
d = sma(k, periodD)

k_sub = security(syminfo.tickerid, "10", k) // 3 m time frame for k
d_sub = security(syminfo.tickerid, "10", d) // 3 m time frame for d

vwap_ = vwap(close)

vwap_1 = security(syminfo.tickerid,"1",vwap_)

plot(vwap_1,color=color.white)

DIF = ema(close, 5) - ema(close, 57)
DEA = ema(DIF, 14)
macd_bar = (DIF - DEA) * 2
macd = security(syminfo.tickerid,"15",macd_bar)
dayl = security(syminfo.tickerid,"D",low)
dayh = security(syminfo.tickerid,"D",high)
//plot(dayh[1],style=plot.style_line)
//plot(dayl[1],style=plot.style_line)
volumeUp = if volume>volume[1] and hlc3>hlc3[1]
	true
else
	false

v15 = security(syminfo.tickerid,"15",volumeUp)
//sma2=sma(close,2)
//sma21=sma(close,21)

ma2=sma(close,2)
ma21=sma(close,21)

ma2D = security(syminfo.tickerid,"D",ma2)
ma21D = security(syminfo.tickerid,"D",ma21)

plot(ma2)
plot(ma21)
	
E34=ema(close,34)
//usedEma = security(syminfo.tickerid,"15",E34)
usedEma = E34
emaUpColor() => hlc3 >= usedEma
emaDownColor() => hlc3  < usedEma
col = hlc3  >= usedEma ? color.lime : hlc3  < usedEma ?  color.red : color.white
plot(usedEma ? usedEma : na, title="EMA", style=plot.style_line , linewidth=3, color=col)

b34 = usedEma[1]-usedEma<usedEma[2]-usedEma[1] and emaDownColor() and high < usedEma and not emaUpColor()[3]

p_buy = if crossover(ma2, ma21) and ma2[1] < ma21[1] and ma2[2] < ma21[2] and ma2[3] < ma21[3] 
    true
else
    false
p_sell = if crossover(ma21, ma2) and ma2[1] > ma21[1] and ma2[2] > ma21[2] and ma2[3] > ma21[3] 
    true
else
    false

strategy.entry("buy", strategy.long, 100, comment='openlong', when= p_buy)
	
strategy.close("buy", comment='closelong', when = strategy.position_size >0 and p_sell)
	
//strategy.entry("sell", strategy.short, 100, comment='openshort', when= p_sell )
	
//strategy.close("sell", comment='closeshort', when = strategy.position_size <0 and p_buy)
