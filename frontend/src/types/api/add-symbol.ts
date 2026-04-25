import type { APIResponse, SavedSymbol, SymbolPayload } from './shared'

export type AddSymbolFunction = (symbolData: SymbolPayload) => Promise<APIResponse<SavedSymbol>>
