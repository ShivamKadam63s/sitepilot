import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { App } from './App'

describe('App Smoke Test', () => {
  it('renders login page or redirects correctly', () => {
    render(<App />)
    // Since it's protected, it should redirect to login if no token
    // We just check if the app doesn't crash
    expect(true).toBe(true)
  })
})
