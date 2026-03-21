// ─── User & Auth ────────────────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  role: 'owner' | 'admin' | 'editor'
  tenantId: string
  name: string
}

export interface Tenant {
  id: string
  name: string
  plan: 'free' | 'pro' | 'enterprise'
  sitesAllowed: number
  sitesUsed: number
  storageUsedMb: number
  storageLimitMb: number
}

export interface AuthResponse {
  accessToken: string
  tokenType: string
  user: User
  tenant: Tenant
}

// ─── Sites ───────────────────────────────────────────────────────────────────

export type Framework =
  | 'react'
  | 'vue'
  | 'flask'
  | 'fastapi'
  | 'static'
  | 'nextjs'
  | 'unknown'

export type SiteStatus = 'draft' | 'deploying' | 'live' | 'failed'

export interface Site {
  id: string
  tenantId: string
  name: string
  slug: string
  framework: Framework
  status: SiteStatus
  liveUrl: string | null
  repoPath: string | null
  createdAt: string
  updatedAt: string
}

export interface CreateSitePayload {
  name: string
  slug: string
  sourceType: 'upload' | 'git'
  repoUrl?: string
}

// ─── Deployments ─────────────────────────────────────────────────────────────

export type DeploymentStatus =
  | 'pending'
  | 'building'
  | 'testing'
  | 'deploying'
  | 'live'
  | 'failed'
  | 'rolled_back'

export interface Deployment {
  id: string
  siteId: string
  status: DeploymentStatus
  imageTag: string
  commitHash: string
  commitMessage: string
  liveUrl: string | null
  errorMessage: string | null
  createdAt: string
  completedAt: string | null
}

export interface CommitRecord {
  hash: string
  shortHash: string
  message: string
  timestamp: string
  deploymentId: string | null
}

// ─── Monitoring ──────────────────────────────────────────────────────────────

export type TimeRange = '1h' | '6h' | '24h' | '7d'

export interface SiteMetrics {
  requestRate: number
  errorRate: number
  p95LatencyMs: number
  activeConnections: number
  timestamps: string[]
  requestHistory: number[]
  errorHistory: number[]
}

export type LogLevel = 'INFO' | 'WARN' | 'ERROR' | 'DEBUG'

export interface LogEntry {
  timestamp: string
  level: LogLevel
  service: string
  message: string
  traceId: string | null
}

// ─── API Responses ────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface ApiError {
  detail: string
  code?: string
}
