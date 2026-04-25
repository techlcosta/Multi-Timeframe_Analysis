import { Trash } from 'lucide-react'
import { memo } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useMutationRemoveSymbol } from '@/hooks/mutationRemoveSymbol'
import { cn } from '@/lib/utils'
import type { SavedSymbol } from '@/types/api/shared'

interface CardSymbolProps {
  symbols: SavedSymbol[]
}

function CardSymbolComponent({ symbols }: CardSymbolProps) {
  const { mutate, isPending, variables } = useMutationRemoveSymbol()

  function handleRemove(name: string) {
    if (!name || isPending) {
      return
    }

    mutate(name)
  }

  return (
    <Card size="sm" className="border-border/70 bg-card/70 shadow-xs">
      <CardHeader className="border-border/60 border-b">
        <CardTitle>Symbols</CardTitle>
        <CardDescription>
          {symbols.length > 0 ? `${symbols.length} simbolo${symbols.length > 1 ? 's' : ''} salvo${symbols.length > 1 ? 's' : ''}` : 'Nenhum simbolo salvo ainda.'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        {symbols.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {symbols.map(symbol => {
              const isRemoving = isPending && variables === symbol.name

              return (
                <Badge key={symbol.name} variant="outline" className={cn('border-border bg-background/80 h-auto gap-1.5 py-1 pl-3 pr-2 text-sm', isRemoving && 'opacity-70')}>
                  <span className="font-mono">{symbol.name}</span>
                  <Button
                    variant="ghost"
                    size="icon-xs"
                    type="button"
                    aria-label={`Remover simbolo ${symbol.name}`}
                    title={`Remover ${symbol.name}`}
                    disabled={isRemoving}
                    onClick={() => handleRemove(symbol.name)}
                    className="text-muted-foreground size-4 cursor-pointer rounded-full p-0 hover:text-red-500"
                  >
                    <Trash className="size-3" />
                  </Button>
                </Badge>
              )
            })}
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">Adicione simbolos no seletor acima para comecar.</p>
        )}
      </CardContent>
    </Card>
  )
}

export const CardSymbol = memo(CardSymbolComponent)
