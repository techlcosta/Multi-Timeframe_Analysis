import type { IndicatorsResponseData } from '@/types/api/indicators'
import { useQuery, type UseQueryResult } from '@tanstack/react-query'

import { unwrapApiResponse } from '@/lib/api'

import { usePywebviewReady } from './usePywebviewReady'

export function useIndicators(bars = 200): UseQueryResult<IndicatorsResponseData, Error> {
  const isReady = usePywebviewReady()

  const query = useQuery<IndicatorsResponseData, Error>({
    queryKey: ['indicators', bars],
    queryFn: async (): Promise<IndicatorsResponseData> => {
      const response = await window.pywebview.api.indicators(bars)
      return unwrapApiResponse(response)
    },
    refetchInterval: 2000,
    staleTime: 3000,
    retry: 3,
    gcTime: 0,
    enabled: isReady
  })

  return query
}
