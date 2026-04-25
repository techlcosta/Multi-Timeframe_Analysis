import type { APIResponse } from './shared'

export type IndicatorTimeframe = 'M1' | 'M5' | 'M15' | 'M30'
export type IndicatorSignal = 'BUY' | 'SELL' | 'NEUTRAL'
export type IndicatorName = 'bb_breakout' | 'support_resistance' | 'pivot_point' | 'macd' | 'adx' | 'williams_r' | 'moving_average_cross' | 'vwap_bands'

export interface IndicatorConfig {
  name: IndicatorName
  params: Record<string, number>
}

export interface WilliamsRResult {
  value: number | null
  length: number
  series: number[]
}

export interface MACDResult {
  value: number | null
  signal: number | null
  histogram: number | null
  fast: number
  slow: number
  signal_period: number
  macd_series: number[]
  signal_series: number[]
  histogram_series: number[]
}

export interface ADXResult {
  value: number | null
  plus_di: number | null
  minus_di: number | null
  length: number
  adx_series: number[]
  plus_di_series: number[]
  minus_di_series: number[]
}

export interface BBBreakoutResult {
  signal: IndicatorSignal
  status: string
  value: number | null
  upper: number | null
  middle: number | null
  lower: number | null
  length: number
  std_dev: number
  price_series: number[]
  upper_series: number[]
  middle_series: number[]
  lower_series: number[]
}

export interface SupportResistanceResult {
  signal: IndicatorSignal
  status: string
  support: number | null
  resistance: number | null
  value: number | null
  price_series: number[]
}

export interface PivotPointResult {
  signal: IndicatorSignal
  status: string
  value: number | null
  pivot: number | null
  resistance_1: number | null
  support_1: number | null
  resistance_2: number | null
  support_2: number | null
  price_series: number[]
}

export interface MovingAverageCrossResult {
  signal: IndicatorSignal
  status: string
  value: number | null
  ema_9: number | null
  ema_21: number | null
  ema_55: number | null
  ema_200: number | null
  price_series: number[]
  ema_9_series: number[]
  ema_21_series: number[]
  ema_55_series: number[]
  ema_200_series: number[]
}

export interface VWAPBandsResult {
  signal: IndicatorSignal
  status: string
  value: number | null
  vwap: number | null
  upper_1: number | null
  lower_1: number | null
  upper_2: number | null
  lower_2: number | null
  price_series: number[]
  vwap_series: number[]
  upper_1_series: number[]
  lower_1_series: number[]
  upper_2_series: number[]
  lower_2_series: number[]
}

export interface TimeframeIndicators {
  williams_r: WilliamsRResult
  macd: MACDResult
  adx: ADXResult
  bb_breakout: BBBreakoutResult
  support_resistance: SupportResistanceResult
  pivot_point: PivotPointResult
  moving_average_cross: MovingAverageCrossResult
  vwap_bands: VWAPBandsResult
}

export type IndicatorsByTimeframe = Partial<Record<IndicatorTimeframe, TimeframeIndicators>>
export type IndicatorsSnapshot = Record<string, IndicatorsByTimeframe>

export interface IndicatorsResponseData {
  timeframes: IndicatorTimeframe[]
  indicators: IndicatorConfig[]
  symbols: IndicatorsSnapshot
}

export type IndicatorsFunction = (bars?: number) => Promise<APIResponse<IndicatorsResponseData>>
