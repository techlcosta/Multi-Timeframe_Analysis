import { Settings2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle, DrawerTrigger } from '@/components/ui/drawer'
import { useSymbols } from '@/hooks/useSymbols'
import { cn } from '@/lib/utils'
import { CardSymbol } from './cardSymbol'
import { SymbolSelector } from './symbolSelector'

export function Settings() {
  const { data: symbols = [] } = useSymbols()

  return (
    <Drawer direction="right">
      <DrawerTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          type="button"
          aria-label="Open settings"
          title="Settings"
          className={cn('border-border/70 bg-background/70 shadow-card hover:shadow-card-hover relative h-11 w-11 cursor-pointer rounded-full backdrop-blur-sm transition-all')}
        >
          <Settings2 className="h-5 w-5" />
          <span className="sr-only">Settings</span>
        </Button>
      </DrawerTrigger>

      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Settings</DrawerTitle>
          <DrawerDescription>Settings panel and symbol management.</DrawerDescription>
        </DrawerHeader>

        <div className="space-y-4 px-4 pb-4">
          <SymbolSelector symbols={symbols} />
          <CardSymbol symbols={symbols} />
        </div>
      </DrawerContent>
    </Drawer>
  )
}
