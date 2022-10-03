// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// ? loxx

//@version=5
indicator("HMA Slope Variation [Loxx]",
     shorttitle="HMASV [Loxx]", 
     overlay = false, 
     timeframe="", 
     timeframe_gaps = true)

import loxx/loxxexpandedsourcetypes/4

greencolor = #2DD204
redcolor = #D2042D 
bluecolor = #042dd2

SM02 = 'Trend'
SM03 = 'Agreement'

smthtype = input.string("Kaufman", "Heikin-Ashi Better Caculation Type", options = ["AMA", "hma", "Kaufman"], group = "Source Settings")

srcin = input.string("Close", "Source", group= "Source Settings", 
     options = 
     ["Close", "Open", "High", "Low", "Median", "Typical", "Weighted", "Average", "Average Median Body", "Trend Biased", "Trend Biased (Extreme)", 
     "HA Close", "HA Open", "HA High", "HA Low", "HA Median", "HA Typical", "HA Weighted", "HA Average", "HA Average Median Body", "HA Trend Biased", "HA Trend Biased (Extreme)",
     "HAB Close", "HAB Open", "HAB High", "HAB Low", "HAB Median", "HAB Typical", "HAB Weighted", "HAB Average", "HAB Average Median Body", "HAB Trend Biased", "HAB Trend Biased (Extreme)"])

hmaPeriod = input.int(60, "Period", group= "Basic Settings")  
Treshold = input.float(10, "Threshold", group= "Basic Settings")  

sigtype = input.string(SM02, "Signal type", options = [SM02, SM03], group = "Signal Settings")

colorbars = input.bool(true, "Color bars?", group = "UI Options")
showSigs = input.bool(true, "Show signals?", group = "UI Options")

kfl=input.float(0.666, title="* Kaufman's Adaptive MA (KAMA) Only - Fast End", group = "Moving Average Inputs")
ksl=input.float(0.0645, title="* Kaufman's Adaptive MA (KAMA) Only - Slow End", group = "Moving Average Inputs")
amafl = input.int(2, title="* Adaptive Moving Average (AMA) Only - Fast", group = "Moving Average Inputs")
amasl = input.int(30, title="* Adaptive Moving Average (AMA) Only - Slow", group = "Moving Average Inputs")

haclose = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, close)
haopen = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, open)
hahigh = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, high)
halow = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, low)
hamedian = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hl2)
hatypical = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hlc3)
haweighted = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, hlcc4)
haaverage = request.security(ticker.heikinashi(syminfo.tickerid), timeframe.period, ohlc4)

src = switch srcin
	"Close" => loxxexpandedsourcetypes.rclose()
	"Open" => loxxexpandedsourcetypes.ropen()
	"High" => loxxexpandedsourcetypes.rhigh()
	"Low" => loxxexpandedsourcetypes.rlow()
	"Median" => loxxexpandedsourcetypes.rmedian()
	"Typical" => loxxexpandedsourcetypes.rtypical()
	"Weighted" => loxxexpandedsourcetypes.rweighted()
	"Average" => loxxexpandedsourcetypes.raverage()
    "Average Median Body" => loxxexpandedsourcetypes.ravemedbody()
	"Trend Biased" => loxxexpandedsourcetypes.rtrendb()
	"Trend Biased (Extreme)" => loxxexpandedsourcetypes.rtrendbext()
	"HA Close" => loxxexpandedsourcetypes.haclose(haclose)
	"HA Open" => loxxexpandedsourcetypes.haopen(haopen)
	"HA High" => loxxexpandedsourcetypes.hahigh(hahigh)
	"HA Low" => loxxexpandedsourcetypes.halow(halow)
	"HA Median" => loxxexpandedsourcetypes.hamedian(hamedian)
	"HA Typical" => loxxexpandedsourcetypes.hatypical(hatypical)
	"HA Weighted" => loxxexpandedsourcetypes.haweighted(haweighted)
	"HA Average" => loxxexpandedsourcetypes.haaverage(haaverage)
    "HA Average Median Body" => loxxexpandedsourcetypes.haavemedbody(haclose, haopen)
	"HA Trend Biased" => loxxexpandedsourcetypes.hatrendb(haclose, haopen, hahigh, halow)
	"HA Trend Biased (Extreme)" => loxxexpandedsourcetypes.hatrendbext(haclose, haopen, hahigh, halow)
	"HAB Close" => loxxexpandedsourcetypes.habclose(smthtype, amafl, amasl, kfl, ksl)
	"HAB Open" => loxxexpandedsourcetypes.habopen(smthtype, amafl, amasl, kfl, ksl)
	"HAB High" => loxxexpandedsourcetypes.habhigh(smthtype, amafl, amasl, kfl, ksl)
	"HAB Low" => loxxexpandedsourcetypes.hablow(smthtype, amafl, amasl, kfl, ksl)
	"HAB Median" => loxxexpandedsourcetypes.habmedian(smthtype, amafl, amasl, kfl, ksl)
	"HAB Typical" => loxxexpandedsourcetypes.habtypical(smthtype, amafl, amasl, kfl, ksl)
	"HAB Weighted" => loxxexpandedsourcetypes.habweighted(smthtype, amafl, amasl, kfl, ksl)
	"HAB Average" => loxxexpandedsourcetypes.habaverage(smthtype, amafl, amasl, kfl, ksl)
    "HAB Average Median Body" => loxxexpandedsourcetypes.habavemedbody(smthtype, amafl, amasl, kfl, ksl)
	"HAB Trend Biased" => loxxexpandedsourcetypes.habtrendb(smthtype, amafl, amasl, kfl, ksl)
	"HAB Trend Biased (Extreme)" => loxxexpandedsourcetypes.habtrendbext(smthtype, amafl, amasl, kfl, ksl)
	=> haclose
	
_hmaa = ta.hma(src, hmaPeriod)

_hmao = 100.0 * (_hmaa - nz(_hmaa[1])) / nz(_hmaa[1])
_hmas = (4.0 * _hmao + 3.0 * nz(_hmao[1]) + 2.0 * nz(_hmao[2]) + nz(_hmao[3])) / 10.0
hmaout = _hmao

minVal = math.min(_hmao, _hmas)
maxVal = math.max(_hmao, _hmas)

diffP = 0.
if (minVal != 0) 
    diffP := math.abs(100 * (maxVal - minVal) / minVal)

HistoUP = 0.
HistoDN = 0.
HistoNN = 0.
TrendUP = 0.
TrendDN = 0.

TrendUP := TrendUP[1]
TrendDN := TrendDN[1]

if _hmao > _hmas and diffP > Treshold
    TrendUP := 0
    TrendDN := na

if _hmao < _hmas and diffP > Treshold
    TrendDN := 0
    TrendUP := na

if _hmao > 0 and TrendUP == 0
    if high <= nz(high[1])  
        HistoUP := _hmao
    else 
        HistoNN := _hmao
      
if _hmao < 0 and TrendDN == 0
    if low >= nz(low[1])  
        HistoDN := _hmao
    else 
        HistoNN := _hmao

trendcolor = hmaout > 0 ? greencolor : hmaout < 0 ? redcolor : color.gray
colorout = HistoUP > 0 ? greencolor : HistoDN < 0 ? redcolor : color.gray

mid = 0.           

plot(HistoUP, color = greencolor, linewidth = 2, style = plot.style_histogram)
plot(HistoDN, color = redcolor, linewidth = 2, style = plot.style_histogram)
plot(HistoNN, color = color.gray, linewidth = 2, style = plot.style_histogram)

plot(mid, color = trendcolor, linewidth = 3)
plot(hmaout, color = color.gray, linewidth = 2)

barcolor(colorbars ? sigtype == SM02 ? trendcolor : colorout : na)

pregoLong = sigtype == SM02 ? trendcolor == greencolor and trendcolor[1] != greencolor : colorout == greencolor and colorout[1] != greencolor
pregoShort = sigtype == SM02 ? trendcolor == redcolor and trendcolor[1] != redcolor : colorout == redcolor and colorout[1] != redcolor

contswitch = 0
contswitch := nz(contswitch[1])
contswitch := pregoLong ? 1 : pregoShort ? -1 : contswitch

goLong = pregoLong and contswitch == 1 and contswitch[1] == -1
goShort = pregoShort and contswitch == -1 and contswitch[1] == 1

plotshape(showSigs and goLong, title = "Long", color = color.yellow, textcolor = color.yellow, text = "L", style = shape.triangleup, location = location.bottom, size = size.auto)
plotshape(showSigs and goShort, title = "Short", color = color.fuchsia, textcolor = color.fuchsia, text = "S", style = shape.triangledown, location = location.top, size = size.auto)

alertcondition(goLong, title = "Long", message = "HMA Slope Variation [Loxx]: Long\nSymbol: {{ticker}}\nPrice: {{close}}")
alertcondition(goShort, title = "Short", message = "HMA Slope Variation [Loxx]: Short\nSymbol: {{ticker}}\nPrice: {{close}}")