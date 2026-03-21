from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Site
from app.schemas.schemas import MetricsOut, LogEntryOut
from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


def _assert_site_access(site_id: str, db: Session, user: User) -> Site:
    site = db.query(Site).filter(
        Site.id == site_id, Site.tenant_id == user.tenant_id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("/metrics/{site_id}", response_model=MetricsOut)
def get_metrics(
    site_id: str,
    range:   str     = Query("1h", pattern=r"^(1h|6h|24h|7d)$"),
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    site = _assert_site_access(site_id, db, user)
    svc  = MonitoringService()
    return svc.get_metrics(site_slug=site.slug, time_range=range)


@router.get("/logs/{site_id}", response_model=list[LogEntryOut])
def get_logs(
    site_id: str,
    level:   str | None = Query(None),
    search:  str | None = Query(None),
    db:      Session    = Depends(get_db),
    user:    User       = Depends(get_current_user),
):
    site = _assert_site_access(site_id, db, user)
    svc  = MonitoringService()
    return svc.get_logs(site_slug=site.slug, level=level, search=search)
