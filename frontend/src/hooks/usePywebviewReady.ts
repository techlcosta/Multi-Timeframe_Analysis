import { useEffect, useState } from 'react'

export function usePywebviewReady(): boolean {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    function checkReady() {
      if (window.pywebview?.api) {
        setIsReady(true)
      }
    }

    checkReady()
    window.addEventListener('pywebviewready', checkReady)

    return () => {
      window.removeEventListener('pywebviewready', checkReady)
    }
  }, [])

  return isReady
}
