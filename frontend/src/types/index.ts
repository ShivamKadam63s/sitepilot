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
  access_token: string
  token_type: string
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
  tenantId?: string
  tenant_id?: string
  name: string
  slug: string
  framework: Framework
  status: SiteStatus
  liveUrl?: string | null
  live_url?: string | null
  repoPath?: string | null
  repo_path?: string | null
  sourceType?: string
  source_type?: string
  repoUrl?: string | null
  repo_url?: string | null
  createdAt?: string
  created_at?: string
  updatedAt?: string
  updated_at?: string
}

export interface CreateSitePayload {
  name: string
  slug: string
  sourceType?: 'upload' | 'git'
  source_type?: 'upload' | 'git'
  repoUrl?: string
  repo_url?: string
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
  siteId?: string
  site_id?: string
  triggeredById?: string
  triggered_by_id?: string
  status: DeploymentStatus
  imageTag?: string
  image_tag?: string
  commitHash?: string
  commit_hash?: string
  commitMessage?: string
  commit_message?: string
  liveUrl?: string | null
  live_url?: string | null
  errorMessage?: string | null
  error_message?: string | null
  logs?: string
  createdAt?: string
  created_at?: string
  completedAt?: string | null
  completed_at?: string | null
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
  requestRate?: number
  request_rate?: number
  errorRate?: number
  error_rate?: number
  p95LatencyMs?: number
  p95_latency_ms?: number
  activeConnections?: number
  active_connections?: number
  timestamps: string[]
  requestHistory?: number[]
  request_history?: number[]
  errorHistory?: number[]
  error_history?: number[]
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
