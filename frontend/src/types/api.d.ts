import type { AddSymbolFunction } from './api/add-symbol'
import type { FechSymbolsFunction } from './api/fech-symbols'
import type { IndicatorsFunction } from './api/indicators'
import type { MtSymbolsFunction } from './api/mt-symbols'
import type { RemoveSymbolFunction } from './api/remove-symbol'

interface API {
  mt_symbols: MtSymbolsFunction
  fech_symbols: FechSymbolsFunction
  indicators: IndicatorsFunction
  add_symbol: AddSymbolFunction
  remove_symbol: RemoveSymbolFunction
}

declare global {
  interface Window {
    pywebview: {
      api: API
    }
  }
}
