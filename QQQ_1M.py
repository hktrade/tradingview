//@version=4

strategy(title = "QQQ 1M", shorttitle="QQQ 1M",overlay=true)

config_FromDay = '2022-06-01T00:00:00'
config_ToDay = '2025-01-01T00:00:00'
starttime = input(defval = timestamp(config_FromDay), title = "Begin time")
finishtime = input(defval = timestamp(config_ToDay), title = "End time")
window()  => time >= starttime and time <= finishtime ? true : false

t1 = time(timeframe.period, '0930-0940:23456')
t2 = time(timeframe.period, '1550-1600:23456')
t_b1 = not na(t1)
t_b2 = not na(t2)

dayl = security(syminfo.tickerid,"D",low)
dayh = security(syminfo.tickerid,"D",high)
daysell = if highest(high,10) > dayh and t_b2
	true
else
	false
daybuy = if lowest(low,10) < dayl and t_b2
	true
else
	false
plot(dayh[1],style=plot.style_line)
plot(dayl[1],style=plot.style_line)

strategy.entry("buy", strategy.long, 100, comment='openlong_end', when= daybuy)
strategy.close("buy", comment='closelong_end', when= daysell)

strategy.entry("sell", strategy.short, 100, comment='openshort_end', when= daysell)
strategy.close("sell", comment='closeshort_end', when= daybuy)
