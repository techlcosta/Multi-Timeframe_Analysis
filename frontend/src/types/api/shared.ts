export interface APIResponse<T> {
  ok: boolean
  code: string
  data: T | null
  error: APIErrorPayload | null
}

export interface APIMT5Error {
  code: number
  message: string
}

export interface APIErrorPayload {
  message: string
  mt5_error?: APIMT5Error | null
}

export interface SavedSymbol {
  name: string
  path: string
  description: string
  currency_base: string
  currency_profit: string
  created_at: string | null
  updated_at: string | null
}

export interface SymbolPayload {
  name: string
  path?: string
  description?: string
  currency_base?: string
  currency_profit?: string
}
