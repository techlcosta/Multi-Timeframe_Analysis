import type { APIResponse, SavedSymbol } from './shared'

export type FechSymbolsFunction = () => Promise<APIResponse<SavedSymbol[]>>
