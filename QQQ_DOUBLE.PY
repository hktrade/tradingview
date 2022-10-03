//@version=4

strategy(title = "QQQ_DOUBLE", shorttitle="QQQ_DOUBLE",overlay=true)

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

k_sub = security(syminfo.tickerid, "5", k) // 3 m time frame for k
d_sub = security(syminfo.tickerid, "5", d) // 3 m time frame for d

vwap_ = vwap(close)
sma_ = ema(close,50)

sma_3 = sma(close,3)
sma_5 = sma(close,5)
sma_10 = sma(close,10)

//sma_sub = security(syminfo.tickerid,"3",sma_)
vwap_1 = security(syminfo.tickerid,"1",vwap_)

//close_sub = security(syminfo.tickerid,"3",close)

plot(sma_)
plot(sma_3,color=color.red)
plot(sma_5,color=color.yellow)
plot(sma_10,color=color.blue)

plot(vwap_1,color=color.white)

plot(sma_)
	
//plot(k,style=plot.style_stepline)
//plot(d,style=plot.style_stepline)
//plot(k_sub,style=plot.style_stepline)
//plot(d_sub,style=plot.style_stepline)

DIF = ema(close, 9) - ema(close, 26) //9 26 12 5 57 14
DEA = ema(DIF, 12)
macd_bar = (DIF - DEA) * 2
macd = security(syminfo.tickerid,"15",macd_bar)

volumeUp = if volume>volume[1] and hlc3>hlc3[1]
	true
else
	false
volumeDown = if volume>volume[1] and hlc3<hlc3[1]
	true
else
	false

p_close = if (DIF > 0 and close > vwap_ and DEA < 0) or (cross(DIF, DEA) and macd>macd[1])
    true
else
    false
p_high = if high > max(sma_5,sma_3,sma_10,sma_)
	true
else
	false
p_buy = if cross(close, sma_5) and vwap_ > vwap_[1] and close > open and close > close[1] and not p_high
    true
else
    false
p_buy2 = if cross(DIF, DEA) and vwap_ > vwap_[1] and close > open and close > close[1] and not p_high
    true
else
    false

p_sell = if ((cross(d, k) and low > vwap_) or cross( vwap_1,close)) and open<open[1] and open>close and not volumeUp and sma_<vwap_1
    true
else
    false

p_sell2 = if sma_5==highest(sma_5,10) and high[1] > sma_3[1] and sma_3[1] and sma_5[1] > sma_10[1] and close<sma_10
	true
else
	false
plotshape(series=p_buy2, style=shape.cross, color=color.green,  text="b2", title='b2')  
plotshape(series=p_buy, style=shape.cross, color=color.green,  text="b", title='b')  
plotshape(series=p_sell, style=shape.cross, color=color.red,  text="s", title='s')
plotshape(series=p_sell2, style=shape.cross, color=color.red,  text="p_sell2", title='p_sell2')
plotshape(series=p_close, style=shape.cross, color=color.red,  text="p_close", title='p_close')

strategy.entry("buy", strategy.long, 100, comment='openlong', when=window() and strategy.position_size == 0 and (p_buy or p_buy2))
	
strategy.close("buy", comment='closelong', when = strategy.position_size >=0 and (p_sell or p_sell2))
	
// 上面两个条件 开多 平多，下面两个条件 开空 平空

strategy.entry("sell", strategy.short, 100, comment='openshort', when=window() and strategy.position_size == 0 and (p_sell or p_sell2))
	
strategy.close("sell", comment='closeshort', when = strategy.position_size <=0 and (p_buy or p_close))