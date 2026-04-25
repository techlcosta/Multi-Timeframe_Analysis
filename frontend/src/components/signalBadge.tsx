import { ArrowDown, ArrowUp, Minus } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export type Signal = 'BUY' | 'SELL' | 'NEUTRAL'

interface SignalBadgeProps {
  signal: Signal
  size?: 'sm' | 'md'
  showIcon?: boolean
  label?: string
  className?: string
}

const signalStyles: Record<Signal, string> = {
  BUY: 'border-bullish/20 bg-bullish-soft text-bullish',
  SELL: 'border-bearish/20 bg-bearish-soft text-bearish',
  NEUTRAL: 'border-border bg-neutral-soft text-neutral',
}

const signalIcons = {
  BUY: ArrowUp,
  SELL: ArrowDown,
  NEUTRAL: Minus,
} satisfies Record<Signal, typeof ArrowUp>

export function SignalBadge({
  signal,
  size = 'sm',
  showIcon = true,
  label,
  className,
}: SignalBadgeProps) {
  const Icon = signalIcons[signal]

  return (
    <Badge
      variant="outline"
      className={cn(
        'rounded-md font-mono font-semibold tracking-wide uppercase',
        size === 'sm' ? 'h-6 gap-1 px-1.5 text-[10px]' : 'h-7 gap-1.5 px-2 text-[11px]',
        signalStyles[signal],
        className
      )}
    >
      {showIcon ? (
        <Icon
          className={size === 'sm' ? 'h-2.5 w-2.5' : 'h-3 w-3'}
          strokeWidth={3}
        />
      ) : null}
      {label ?? signal}
    </Badge>
  )
}
