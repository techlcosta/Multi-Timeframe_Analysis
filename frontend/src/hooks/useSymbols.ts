import type { SavedSymbol } from '@/types/api/shared'
import { useQuery, type UseQueryResult } from '@tanstack/react-query'

import { unwrapApiResponse } from '@/lib/api'

import { usePywebviewReady } from './usePywebviewReady'

export function useSymbols(): UseQueryResult<SavedSymbol[], Error> {
  const isReady = usePywebviewReady()

  const query = useQuery<SavedSymbol[], Error>({
    queryKey: ['symbols', 'saved'],
    queryFn: async (): Promise<SavedSymbol[]> => {
      const response = await window.pywebview.api.fech_symbols()
      return unwrapApiResponse(response)
    },
    refetchInterval: 5000,
    staleTime: 3000,
    retry: 3,
    gcTime: 0,
    enabled: isReady
  })

  return query
}
