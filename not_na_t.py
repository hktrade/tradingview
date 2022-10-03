//@version=4

strategy(title = "QQQ 1M", shorttitle="QQQ 1M",overlay=true)

config_FromDay = '2022-06-01T00:00:00'
config_ToDay = '2025-01-01T00:00:00'
starttime = input(defval = timestamp(config_FromDay), title = "Begin time")
finishtime = input(defval = timestamp(config_ToDay), title = "End time")
window()  => time >= starttime and time <= finishtime ? true : false
sma_3 = sma(close,3)
sma_5 = sma(close,5)
sma_10 = sma(close,10)
t1 = time(timeframe.period, '0930-0940:23456')
t2 = time(timeframe.period, '1550-1600:23456')
t_b1 = not na(t1)
t_b2 = not na(t2)

periodK = input(9, title="K", minval=1)
periodD = input(3, title="D", minval=1)
smoothK = input(3, title="Smooth", minval=1)
k = sma(stoch(close, high, low, periodK), smoothK)
d = sma(k, periodD)
vwap_ = vwap(close)
sma_200 = sma(close,200)

p_sell2 = if sma_5==highest(sma_5,10) and high[1] > sma_3[1] and sma_3[1] and sma_5[1] > sma_10[1]
	true
else
	false
p_sell = security(syminfo.tickerid, "3", p_sell2)

//open_B = sma_200 > close and cross(k,d) and k < 45 and vwap_<vwap_[1] and t_b1
close_S = sma_200 < close and vwap_ < close and cross(d,k) and d > 55 and t_b2 and p_sell and close<sma_10  
//plotshape(series=open_B,style=shape.cross,color=color.green, text="open_B", title='open_B')
plotshape(series=close_S,style=shape.cross,color=color.red, text="close_S", title='close_S')

strategy.order("sell", strategy.short, 1, comment='openshort_close_S', when=window() and close_S)
