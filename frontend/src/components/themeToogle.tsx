import { MoonStar, SunMedium } from 'lucide-react'
import { useEffect, useEffectEvent, useState } from 'react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type ThemePreference = 'dark' | 'light' | 'system'

const THEME_STORAGE_KEY = 'theme'
const DARK_THEME_CLASS = 'dark'
const SYSTEM_THEME_QUERY = '(prefers-color-scheme: dark)'

function getStoredThemePreference(): ThemePreference {
  if (typeof window === 'undefined') {
    return 'system'
  }

  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY)
  return savedTheme === 'dark' || savedTheme === 'light' ? savedTheme : 'system'
}

function getSystemPrefersDark(): boolean {
  if (typeof window === 'undefined') {
    return false
  }

  return window.matchMedia(SYSTEM_THEME_QUERY).matches
}

function resolveTheme(preference: ThemePreference, systemPrefersDark: boolean): 'dark' | 'light' {
  if (preference === 'system') {
    return systemPrefersDark ? 'dark' : 'light'
  }

  return preference
}

export function ThemeToggle() {
  const [themePreference, setThemePreference] = useState<ThemePreference>(getStoredThemePreference)
  const [systemPrefersDark, setSystemPrefersDark] = useState<boolean>(getSystemPrefersDark)

  const currentTheme = resolveTheme(themePreference, systemPrefersDark)
  const isDark = currentTheme === 'dark'

  const syncThemeWithDom = useEffectEvent((nextTheme: 'dark' | 'light') => {
    const root = document.documentElement

    root.classList.toggle(DARK_THEME_CLASS, nextTheme === 'dark')
    root.style.colorScheme = nextTheme
  })

  useEffect(() => {
    syncThemeWithDom(currentTheme)

    if (themePreference === 'system') {
      window.localStorage.removeItem(THEME_STORAGE_KEY)
      return
    }

    window.localStorage.setItem(THEME_STORAGE_KEY, themePreference)
  }, [currentTheme, themePreference])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const mediaQuery = window.matchMedia(SYSTEM_THEME_QUERY)
    const updateThemeFromSystem = (event: MediaQueryListEvent) => {
      setSystemPrefersDark(event.matches)
    }

    mediaQuery.addEventListener('change', updateThemeFromSystem)

    return () => {
      mediaQuery.removeEventListener('change', updateThemeFromSystem)
    }
  }, [])

  const nextTheme = isDark ? 'light' : 'dark'
  const actionLabel = nextTheme === 'dark' ? 'Enable dark theme' : 'Enable light theme'

  return (
    <Button
      variant="outline"
      size="icon"
      type="button"
      onClick={() => setThemePreference(nextTheme)}
      aria-label={actionLabel}
      aria-pressed={isDark}
      title={actionLabel}
      className={cn('border-border/70 bg-background/70 shadow-card hover:shadow-card-hover group relative h-11 w-11 cursor-pointer rounded-full backdrop-blur-sm transition-all')}
    >
      <SunMedium className={cn('absolute h-5 w-5 text-amber-500 transition-all duration-300', isDark ? 'rotate-0 scale-100 opacity-100' : 'rotate-90 scale-0 opacity-0')} />
      <MoonStar className={cn('absolute h-5 w-5 text-sky-500 transition-all duration-300', isDark ? '-rotate-90 scale-0 opacity-0' : 'rotate-0 scale-100 opacity-100')} />
      <span className="sr-only">{actionLabel}</span>
    </Button>
  )
}
