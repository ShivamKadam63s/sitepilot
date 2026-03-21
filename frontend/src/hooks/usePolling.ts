import { useEffect, useRef } from 'react'

interface UsePollingOptions {
  intervalMs?: number
  enabled?: boolean
}

/**
 * Calls `fn` immediately and then every `intervalMs` milliseconds.
 * Automatically clears the interval when the component unmounts or
 * when `enabled` becomes false.
 */
export function usePolling(
  fn: () => void | Promise<void>,
  { intervalMs = 5000, enabled = true }: UsePollingOptions = {}
) {
  const fnRef = useRef(fn)
  fnRef.current = fn

  useEffect(() => {
    if (!enabled) return

    void fnRef.current()
    const id = setInterval(() => void fnRef.current(), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs, enabled])
}
