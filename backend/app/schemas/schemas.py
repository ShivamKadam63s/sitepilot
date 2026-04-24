from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
import re


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut
    tenant:       TenantOut


# ── Tenant ────────────────────────────────────────────────────────────────────

class TenantOut(BaseModel):
    id:               str
    name:             str
    plan:             str
    sites_allowed:    int
    sites_used:       int
    storage_used_mb:  int
    storage_limit_mb: int

    model_config = {"from_attributes": True}


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id:        str
    email:     str
    name:      str
    role:      str
    tenant_id: str

    model_config = {"from_attributes": True}


# ── Sites ─────────────────────────────────────────────────────────────────────

class SiteCreate(BaseModel):
    name:        str
    slug:        str
    source_type: str = "upload"
    repo_url:    Optional[str] = None

    @field_validator("slug")
    @classmethod
    def slug_valid(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug may only contain lowercase letters, digits, and hyphens")
        return v


class SiteUpdate(BaseModel):
    name:   Optional[str] = None
    status: Optional[str] = None


class SiteOut(BaseModel):
    id:          str
    tenant_id:   str
    name:        str
    slug:        str
    framework:   str
    status:      str
    live_url:    Optional[str]
    repo_path:   Optional[str]
    source_type: str
    repo_url:    Optional[str]
    created_at:  datetime
    updated_at:  datetime

    model_config = {"from_attributes": True}


class CommitRequest(BaseModel):
    message: str


class CommitOut(BaseModel):
    hash:          str
    short_hash:    str
    message:       str
    timestamp:     str
    deployment_id: Optional[str]


# ── Deployments ───────────────────────────────────────────────────────────────

class DeploymentCreate(BaseModel):
    site_id:     str
    commit_hash: Optional[str] = None


class DeploymentOut(BaseModel):
    id:              str
    site_id:         str
    triggered_by_id: str
    status:          str
    image_tag:       str
    commit_hash:     str
    commit_message:  str
    live_url:        Optional[str]
    error_message:   Optional[str]
    logs:            str
    created_at:      datetime
    completed_at:    Optional[datetime]

    model_config = {"from_attributes": True}


class LogsOut(BaseModel):
    logs: list[str]


# ── Monitoring ────────────────────────────────────────────────────────────────

class MetricsOut(BaseModel):
    request_rate:    float
class MetricsOut(BaseModel):
    request_count:      int
    error_rate:         float
    p95_latency_ms:     int
    active_connections: int
    timestamps:         list[str]
    request_history:    list[float]
    error_history:      list[float]


class LogEntryOut(BaseModel):
    timestamp: str
    level:     str
    service:   str
    message:   str
    trace_id:  Optional[str]


# ── Pagination ────────────────────────────────────────────────────────────────

class Paginated(BaseModel):
    items:     list
    total:     int
    page:      int
    page_size: int
