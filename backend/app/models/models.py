import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> str:
    return str(uuid.uuid4())


# ── Tenant ────────────────────────────────────────────────────────────────────

class Tenant(Base):
    __tablename__ = "tenants"

    id:               Mapped[str]  = mapped_column(String, primary_key=True, default=new_uuid)
    name:             Mapped[str]  = mapped_column(String(120), nullable=False)
    plan:             Mapped[str]  = mapped_column(
        Enum("free", "pro", "enterprise", name="plan_enum"), default="free"
    )
    sites_allowed:    Mapped[int]  = mapped_column(Integer, default=3)
    sites_used:       Mapped[int]  = mapped_column(Integer, default=0)
    storage_used_mb:  Mapped[int]  = mapped_column(Integer, default=0)
    storage_limit_mb: Mapped[int]  = mapped_column(Integer, default=500)
    created_at:       Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    users:   Mapped[list["User"]] = relationship("User",   back_populates="tenant")
    sites:   Mapped[list["Site"]] = relationship("Site",   back_populates="tenant")


# ── User ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id:              Mapped[str]  = mapped_column(String, primary_key=True, default=new_uuid)
    tenant_id:       Mapped[str]  = mapped_column(String, ForeignKey("tenants.id"), nullable=False)
    email:           Mapped[str]  = mapped_column(String(255), unique=True, nullable=False)
    name:            Mapped[str]  = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str]  = mapped_column(String, nullable=False)
    role:            Mapped[str]  = mapped_column(
        Enum("owner", "admin", "editor", name="role_enum"), default="editor"
    )
    is_active:       Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

    tenant:      Mapped["Tenant"]          = relationship("Tenant", back_populates="users")
    deployments: Mapped[list["Deployment"]] = relationship("Deployment", back_populates="triggered_by")


# ── Site ──────────────────────────────────────────────────────────────────────

class Site(Base):
    __tablename__ = "sites"

    id:         Mapped[str]  = mapped_column(String, primary_key=True, default=new_uuid)
    tenant_id:  Mapped[str]  = mapped_column(String, ForeignKey("tenants.id"), nullable=False)
    name:       Mapped[str]  = mapped_column(String(120), nullable=False)
    slug:       Mapped[str]  = mapped_column(String(80),  nullable=False)
    framework:  Mapped[str]  = mapped_column(String(40),  default="unknown")
    status:     Mapped[str]  = mapped_column(
        Enum("draft", "deploying", "live", "failed", name="site_status_enum"),
        default="draft",
    )
    live_url:   Mapped[str | None]  = mapped_column(String(500), nullable=True)
    repo_path:  Mapped[str | None]  = mapped_column(String(500), nullable=True)
    source_type: Mapped[str]        = mapped_column(String(20), default="upload")
    repo_url:   Mapped[str | None]  = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=now_utc)
    updated_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)

    tenant:      Mapped["Tenant"]          = relationship("Tenant", back_populates="sites")
    deployments: Mapped[list["Deployment"]] = relationship("Deployment", back_populates="site")


# ── Deployment ────────────────────────────────────────────────────────────────

class Deployment(Base):
    __tablename__ = "deployments"

    id:              Mapped[str]  = mapped_column(String, primary_key=True, default=new_uuid)
    site_id:         Mapped[str]  = mapped_column(String, ForeignKey("sites.id"), nullable=False)
    triggered_by_id: Mapped[str]  = mapped_column(String, ForeignKey("users.id"), nullable=False)
    status:          Mapped[str]  = mapped_column(
        Enum("pending","building","testing","deploying","live","failed","rolled_back",
             name="deploy_status_enum"),
        default="pending",
    )
    image_tag:       Mapped[str]         = mapped_column(String(200), nullable=False)
    commit_hash:     Mapped[str]         = mapped_column(String(80),  default="")
    commit_message:  Mapped[str]         = mapped_column(String(500), default="")
    live_url:        Mapped[str | None]  = mapped_column(String(500), nullable=True)
    error_message:   Mapped[str | None]  = mapped_column(Text, nullable=True)
    logs:            Mapped[str]         = mapped_column(Text, default="")
    created_at:      Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=now_utc)
    completed_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    site:         Mapped["Site"] = relationship("Site", back_populates="deployments")
    triggered_by: Mapped["User"] = relationship("User", back_populates="deployments")
