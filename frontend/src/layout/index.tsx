import { useMemo, useState } from 'react'

import dark from '@/assets/logo.svg'
import { IndicatorCard } from '@/components/indicatorCard'
import { Settings } from '@/components/settings'
import { ThemeToggle } from '@/components/themeToogle'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Toggle } from '@/components/ui/toggle'
import { useIndicators } from '@/hooks/useIndicators'
import type { IndicatorName } from '@/types/api/indicators'

export function Layout() {
  const { data, isLoading, isError, error } = useIndicators()
  const [selectedSymbolKey, setSelectedSymbolKey] = useState<string | null>(null)
  const symbolEntries = useMemo(() => Object.entries(data?.symbols ?? {}), [data?.symbols])
  const defaultSymbolEntry = symbolEntries[0]
  const selectedSymbolEntry = symbolEntries.find(([symbolName]) => symbolName === selectedSymbolKey) ?? defaultSymbolEntry
  const selectedSymbolName = selectedSymbolEntry?.[0]
  const selectedSymbolValues = selectedSymbolEntry?.[1]
  const timeframes = data?.timeframes ?? []
  const indicatorNames = (data?.indicators.map(item => item.name) ?? []) as IndicatorName[]

  return (
    <main className="grid h-screen w-full grid-rows-[auto_minmax(0,1fr)] overflow-hidden">
      <header className="border-b backdrop-blur-md">
        <div className="flex items-center justify-between gap-4 px-6 py-1">
          <div className="flex items-center gap-2">
            <img className="h-16" src={dark} alt="" />
            <div className="leading-tight">
              <h1 className="text-2xl font-bold tracking-wider">Strategies</h1>
              <p className="text-muted-foreground text-xs uppercase tracking-wider">Multi-timeframe Analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Settings />
            <ThemeToggle />
          </div>
        </div>
      </header>

      <section className="min-h-0">
        <ScrollArea className="h-full">
          <div className="px-6 py-5">
            {isLoading ? <div className="text-muted-foreground text-sm">Loading indicators...</div> : null}

            {isError ? <div className="text-destructive text-sm">Could not load indicators. {error?.message}</div> : null}

            {!isLoading && !isError && !selectedSymbolValues ? <div className="text-muted-foreground text-sm">No saved symbol available for analysis.</div> : null}

            {!isLoading && !isError && selectedSymbolValues ? (
              <div className="space-y-4">
                <div className="space-y-3">
                  <div className="flex flex-wrap gap-2">
                    {symbolEntries.map(([symbolName]) => (
                      <Toggle
                        key={symbolName}
                        pressed={selectedSymbolName === symbolName}
                        variant="outline"
                        size="sm"
                        type="button"
                        aria-label={`Select symbol ${symbolName}`}
                        onPressedChange={pressed => {
                          if (pressed) {
                            setSelectedSymbolKey(symbolName)
                          }
                        }}
                        className="cursor-pointer font-mono text-xs"
                      >
                        {symbolName}
                      </Toggle>
                    ))}
                  </div>

                  <h2 className="text-lg font-semibold tracking-tight">{selectedSymbolName}</h2>
                  <p className="text-muted-foreground text-sm">Multi-timeframe indicators based on the latest MetaTrader 5 data.</p>
                </div>

                <div className="grid grid-cols-2 gap-4 md:grid-cols-3 2xl:grid-cols-4">
                  {indicatorNames.map(indicator => (
                    <IndicatorCard key={indicator} indicator={indicator} values={selectedSymbolValues} timeframes={timeframes} />
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </ScrollArea>
      </section>
    </main>
  )
}
