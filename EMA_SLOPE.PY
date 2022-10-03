//@version=5
// By Pedro Braconnot
// New version with minor adjustments.
// Moving averages Slope with no trade zones where slope is under Threshold.

//indicator('EMA Slope', precision=5, timeframe="", timeframe_gaps=true)
strategy(title = "QQQ_HOUR", shorttitle="QQQ_HOUR",overlay=true)

smoothBars = input.int(3, 'Smooth Bars', minval=1)
maLength = input.int(100, 'MA Length', minval=1)
noTZone = input(true, 'No Trade Zone Threshold')
maDL = input.int(8, 'NTZ Threshold', step=1, minval=1)
hLineHeight = maDL
maType = input.string('EMA', 'MA Type', options=['SMA', 'EMA', 'DEMA', 'TEMA', 'WMA', 'VWMA', 'SMWMA', 'SWMA', 'HMA'])
src = input(close, 'MA Source')

// Moving Average function, for MA Cross, long MA plot and MA Slope no trade zone detection.
fma(type, src, _len) =>
    float result = 0
    if type == 'SMA'
        result := ta.sma(src, _len)
        result
    if type == 'EMA'  // Exponential
        result := ta.ema(src, _len)
        result
    if type == 'DEMA'
        e = ta.ema(src, _len)
        result := 2 * e - ta.ema(e, _len)
        result
    if type == 'TEMA'
        e = ta.ema(src, _len)
        result := 3 * (e - ta.ema(e, _len)) + ta.ema(ta.ema(e, _len), _len)
        result
    if type == 'WMA'
        result := ta.wma(src, _len)
        result
    if type == 'VWMA'
        result := ta.vwma(src, _len)
        result
    if type == 'SMWMA'  // Smoothed
        w = ta.wma(src, _len)
        wb = ta.sma(src, _len)
        result := na(w[1]) ? wb : (w[1] * (_len - 1) + src) / _len
        result
    if type == 'SWMA'  // Symmetrically weighted
        result := ta.swma(src)
        result
    if type == 'HMA'
        result := ta.wma(2 * ta.wma(src, _len / 2) - ta.wma(src, _len), math.round(math.sqrt(_len)))
        result
    result

ma = fma(maType, src, maLength)
maDF = ma - ma[smoothBars]
// MA Slope scale
fmaDf(ma, maDF) =>
    maMax = ta.highest(maDF,500)
    maMin = ta.lowest(maDF,500)
    ma_range = maMax - maMin
    maDf = 100 * maDF / ma_range
    maDf

maDf = fmaDf(ma, maDF)

maAcc = math.abs(maDf - maDf[1]) * smoothBars * 2

// Plotting
cUP = color.rgb(38, 255, 72, 50)
cUPb = color.rgb(38, 255, 52, 40)
cLP = color.rgb(255, 20, 20, 40)
cLPb = color.rgb(229, 18, 18, 40)
cNTZ = color.rgb(186, 167, 167, 70)
colorS = maDf > 0 ? cUP : maDf < 0 ? cLP : cNTZ

//Colors
f_colorN(maDf, maDL, cUP, cUPb, cLP, cLPb, cNTZ) =>
    colorN = color.rgb(38, 255, 72, 75)
    colorN := maDf > 0 and maDf > maDL and maDf > maDf[1] ? cUPb : maDf > 0 and maDf > maDL and maDf <= maDf[1] ? cUP : maDf > 0 and maDf <= maDL ? cNTZ : maDf <= 0 and maDf < -maDL and maDf > maDf[1] ? cLPb : maDf <= 0 and maDf < -maDL and maDf <= maDf[1] ? cLP : maDf > -maDL ? cNTZ : na
    colorN

c_ntz = noTZone ? f_colorN(maDf, maDL, cUP, cUPb, cLP, cLPb, cNTZ) : colorS
c_Acc = maAcc > 30 and maDf > 0 ? color.rgb(10, 246, 255, (50 - maAcc)) : maAcc > 30  and maDf < 0 ? color.rgb(239, 2, 77, (50 - maAcc)) : color.rgb(160, 160, 160, 40)

hUp = hline(hLineHeight, title='NTZ Top', color=color.rgb(75, 219, 94, 40), linewidth=2, linestyle=hline.style_dashed)
hDn = hline(-hLineHeight, title='NTZ Bottom', color=color.rgb(244, 34, 34, 40), linewidth=2, linestyle=hline.style_dashed)
fill(hUp,hDn,color=color.new(color.gray,80))
hline(0, linestyle=hline.style_solid, color=color.rgb(255, 255, 255, 70))
plot(maDf, 'Diff MA', c_ntz)
plot(maDf, 'Diff MA fill', c_ntz, style=plot.style_area)
plot(maAcc, 'MA Accel', color=c_Acc, style=plot.style_line, linewidth=2)

ma2=ta.sma(close,2)
ma21=ta.sma(close,21)

ma2D = request.security(syminfo.tickerid,"D",ma2)
ma21D = request.security(syminfo.tickerid,"D",ma21)
// PLUS D sma :44 1.53 , 41 1.97
p_buy = if maDf[3] <= 0 and maDf[2] <= 0 and maDf[1] <= 0 and maDf > 0 and ma2D>ma21D
    true
else
    false
p_sell = if maDf[3] >= 0 and maDf[2] >= 0 and maDf[1] >= 0 and maDf < 0
    true
else
    false

strategy.entry("buy", strategy.long, 100, comment='openlong', when=  p_buy)
strategy.close("buy", comment='closelong', when=  p_sell)