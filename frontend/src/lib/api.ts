import type { APIResponse } from '@/types/api/shared'

export function unwrapApiResponse<T>(response: APIResponse<T>): T {
  if (response.ok && response.data !== null) {
    return response.data
  }

  if (response.error?.mt5_error?.message) {
    throw new Error(`${response.code}: ${response.error.mt5_error.message}`)
  }

  throw new Error(response.error?.message ?? response.code)
}
