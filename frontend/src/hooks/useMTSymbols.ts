import type { MtSymbolRecord } from '@/types/api/mt-symbols'
import { useQuery, type UseQueryResult } from '@tanstack/react-query'

import { unwrapApiResponse } from '@/lib/api'

import { usePywebviewReady } from './usePywebviewReady'

export function useMTSymbols(group?: string): UseQueryResult<MtSymbolRecord[], Error> {
  const isReady = usePywebviewReady()

  const query = useQuery<MtSymbolRecord[], Error>({
    queryKey: ['mt_symbols', group ?? 'all'],
    queryFn: async (): Promise<MtSymbolRecord[]> => {
      const response = group ? await window.pywebview.api.mt_symbols(group) : await window.pywebview.api.mt_symbols()
      return unwrapApiResponse(response)
    },
    // refetchInterval: 5000,
    staleTime: 3000,
    retry: 3,
    gcTime: 0,
    enabled: isReady
  })

  return query
}
