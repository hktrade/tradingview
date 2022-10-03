//@version=4
strategy("EMA Bounce", overlay=true, 
     default_qty_type=strategy.percent_of_equity, 
     default_qty_value=100, 
     initial_capital=10000, 
     commission_value=0.04, 
     calc_on_every_tick=false, 
     slippage=0)

E34=ema(hlc3,34)
usedEma = security(syminfo.tickerid,"15",E34)
emaUpColor() => hlc3 >= usedEma
emaDownColor() => hlc3  < usedEma
col = hlc3  >= usedEma ? color.lime : hlc3  < usedEma ?  color.red : color.white
barcolor(emaUpColor() ? color.lime: emaDownColor() ? color.red : na)
//plot(usedEma ? usedEma : na, title="EMA", style=plot.style_line , linewidth=3, color=col)
E34B = cross(hlc3,E34) and usedEma[1]-usedEma<usedEma[2]-usedEma[1]  and emaDownColor() and high < usedEma and not emaUpColor()[3]
plotshape(series=E34B, style=shape.cross, color=color.green,  text="34", title='34') 
