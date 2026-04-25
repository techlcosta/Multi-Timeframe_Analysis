import type { SavedSymbol, SymbolPayload } from '@/types/api/shared'
import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query'

import { unwrapApiResponse } from '@/lib/api'

import { usePywebviewReady } from './usePywebviewReady'

export function useMutationSymbol(): UseMutationResult<SavedSymbol, Error, SymbolPayload> {
  const isReady = usePywebviewReady()
  const queryClient = useQueryClient()

  const mutation = useMutation<SavedSymbol, Error, SymbolPayload>({
    mutationFn: async (symbolData: SymbolPayload): Promise<SavedSymbol> => {
      if (!isReady) {
        throw new Error('PYWEBVIEW_API_NOT_READY')
      }

      const response = await window.pywebview.api.add_symbol(symbolData)
      return unwrapApiResponse(response)
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['symbols', 'saved'] })
    }
  })

  return mutation
}
