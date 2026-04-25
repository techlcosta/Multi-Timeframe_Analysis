import { Check, Plus, Search } from 'lucide-react'
import { useDeferredValue, useMemo, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { useMutationSymbol } from '@/hooks/mutationSymbol'
import { useMTSymbols } from '@/hooks/useMTSymbols'
import { cn } from '@/lib/utils'
import type { MtSymbolRecord } from '@/types/api/mt-symbols'
import type { SavedSymbol } from '@/types/api/shared'

interface SymbolSelectorProps {
  symbols: SavedSymbol[]
}

function getSymbolName(symbol: MtSymbolRecord): string {
  const rawName = symbol.name
  return typeof rawName === 'string' ? rawName : ''
}

export function SymbolSelector({ symbols }: SymbolSelectorProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const { data: mtSymbols = [], isLoading, isFetching, isError, error } = useMTSymbols()
  const { mutate, isPending } = useMutationSymbol()
  const deferredQuery = useDeferredValue(query)

  const savedSymbolNames = useMemo(() => new Set(symbols.map(symbol => symbol.name)), [symbols])

  const filtered = useMemo(
    () =>
      mtSymbols.filter(symbol => {
        const symbolName = getSymbolName(symbol)
        return symbolName.toLowerCase().includes(deferredQuery.toLowerCase())
      }),
    [deferredQuery, mtSymbols]
  )

  function handleAdd(symbol: MtSymbolRecord) {
    const symbolName = getSymbolName(symbol)

    if (!symbolName || savedSymbolNames.has(symbolName) || isPending) {
      return
    }

    mutate({
      name: symbolName,
      path: typeof symbol.path === 'string' ? symbol.path : undefined,
      description: typeof symbol.description === 'string' ? symbol.description : undefined,
      currency_base: typeof symbol.currency_base === 'string' ? symbol.currency_base : undefined,
      currency_profit: typeof symbol.currency_profit === 'string' ? symbol.currency_profit : undefined
    })
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="h-9 w-full cursor-pointer gap-2">
          <Plus className="h-4 w-4" />
          Add symbol
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-(--radix-popover-trigger-width) min-w-(--radix-popover-trigger-width) p-0" align="start">
        <div className="border-b p-2">
          <div className="relative">
            <Search className="text-muted-foreground absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2" />
            <Input placeholder="Search symbol..." value={query} onChange={event => setQuery(event.target.value)} className="h-8 pl-8" />
          </div>
        </div>

        <div className="max-h-72 overflow-y-auto p-1">
          {(isLoading || isFetching) && <p className="text-muted-foreground py-6 text-center text-sm">Loading symbols...</p>}

          {isError && <p className="text-muted-foreground py-6 text-center text-sm">Could not load symbols. {error?.message}</p>}

          {filtered.map(symbol => {
            const symbolName = getSymbolName(symbol)

            if (!symbolName) {
              return null
            }

            const isSaved = savedSymbolNames.has(symbolName)
            const isDisabled = isSaved || isPending

            return (
              <button
                key={symbolName}
                type="button"
                disabled={isDisabled}
                onClick={() => handleAdd(symbol)}
                className={cn(
                  'group flex w-full cursor-pointer items-center justify-between rounded-md px-2 py-1.5 font-mono text-sm transition',
                  isDisabled ? 'cursor-not-allowed opacity-70' : 'hover:bg-accent',
                  isSaved && 'text-primary'
                )}
              >
                <span>{symbolName}</span>
                <Check className={cn('h-4 w-4 transition-opacity', isSaved ? 'text-primary opacity-100' : 'text-muted-foreground opacity-0 group-hover:opacity-100')} />
              </button>
            )
          })}

          {!isLoading && !isFetching && !isError && filtered.length === 0 && <p className="text-muted-foreground py-6 text-center text-sm">No symbols found</p>}
        </div>
      </PopoverContent>
    </Popover>
  )
}
