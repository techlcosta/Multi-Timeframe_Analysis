import { useMutation, useQueryClient, type UseMutationResult } from '@tanstack/react-query'

import { unwrapApiResponse } from '@/lib/api'

import { usePywebviewReady } from './usePywebviewReady'

export function useMutationRemoveSymbol(): UseMutationResult<
  boolean,
  Error,
  string
> {
  const isReady = usePywebviewReady()
  const queryClient = useQueryClient()

  const mutation = useMutation<boolean, Error, string>({
    mutationFn: async (symbol: string): Promise<boolean> => {
      if (!isReady) {
        throw new Error('PYWEBVIEW_API_NOT_READY')
      }

      const response = await window.pywebview.api.remove_symbol(symbol)
      return unwrapApiResponse(response)
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['symbols', 'saved'] })
    },
  })

  return mutation
}
