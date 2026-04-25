/* eslint-disable react-refresh/only-export-components */
import { memo, useMemo } from 'react'

import type { Signal } from './signalBadge'

interface ChartSeries {
  data: number[]
  color: string
  width?: number
  dashed?: boolean
  opacity?: number
}

interface CloudArea {
  upper: number[]
  lower: number[]
  color: string
  opacity?: number
}

interface GuideLine {
  value: number
  color?: string
  opacity?: number
  dashed?: boolean
  width?: number
}

interface MiniChartProps {
  series: ChartSeries[]
  width?: number
  height?: number
  guideLines?: GuideLine[]
  zeroLine?: boolean
  histogram?: number[]
  histogramSignal?: Signal
  cloud?: CloudArea
  className?: string
}

function getSignalColor(signal: Signal): string {
  if (signal === 'BUY') {
    return 'hsl(var(--bullish))'
  }

  if (signal === 'SELL') {
    return 'hsl(var(--bearish))'
  }

  return 'hsl(var(--muted-foreground))'
}

function normalizeSeries(values: number[][], height: number, paddingY = 5) {
  const flat = values.flat().filter(value => Number.isFinite(value))
  const min = flat.length > 0 ? Math.min(...flat) : 0
  const max = flat.length > 0 ? Math.max(...flat) : 1
  const range = max - min || 1
  const usableHeight = height - paddingY * 2

  return {
    mapY: (value: number) => paddingY + usableHeight - ((value - min) / range) * usableHeight
  }
}

function buildCoordinates(data: number[], width: number, mapY: (value: number) => number, paddingX = 4) {
  if (data.length === 0) {
    return []
  }

  if (data.length === 1) {
    return [
      { x: paddingX, y: mapY(data[0]) },
      { x: width - paddingX, y: mapY(data[0]) }
    ]
  }

  const usableWidth = width - paddingX * 2
  const stepX = usableWidth / (data.length - 1)

  return data.map((value, index) => ({
    x: paddingX + index * stepX,
    y: mapY(value)
  }))
}

function buildLinePath(data: number[], width: number, mapY: (value: number) => number, paddingX = 4) {
  const points = buildCoordinates(data, width, mapY, paddingX)
  if (points.length === 0) {
    return ''
  }

  return points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ')
}

function buildAreaPath(upper: number[], lower: number[], width: number, mapY: (value: number) => number) {
  const upperPoints = buildCoordinates(upper, width, mapY)
  const lowerPoints = buildCoordinates(lower, width, mapY).reverse()

  if (upperPoints.length === 0 || lowerPoints.length === 0) {
    return ''
  }

  const path = [
    `M ${upperPoints[0].x} ${upperPoints[0].y}`,
    ...upperPoints.slice(1).map(point => `L ${point.x} ${point.y}`),
    ...lowerPoints.map(point => `L ${point.x} ${point.y}`),
    'Z'
  ]

  return path.join(' ')
}

function MiniChartComponent({ series, width = 150, height = 48, guideLines, zeroLine, histogram, histogramSignal = 'NEUTRAL', cloud, className }: MiniChartProps) {
  const normalized = useMemo(() => {
    const sourceValues = [
      ...series.map(item => item.data),
      ...(histogram ? [histogram] : []),
      ...(guideLines ? [guideLines.map(item => item.value)] : []),
      ...(cloud ? [cloud.upper, cloud.lower] : []),
      ...(zeroLine ? [[0]] : [])
    ]

    return normalizeSeries(sourceValues, height)
  }, [cloud, guideLines, height, histogram, series, zeroLine])

  const histogramRects = useMemo(() => {
    if (!histogram || histogram.length === 0) {
      return []
    }

    const paddingX = 4
    const usableWidth = width - paddingX * 2
    const step = usableWidth / histogram.length
    const barWidth = Math.max(1.1, Math.min(4, step * 0.46))

    return histogram.map((value, index) => {
      const yZero = normalized.mapY(0)
      const yValue = normalized.mapY(value)
      const x = paddingX + index * step + (step - barWidth) / 2

      return {
        x,
        y: Math.min(yZero, yValue),
        width: barWidth,
        height: Math.max(0.8, Math.abs(yValue - yZero)),
        positive: value >= 0
      }
    })
  }, [histogram, normalized, width])

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} className={className} aria-hidden="true">
      {guideLines?.map(line => (
        <line
          key={`guide-${line.value}`}
          x1={4}
          x2={width - 4}
          y1={normalized.mapY(line.value)}
          y2={normalized.mapY(line.value)}
          stroke={line.color ?? 'hsl(var(--muted-foreground))'}
          strokeOpacity={line.opacity ?? 0.22}
          strokeDasharray={(line.dashed ?? true) ? '2 3' : undefined}
          strokeWidth={line.width ?? 0.9}
        />
      ))}

      {zeroLine ? <line x1={4} x2={width - 4} y1={normalized.mapY(0)} y2={normalized.mapY(0)} stroke="hsl(var(--border))" strokeOpacity={0.75} strokeWidth={0.9} /> : null}

      {cloud ? (
        <>
          <path d={buildAreaPath(cloud.upper, cloud.lower, width, normalized.mapY)} fill={cloud.color} fillOpacity={cloud.opacity ?? 0.14} />
          <path d={buildLinePath(cloud.upper, width, normalized.mapY)} fill="none" stroke={cloud.color} strokeOpacity={0.45} strokeWidth={1} />
          <path d={buildLinePath(cloud.lower, width, normalized.mapY)} fill="none" stroke={cloud.color} strokeOpacity={0.22} strokeWidth={1} />
        </>
      ) : null}

      {histogramRects.map((rect, index) => (
        <rect
          key={`bar-${index}`}
          x={rect.x}
          y={rect.y}
          width={rect.width}
          height={rect.height}
          rx={0.6}
          fill={rect.positive ? 'hsl(var(--bullish))' : 'hsl(var(--bearish))'}
          fillOpacity={histogramSignal === 'NEUTRAL' ? 0.5 : 0.72}
        />
      ))}

      {series.map((item, index) => (
        <path
          key={`series-${index}`}
          d={buildLinePath(item.data, width, normalized.mapY)}
          fill="none"
          stroke={item.color}
          strokeOpacity={item.opacity ?? 1}
          strokeWidth={item.width ?? 1.65}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={item.dashed ? '2.8 2.2' : undefined}
        />
      ))}
    </svg>
  )
}

export const MiniChart = memo(MiniChartComponent)
export { getSignalColor }
