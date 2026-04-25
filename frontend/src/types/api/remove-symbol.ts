import type { APIResponse } from './shared'

export type RemoveSymbolFunction = (symbol: string) => Promise<APIResponse<boolean>>
