import { memo, useMemo } from 'react'

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type {
  ADXResult,
  BBBreakoutResult,
  IndicatorName,
  IndicatorSignal,
  IndicatorTimeframe,
  MACDResult,
  MovingAverageCrossResult,
  PivotPointResult,
  SupportResistanceResult,
  TimeframeIndicators,
  VWAPBandsResult,
  WilliamsRResult
} from '@/types/api/indicators'

import { getSignalColor, MiniChart } from './minichart'
import { type Signal, SignalBadge } from './signalBadge'

const EMA_BADGE_COLORS = {
  price: 'hsl(var(--bearish))',
  ema9: 'hsl(189 88% 66%)',
  ema21: 'hsl(43 96% 60%)',
  ema55: 'hsl(324 78% 68%)',
  ema200: 'hsl(215 14% 74%)'
} as const

const INDICATOR_META: Record<IndicatorName, { short: string; name: string }> = {
  bb_breakout: {
    short: 'BB',
    name: 'Bollinger Breakout (20, 3)'
  },
  support_resistance: {
    short: 'Support / Resistance',
    name: 'Reacao em niveis-chave'
  },
  pivot_point: {
    short: 'Pivot Point',
    name: 'Pivo classico'
  },
  adx: {
    short: 'ADX',
    name: 'Average Directional Index (14)'
  },
  williams_r: {
    short: 'Williams %R',
    name: 'Williams Percent Range (14)'
  },
  macd: {
    short: 'MACD',
    name: 'MACD (12, 26, 9)'
  },
  moving_average_cross: {
    short: 'EMA Cross',
    name: 'EMA 9, 21, 55, 200'
  },
  vwap_bands: {
    short: 'VWAP Bands',
    name: 'VWAP com bandas 1x e 2x'
  }
}

const STATUS_LABELS: Record<string, string> = {
  DENTRO_DAS_BANDAS: 'Nas bandas',
  ROMPEU_BANDA_INFERIOR: 'Breakout inf.',
  ROMPEU_BANDA_SUPERIOR: 'Breakout sup.',
  ACIMA_DA_MEDIA: 'Acima media',
  ABAIXO_DA_MEDIA: 'Abaixo media',
  ACIMA_DA_MEDIA_LONGE_BANDA_SUPERIOR: 'Acima media',
  ACIMA_DA_MEDIA_PERTO_BANDA_SUPERIOR: 'Perto banda sup.',
  ABAIXO_DA_MEDIA_LONGE_BANDA_INFERIOR: 'Abaixo media',
  ABAIXO_DA_MEDIA_PERTO_BANDA_INFERIOR: 'Perto banda inf.',
  DEFENDEU_SUPORTE: 'Suporte ok',
  REJEITOU_RESISTENCIA: 'Resistencia',
  PRESSIONANDO_RESISTENCIA: 'Pressao res.',
  PRESSIONANDO_SUPORTE: 'Pressao sup.',
  RANGE: 'Range',
  ACIMA_DO_PIVO: 'Acima pivo',
  ABAIXO_DO_PIVO: 'Abaixo pivo',
  NO_PIVO: 'No pivo',
  ALINHADO_PARA_COMPRA: 'Compra alinhada',
  ALINHADO_PARA_VENDA: 'Venda alinhada',
  MISTO: 'Neutro',
  SEM_VWAP: 'Sem VWAP',
  ACIMA_BANDA_2: 'Acima banda 2',
  ABAIXO_BANDA_2: 'Abaixo banda 2',
  ACIMA_BANDA_1: 'Acima banda 1',
  ABAIXO_BANDA_1: 'Abaixo banda 1',
  ACIMA_VWAP: 'Acima VWAP',
  ABAIXO_VWAP: 'Abaixo VWAP'
}

interface IndicatorCardProps {
  indicator: IndicatorName
  values: Partial<Record<IndicatorTimeframe, TimeframeIndicators>>
  timeframes: IndicatorTimeframe[]
  className?: string
}

interface IndicatorTileViewModel {
  timeframe: IndicatorTimeframe
  signal: Signal
  footerLabel: string
  guideLines?: Array<{
    value: number
    color?: string
    opacity?: number
    dashed?: boolean
    width?: number
  }>
  zeroLine?: boolean
  histogram?: number[]
  cloud?: {
    upper: number[]
    lower: number[]
    color: string
    opacity?: number
  }
  series: Array<{
    data: number[]
    color: string
    dashed?: boolean
    width?: number
    opacity?: number
  }>
}

function LegendBadge({ label, color }: { label: string; color: string }) {
  return (
    <span className="bg-muted/50 text-muted-foreground inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-medium">
      <span className="size-2 rounded-full" style={{ backgroundColor: color }} />
      <span>{label}</span>
    </span>
  )
}

function toSignal(signal: IndicatorSignal): Signal {
  return signal
}

function formatNumber(value: number | null, digits = 1): string {
  if (value === null || Number.isNaN(value)) {
    return '-'
  }

  return value >= 0 ? `+${value.toFixed(digits)}` : value.toFixed(digits)
}

function formatStatus(status: string): string {
  return STATUS_LABELS[status] ?? status
}

function makeGuideLine(value: number, color?: string, options?: { opacity?: number; dashed?: boolean; width?: number }) {
  return {
    value,
    color,
    opacity: options?.opacity,
    dashed: options?.dashed,
    width: options?.width
  }
}

function buildTrendSeries(
  value: number,
  {
    min = 0,
    max = 100,
    size = 18,
    phase = 0,
    trend = 0.2
  }: {
    min?: number
    max?: number
    size?: number
    phase?: number
    trend?: number
  } = {}
) {
  const center = Math.min(max, Math.max(min, value))
  const amplitude = Math.max((max - min) * 0.03, 0.55)

  return Array.from({ length: size }, (_, index) => {
    const progress = index / Math.max(size - 1, 1)
    const drift = (center - (min + max) / 2) * progress * trend
    const wave = Math.sin(progress * Math.PI * 2 + phase) * amplitude
    return Math.max(min, Math.min(max, center - drift * 0.35 + wave))
  })
}

function buildOscillationSeries(
  value: number,
  {
    min,
    max,
    size = 18,
    phase = 0,
    amplitudeRatio = 0.055
  }: {
    min: number
    max: number
    size?: number
    phase?: number
    amplitudeRatio?: number
  }
) {
  const center = Math.min(max, Math.max(min, value))
  const amplitude = Math.max((max - min) * amplitudeRatio, 0.5)

  return Array.from({ length: size }, (_, index) => {
    const progress = index / Math.max(size - 1, 1)
    const wave = Math.sin(progress * Math.PI * 2 + phase) * amplitude
    return Math.max(min, Math.min(max, center + wave))
  })
}

function buildMacdHistory(macdValue: number, signalValue: number, histogramValue: number, size = 18) {
  const scale = Math.max(Math.abs(macdValue), Math.abs(signalValue), Math.abs(histogramValue), 0.4)
  const macdSeries: number[] = []
  const signalSeries: number[] = []
  const histogramSeries: number[] = []
  const startMacd = macdValue - histogramValue * 2.2 - Math.sign(macdValue || 1) * scale * 0.18
  const startSignal = signalValue - histogramValue * 1.2
  let previousSignal = startSignal

  for (let index = 0; index < size; index += 1) {
    const progress = index / Math.max(size - 1, 1)
    const easing = 1 - (1 - progress) * (1 - progress)
    const macdTarget = startMacd + (macdValue - startMacd) * easing
    const macdNoise = Math.sin(progress * Math.PI * 3.1) * scale * 0.035
    const nextMacd = macdTarget + macdNoise
    const nextSignal = previousSignal + (nextMacd - previousSignal) * (0.18 + progress * 0.1)

    previousSignal = nextSignal
    macdSeries.push(nextMacd)
    signalSeries.push(nextSignal)
    histogramSeries.push(nextMacd - nextSignal)
  }

  macdSeries[size - 1] = macdValue
  signalSeries[size - 1] = signalValue
  histogramSeries[size - 1] = histogramValue

  return { macdSeries, signalSeries, histogramSeries }
}

function buildAverageSeries(source: number[], fallback: number, size = 18) {
  return source.length > 0 ? source : buildTrendSeries(fallback, { min: fallback * 0.96, max: fallback * 1.04, size, trend: 0.08 })
}

function inferWilliamsRSignal(result: WilliamsRResult): Signal {
  if (result.value === null) {
    return 'NEUTRAL'
  }

  if (result.value <= -80) {
    return 'BUY'
  }

  if (result.value >= -20) {
    return 'SELL'
  }

  return 'NEUTRAL'
}

function inferMacdSignal(result: MACDResult): Signal {
  if (result.value === null || result.signal === null) {
    return 'NEUTRAL'
  }

  if (result.value > result.signal) {
    return 'BUY'
  }

  if (result.value < result.signal) {
    return 'SELL'
  }

  return 'NEUTRAL'
}

function inferAdxSignal(result: ADXResult): Signal {
  if (result.plus_di === null || result.minus_di === null) {
    return 'NEUTRAL'
  }

  if (result.plus_di > result.minus_di) {
    return 'BUY'
  }

  if (result.minus_di > result.plus_di) {
    return 'SELL'
  }

  return 'NEUTRAL'
}

function buildWilliamsRTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result = data?.williams_r ?? { value: null, length: 14, series: [] }
  const signal = inferWilliamsRSignal(result)
  const baseValue = result.value ?? -50

  return {
    timeframe,
    signal,
    footerLabel: result.value === null ? '-' : result.value.toFixed(1),
    guideLines: [makeGuideLine(-80), makeGuideLine(-20)],
    series: [
      {
        data: result.series.length > 0 ? result.series : buildTrendSeries(baseValue, { min: -100, max: 0, phase: timeframe.length * 0.3, trend: 0.12 }),
        color: getSignalColor(signal)
      }
    ]
  }
}

function buildMacdTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result = data?.macd ?? {
    value: null,
    signal: null,
    histogram: null,
    fast: 12,
    slow: 26,
    signal_period: 9,
    macd_series: [],
    signal_series: [],
    histogram_series: []
  }
  const signal = inferMacdSignal(result)
  const history =
    result.macd_series.length > 0 && result.signal_series.length > 0 && result.histogram_series.length > 0
      ? {
          macdSeries: result.macd_series,
          signalSeries: result.signal_series,
          histogramSeries: result.histogram_series
        }
      : buildMacdHistory(result.value ?? 0, result.signal ?? 0, result.histogram ?? 0)

  return {
    timeframe,
    signal,
    footerLabel: formatNumber(result.value, 4),
    zeroLine: true,
    histogram: history.histogramSeries,
    series: [
      {
        data: history.macdSeries,
        color: 'hsl(var(--foreground))',
        width: 1.15
      },
      {
        data: history.signalSeries,
        color: getSignalColor(signal),
        width: 1.1,
        opacity: 0.9
      }
    ]
  }
}

function buildAdxTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result = data?.adx ?? {
    value: null,
    plus_di: null,
    minus_di: null,
    length: 14,
    adx_series: [],
    plus_di_series: [],
    minus_di_series: []
  }
  const signal = inferAdxSignal(result)
  const adxValue = result.value ?? 18
  const plusDi = result.plus_di ?? 20
  const minusDi = result.minus_di ?? 20

  return {
    timeframe,
    signal,
    footerLabel: result.value === null ? '-' : `${result.value.toFixed(1)} ${signal === 'BUY' ? '↑' : signal === 'SELL' ? '↓' : ''}`.trim(),
    guideLines: [makeGuideLine(25)],
    series: [
      {
        data: result.adx_series.length > 0 ? result.adx_series : buildOscillationSeries(adxValue, { min: 0, max: 60, phase: timeframe.length * 0.25, amplitudeRatio: 0.08 }),
        color: getSignalColor(signal)
      },
      {
        data: result.plus_di_series.length > 0 ? result.plus_di_series : buildOscillationSeries(plusDi, { min: 0, max: 60, phase: 1.15, amplitudeRatio: 0.06 }),
        color: 'hsl(var(--bullish))',
        dashed: true,
        width: 1,
        opacity: 0.75
      },
      {
        data: result.minus_di_series.length > 0 ? result.minus_di_series : buildOscillationSeries(minusDi, { min: 0, max: 60, phase: 2.05, amplitudeRatio: 0.06 }),
        color: 'hsl(var(--bearish))',
        dashed: true,
        width: 1,
        opacity: 0.75
      }
    ]
  }
}

function buildMovingAverageCrossTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result: MovingAverageCrossResult = data?.moving_average_cross ?? {
    signal: 'NEUTRAL',
    status: 'MISTO',
    value: null,
    ema_9: null,
    ema_21: null,
    ema_55: null,
    ema_200: null,
    price_series: [],
    ema_9_series: [],
    ema_21_series: [],
    ema_55_series: [],
    ema_200_series: []
  }

  const signal = toSignal(result.signal)
  const value = result.value ?? 100
  const ema9 = result.ema_9 ?? value
  const ema21 = result.ema_21 ?? value
  const ema55 = result.ema_55 ?? value
  const ema200 = result.ema_200 ?? value

  return {
    timeframe,
    signal,
    footerLabel: formatStatus(result.status),
    series: [
      {
        data: buildAverageSeries(result.price_series, value),
        color: EMA_BADGE_COLORS.price,
        width: 1.75
      },
      {
        data: buildAverageSeries(result.ema_9_series, ema9),
        color: EMA_BADGE_COLORS.ema9,
        width: 1.2,
        opacity: 0.96
      },
      {
        data: buildAverageSeries(result.ema_21_series, ema21),
        color: EMA_BADGE_COLORS.ema21,
        width: 1.12,
        opacity: 0.96
      },
      {
        data: buildAverageSeries(result.ema_55_series, ema55),
        color: EMA_BADGE_COLORS.ema55,
        width: 1.08,
        opacity: 0.9
      },
      {
        data: buildAverageSeries(result.ema_200_series, ema200),
        color: EMA_BADGE_COLORS.ema200,
        width: 1.02,
        opacity: 0.86
      }
    ]
  }
}

function buildVwapBandsTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result: VWAPBandsResult = data?.vwap_bands ?? {
    signal: 'NEUTRAL',
    status: 'SEM_VWAP',
    value: null,
    vwap: null,
    upper_1: null,
    lower_1: null,
    upper_2: null,
    lower_2: null,
    price_series: [],
    vwap_series: [],
    upper_1_series: [],
    lower_1_series: [],
    upper_2_series: [],
    lower_2_series: []
  }

  const signal = toSignal(result.signal)
  const value = result.value ?? 100
  const vwap = result.vwap ?? value
  const upper1 = result.upper_1 ?? value * 1.01
  const lower1 = result.lower_1 ?? value * 0.99
  const upper2 = result.upper_2 ?? value * 1.02
  const lower2 = result.lower_2 ?? value * 0.98

  return {
    timeframe,
    signal,
    footerLabel: formatStatus(result.status),
    cloud: {
      upper: result.upper_1_series.length > 0 ? result.upper_1_series : buildAverageSeries([upper1], upper1),
      lower: result.lower_1_series.length > 0 ? result.lower_1_series : buildAverageSeries([lower1], lower1),
      color: 'hsl(var(--muted-foreground))',
      opacity: 0.1
    },
    series: [
      {
        data: result.price_series.length > 0 ? result.price_series : buildAverageSeries([value], value),
        color: getSignalColor(signal),
        width: 1.6
      },
      {
        data: result.vwap_series.length > 0 ? result.vwap_series : buildAverageSeries([vwap], vwap),
        color: 'hsl(var(--foreground))',
        width: 1.1,
        opacity: 0.95
      },
      {
        data: result.upper_2_series.length > 0 ? result.upper_2_series : buildAverageSeries([upper2], upper2),
        color: 'hsl(var(--bearish))',
        width: 0.9,
        dashed: true,
        opacity: 0.4
      },
      {
        data: result.upper_1_series.length > 0 ? result.upper_1_series : buildAverageSeries([upper1], upper1),
        color: 'hsl(var(--bearish))',
        width: 1,
        dashed: true,
        opacity: 0.72
      },
      {
        data: result.lower_1_series.length > 0 ? result.lower_1_series : buildAverageSeries([lower1], lower1),
        color: 'hsl(var(--bullish))',
        width: 1,
        dashed: true,
        opacity: 0.72
      },
      {
        data: result.lower_2_series.length > 0 ? result.lower_2_series : buildAverageSeries([lower2], lower2),
        color: 'hsl(var(--bullish))',
        width: 0.9,
        dashed: true,
        opacity: 0.4
      }
    ]
  }
}

function buildBbBreakoutTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result: BBBreakoutResult = data?.bb_breakout ?? {
    signal: 'NEUTRAL',
    status: 'DENTRO_DAS_BANDAS',
    value: null,
    upper: null,
    middle: null,
    lower: null,
    length: 20,
    std_dev: 3,
    price_series: [],
    upper_series: [],
    middle_series: [],
    lower_series: []
  }

  const signal = toSignal(result.signal)
  const value = result.value ?? 0
  const upper = result.upper ?? value + 2
  const middle = result.middle ?? value
  const lower = result.lower ?? value - 2
  const min = Math.min(value, upper, middle, lower) - 1
  const max = Math.max(value, upper, middle, lower) + 1

  return {
    timeframe,
    signal,
    footerLabel: formatStatus(result.status),
    cloud: {
      upper: result.upper_series.length > 0 ? result.upper_series : buildTrendSeries(upper, { min, max, phase: 0.6, trend: 0.08 }),
      lower: result.lower_series.length > 0 ? result.lower_series : buildTrendSeries(lower, { min, max, phase: 1.35, trend: 0.08 }),
      color: 'hsl(var(--muted-foreground))',
      opacity: 0.12
    },
    series: [
      {
        data: result.price_series.length > 0 ? result.price_series : buildTrendSeries(value, { min, max, phase: 0.2, trend: 0.16 }),
        color: getSignalColor(signal),
        width: 1.55
      },
      {
        data: result.upper_series.length > 0 ? result.upper_series : buildTrendSeries(upper, { min, max, phase: 0.55, trend: 0.05 }),
        color: 'hsl(var(--foreground))',
        width: 0.95,
        dashed: true,
        opacity: 0.72
      },
      {
        data: result.middle_series.length > 0 ? result.middle_series : buildTrendSeries(middle, { min, max, phase: 1.1, trend: 0.05 }),
        color: 'hsl(var(--foreground))',
        width: 0.9,
        dashed: true,
        opacity: 0.5
      },
      {
        data: result.lower_series.length > 0 ? result.lower_series : buildTrendSeries(lower, { min, max, phase: 1.65, trend: 0.05 }),
        color: 'hsl(var(--foreground))',
        width: 0.95,
        dashed: true,
        opacity: 0.72
      }
    ]
  }
}

function buildSupportResistanceTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result: SupportResistanceResult = data?.support_resistance ?? {
    signal: 'NEUTRAL',
    status: 'RANGE',
    support: null,
    resistance: null,
    value: null,
    price_series: []
  }
  const signal = toSignal(result.signal)
  const value = result.value ?? 0
  const support = result.support ?? value - 2
  const resistance = result.resistance ?? value + 2
  const min = Math.min(value, support, resistance) - 1
  const max = Math.max(value, support, resistance) + 1

  return {
    timeframe,
    signal,
    footerLabel: formatStatus(result.status),
    guideLines: [
      makeGuideLine(resistance, 'hsl(var(--bearish))', { opacity: 0.38, dashed: true, width: 1 }),
      makeGuideLine(support, 'hsl(var(--bullish))', { opacity: 0.38, dashed: true, width: 1 })
    ],
    series: [
      {
        data: result.price_series.length > 0 ? result.price_series : buildTrendSeries(value, { min, max, phase: 0.28, trend: 0.16 }),
        color: getSignalColor(signal)
      }
    ]
  }
}

function buildPivotPointTile(timeframe: IndicatorTimeframe, data: TimeframeIndicators | undefined): IndicatorTileViewModel {
  const result: PivotPointResult = data?.pivot_point ?? {
    signal: 'NEUTRAL',
    status: 'NO_PIVO',
    value: null,
    pivot: null,
    resistance_1: null,
    support_1: null,
    resistance_2: null,
    support_2: null,
    price_series: []
  }
  const signal = toSignal(result.signal)
  const value = result.value ?? 0
  const pivot = result.pivot ?? value
  const resistance1 = result.resistance_1 ?? value + 1
  const support1 = result.support_1 ?? value - 1
  const resistance2 = result.resistance_2 ?? value + 2
  const support2 = result.support_2 ?? value - 2
  const min = Math.min(value, pivot, support1, support2, resistance1, resistance2) - 1
  const max = Math.max(value, pivot, support1, support2, resistance1, resistance2) + 1

  return {
    timeframe,
    signal,
    footerLabel: formatStatus(result.status),
    guideLines: [
      makeGuideLine(resistance2, 'hsl(var(--bearish))', { opacity: 0.18, dashed: false, width: 0.9 }),
      makeGuideLine(resistance1, 'hsl(var(--bearish))', { opacity: 0.3, dashed: false, width: 1 }),
      makeGuideLine(pivot, 'hsl(var(--foreground))', { opacity: 0.45, dashed: false, width: 1.1 }),
      makeGuideLine(support1, 'hsl(var(--bullish))', { opacity: 0.3, dashed: false, width: 1 }),
      makeGuideLine(support2, 'hsl(var(--bullish))', { opacity: 0.18, dashed: false, width: 0.9 })
    ],
    series: [
      {
        data: result.price_series.length > 0 ? result.price_series : buildTrendSeries(value, { min, max, phase: 0.36, trend: 0.14 }),
        color: getSignalColor(signal)
      }
    ]
  }
}

function buildTileViewModel(indicator: IndicatorName, timeframe: IndicatorTimeframe, values: TimeframeIndicators | undefined): IndicatorTileViewModel {
  if (indicator === 'williams_r') {
    return buildWilliamsRTile(timeframe, values)
  }

  if (indicator === 'macd') {
    return buildMacdTile(timeframe, values)
  }

  if (indicator === 'adx') {
    return buildAdxTile(timeframe, values)
  }

  if (indicator === 'bb_breakout') {
    return buildBbBreakoutTile(timeframe, values)
  }

  if (indicator === 'support_resistance') {
    return buildSupportResistanceTile(timeframe, values)
  }

  if (indicator === 'moving_average_cross') {
    return buildMovingAverageCrossTile(timeframe, values)
  }

  if (indicator === 'vwap_bands') {
    return buildVwapBandsTile(timeframe, values)
  }

  return buildPivotPointTile(timeframe, values)
}

function IndicatorCardComponent({ indicator, values, timeframes, className }: IndicatorCardProps) {
  const meta = INDICATOR_META[indicator]
  const tiles = useMemo(() => timeframes.map(timeframe => buildTileViewModel(indicator, timeframe, values[timeframe])), [indicator, timeframes, values])
  const isMovingAverageCross = indicator === 'moving_average_cross'

  return (
    <Card className={cn('shadow-card border-border gap-4 border', className)}>
      <CardHeader className="gap-0.5">
        <CardTitle>{meta.short}</CardTitle>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-2">
          {tiles.map(tile => (
            <section key={tile.timeframe} className="border-border/60 bg-muted/20 shadow-xs min-h-35 flex flex-col rounded-xl border p-2">
              <div className="mb-2 flex items-center justify-between gap-2">
                <span className="text-muted-foreground font-mono text-[10px] font-semibold uppercase">{tile.timeframe}</span>
                <SignalBadge signal={tile.signal} />
              </div>

              <div className="mb-1.5 min-h-12 flex-1">
                <MiniChart
                  width={160}
                  height={64}
                  guideLines={tile.guideLines}
                  zeroLine={tile.zeroLine}
                  histogram={tile.histogram}
                  histogramSignal={tile.signal}
                  cloud={tile.cloud}
                  series={tile.series}
                  className="w-full"
                />
              </div>

              <p className={cn('text-foreground/90 truncate font-mono text-xs font-semibold tracking-tight')} title={tile.footerLabel}>
                {tile.footerLabel}
              </p>
            </section>
          ))}
        </div>
      </CardContent>
      <CardFooter>
        {isMovingAverageCross ? (
          <CardDescription className="space-x-2">
            <LegendBadge label="EMA 9" color={EMA_BADGE_COLORS.ema9} />
            <LegendBadge label="EMA 21" color={EMA_BADGE_COLORS.ema21} />
            <LegendBadge label="EMA 55" color={EMA_BADGE_COLORS.ema55} />
            <LegendBadge label="EMA 200" color={EMA_BADGE_COLORS.ema200} />
          </CardDescription>
        ) : (
          <CardDescription>{meta.name}</CardDescription>
        )}
      </CardFooter>
    </Card>
  )
}

export const IndicatorCard = memo(IndicatorCardComponent)
