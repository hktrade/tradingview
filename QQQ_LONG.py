//@version=4

strategy(title = "QQQ_LONG", shorttitle="QQQ_LONG",overlay=true)

// 5min for QQQ
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
sma_ = ema(close,50)

sma_3 = sma(close,3)
sma_5 = sma(close,5)
sma_10 = sma(close,10)


vwap_1 = security(syminfo.tickerid,"1",vwap_)

plot(sma_)

plot(sma_3,color=color.red)
plot(sma_5,color=color.yellow)
plot(sma_10,color=color.blue)

plot(vwap_1,color=color.white)

plot(sma_)
	
DIF = ema(close, 5) - ema(close, 57)
DEA = ema(DIF, 14)
macd_bar = (DIF - DEA) * 2
macd = security(syminfo.tickerid,"15",macd_bar)
dayl = security(syminfo.tickerid,"D",low)
dayh = security(syminfo.tickerid,"D",high)
plot(dayh[1],style=plot.style_line)
plot(dayl[1],style=plot.style_line)
volumeUp = if volume>volume[1] and hlc3>hlc3[1]
	true
else
	false

v15 = security(syminfo.tickerid,"15",volumeUp)
sma2=sma(close,2)
sma21=sma(close,21)
ma2 = security(syminfo.tickerid,"D",sma2)
ma21 = security(syminfo.tickerid,"D",sma21)

p_high = if high > max(sma_5,sma_3,sma_10,sma_)
	true
else
	false

p_sell = if ((cross(d, k) and high > vwap_) or cross( vwap_1,close)) and open<open[1] and open>close and not volumeUp and vwap_1<vwap_1[1] and low>dayl[1]*1.5
    true
else
    false
	
E34=ema(hlc3,34)
usedEma = security(syminfo.tickerid,"15",E34)
emaUpColor() => hlc3 >= usedEma
emaDownColor() => hlc3  < usedEma
col = hlc3  >= usedEma ? color.lime : hlc3  < usedEma ?  color.red : color.white
plot(usedEma ? usedEma : na, title="EMA", style=plot.style_line , linewidth=3, color=col)
b34 = cross(hlc3,E34) and usedEma[1]-usedEma<usedEma[2]-usedEma[1] and emaDownColor() and high < usedEma and not emaUpColor()[3]

kdb = cross(k_sub, d_sub) and k < 25 and sma_[1] < vwap_[1] and sma_10[1]<sma_[1] and low>low[1]
kds = cross(d_sub, k_sub) and d > 65 and high[4] > sma_3[4] and sma_5[4] > sma_10[4] and sma_10[4]>sma_[4] and not volumeUp and not v15
plotshape(series=kdb, style=shape.cross, color=color.green,  text="kdb", title='kdb')
plotshape(series=kds, style=shape.cross, color=color.red,  text="kds", title='kds')
plotshape(series=b34, style=shape.cross, color=color.green,  text="b2", title='b2')

plotshape(series=p_sell, style=shape.cross, color=color.red,  text="s", title='s')
 
//low<dayl[1]*1.0015
//if low<dayl[1]*1.0015 and vwap_<sma_ and vwap_ > vwap_[1] and close > open and not p_high and volumeUp
// and high>dayh[1]*0.9925

// if (p_sell or kds) and emaUpColor()
// 	kds:=true
// else
// 	kds:=false
	
strategy.entry("buy", strategy.long, 100, comment='openlong_long', when=window() and strategy.position_size == 0 and (b34 or kdb) and ma21>ma21[1])// and ma2>ma21)
	
//strategy.close("buy", comment='closelong_long', when = strategy.position_size >=0 and (p_sell or kds))

sl = 0.016
tp = 0.016
long_sl = strategy.position_avg_price*(1-sl)
long_tp = strategy.position_avg_price*(1+tp)

short_sl = strategy.position_avg_price*(1+sl)
short_tp = strategy.position_avg_price*(1-tp)

if strategy.position_size > 0 
	strategy.exit(id='close', comment='closelong', stop=long_sl, limit=long_tp)