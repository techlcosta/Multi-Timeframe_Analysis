import type { APIResponse } from './shared'

export type MtSymbolRecord = Record<string, unknown>

export type MtSymbolsFunction = (group?: string) => Promise<APIResponse<MtSymbolRecord[]>>
