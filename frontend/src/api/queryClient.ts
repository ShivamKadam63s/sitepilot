import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,       // data is fresh for 30s
      retry: 1,                // retry once on failure
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
})
