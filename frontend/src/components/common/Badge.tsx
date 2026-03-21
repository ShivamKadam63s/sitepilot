import { clsx } from 'clsx'
import type { DeploymentStatus, SiteStatus, LogLevel } from '@/types'

type BadgeVariant = 'success' | 'error' | 'warning' | 'info' | 'neutral'

interface BadgeProps {
  label: string
  variant?: BadgeVariant
  className?: string
}

const variantClasses: Record<BadgeVariant, string> = {
  success: 'bg-green-100 text-green-800',
  error:   'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info:    'bg-blue-100 text-blue-800',
  neutral: 'bg-gray-100 text-gray-700',
}

export function Badge({ label, variant = 'neutral', className }: BadgeProps) {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
        variantClasses[variant],
        className
      )}
    >
      {label}
    </span>
  )
}

// ── Convenience helpers ───────────────────────────────────────────────────────

export function DeploymentBadge({ status }: { status: DeploymentStatus }) {
  const map: Record<DeploymentStatus, { label: string; variant: BadgeVariant }> = {
    pending:     { label: 'Queued',       variant: 'neutral'  },
    building:    { label: 'Building',     variant: 'info'     },
    testing:     { label: 'Testing',      variant: 'warning'  },
    deploying:   { label: 'Deploying',    variant: 'info'     },
    live:        { label: 'Live',         variant: 'success'  },
    failed:      { label: 'Failed',       variant: 'error'    },
    rolled_back: { label: 'Rolled back',  variant: 'warning'  },
  }
  return <Badge {...map[status]} />
}

export function SiteBadge({ status }: { status: SiteStatus }) {
  const map: Record<SiteStatus, { label: string; variant: BadgeVariant }> = {
    draft:     { label: 'Draft',     variant: 'neutral' },
    deploying: { label: 'Deploying', variant: 'info'    },
    live:      { label: 'Live',      variant: 'success' },
    failed:    { label: 'Failed',    variant: 'error'   },
  }
  return <Badge {...map[status]} />
}

export function LogLevelBadge({ level }: { level: LogLevel }) {
  const map: Record<LogLevel, { label: string; variant: BadgeVariant }> = {
    DEBUG: { label: 'DEBUG', variant: 'neutral'  },
    INFO:  { label: 'INFO',  variant: 'info'     },
    WARN:  { label: 'WARN',  variant: 'warning'  },
    ERROR: { label: 'ERROR', variant: 'error'    },
  }
  return <Badge {...map[level]} />
}
