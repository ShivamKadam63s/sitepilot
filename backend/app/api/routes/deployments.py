from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Deployment, Site
from app.schemas.schemas import DeploymentCreate, DeploymentOut, LogsOut
from app.services.deployment_service import DeploymentService

router = APIRouter(prefix="/deployments", tags=["deployments"])


def _get_deployment_or_404(dep_id: str, db: Session, user: User) -> Deployment:
    dep = (
        db.query(Deployment)
        .join(Site, Deployment.site_id == Site.id)
        .filter(Deployment.id == dep_id, Site.tenant_id == user.tenant_id)
        .first()
    )
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return dep


@router.post("", response_model=DeploymentOut, status_code=201)
def create_deployment(
    payload: DeploymentCreate,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    # Verify the site belongs to this tenant
    site = db.query(Site).filter(
        Site.id == payload.site_id, Site.tenant_id == user.tenant_id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    svc = DeploymentService(db)
    deployment = svc.trigger(site=site, user=user, commit_hash=payload.commit_hash)
    return DeploymentOut.model_validate(deployment)


@router.get("")
def list_deployments(
    site_id: str     = Query(...),
    page:    int     = Query(1, ge=1),
    db:      Session = Depends(get_db),
    user:    User    = Depends(get_current_user),
):
    site = db.query(Site).filter(
        Site.id == site_id, Site.tenant_id == user.tenant_id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    page_size = 20
    offset    = (page - 1) * page_size
    deps = (
        db.query(Deployment)
        .filter(Deployment.site_id == site_id)
        .order_by(Deployment.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(Deployment).filter(Deployment.site_id == site_id).count()
    return {
        "items":     [DeploymentOut.model_validate(d) for d in deps],
        "total":     total,
        "page":      page,
        "page_size": page_size,
    }


@router.get("/{deployment_id}", response_model=DeploymentOut)
def get_deployment(
    deployment_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    dep = _get_deployment_or_404(deployment_id, db, user)
    return DeploymentOut.model_validate(dep)


@router.get("/{deployment_id}/logs", response_model=LogsOut)
def get_logs(
    deployment_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    dep  = _get_deployment_or_404(deployment_id, db, user)
    logs = [line for line in dep.logs.split("\n") if line.strip()]
    return LogsOut(logs=logs)


@router.post("/{deployment_id}/rollback", response_model=DeploymentOut)
def rollback_deployment(
    deployment_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    dep = _get_deployment_or_404(deployment_id, db, user)
    svc = DeploymentService(db)
    new_dep = svc.rollback(original=dep, user=user)
    return DeploymentOut.model_validate(new_dep)
