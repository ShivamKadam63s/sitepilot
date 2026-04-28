from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Site, Tenant
from app.schemas.schemas import SiteCreate, SiteUpdate, SiteOut, CommitRequest, CommitOut
from app.services.git_service import GitService
from app.services.detection_service import detect_framework
import shutil, os, zipfile, tempfile

router = APIRouter(prefix="/sites", tags=["sites"])


def _get_site_or_404(site_id: str, db: Session, user: User) -> Site:
    site = db.query(Site).filter(
        Site.id == site_id, Site.tenant_id == user.tenant_id
    ).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.get("")
def list_sites(
    tenant_id: str = Query(...),
    db:         Session = Depends(get_db),
    user:       User    = Depends(get_current_user),
):
    if tenant_id != user.tenant_id and user.role not in ("owner", "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")
    sites = db.query(Site).filter(Site.tenant_id == tenant_id).all()
    return {"items": [SiteOut.model_validate(s) for s in sites],
            "total": len(sites), "page": 1, "page_size": len(sites)}


@router.post("", response_model=SiteOut, status_code=201)
def create_site(
    payload: SiteCreate,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    tenant: Tenant = user.tenant
    if tenant.sites_used >= tenant.sites_allowed:
        raise HTTPException(status_code=402, detail="Site limit reached for your plan")

    existing = db.query(Site).filter(
        Site.tenant_id == user.tenant_id, Site.slug == payload.slug
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already in use")

    git_svc   = GitService()
    if payload.source_type == "git" and payload.repo_url:
        repo_path = git_svc.clone_external(payload.repo_url, user.tenant_id, payload.slug)
    else:
        repo_path = git_svc.init_repo(user.tenant_id, payload.slug)

    site = Site(
        tenant_id   = user.tenant_id,
        name        = payload.name,
        slug        = payload.slug,
        source_type = payload.source_type,
        repo_url    = payload.repo_url,
        repo_path   = repo_path,
    )
    db.add(site)
    tenant.sites_used += 1
    db.commit()
    db.refresh(site)
    return SiteOut.model_validate(site)


@router.get("/{site_id}", response_model=SiteOut)
def get_site(
    site_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    return SiteOut.model_validate(_get_site_or_404(site_id, db, user))


@router.patch("/{site_id}", response_model=SiteOut)
def update_site(
    site_id: str,
    payload: SiteUpdate,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    site = _get_site_or_404(site_id, db, user)
    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(site, field, val)
    db.commit()
    db.refresh(site)
    return SiteOut.model_validate(site)


@router.delete("/{site_id}", status_code=204)
def delete_site(
    site_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    site = _get_site_or_404(site_id, db, user)
    user.tenant.sites_used = max(0, user.tenant.sites_used - 1)
    
    # Remove repo path if exists
    if site.repo_path and os.path.exists(site.repo_path):
        shutil.rmtree(site.repo_path, ignore_errors=True)

    db.delete(site)
    db.commit()


@router.post("/{site_id}/upload", status_code=204)
async def upload_zip(
    site_id: str,
    file: UploadFile = File(...),
    db:   Session    = Depends(get_db),
    user: User       = Depends(get_current_user),
):
    site = _get_site_or_404(site_id, db, user)
    if not site.repo_path:
        raise HTTPException(status_code=400, detail="Site has no repo path")

    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, "upload.zip")
        with open(zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        extract_dir = os.path.join(tmp, "extracted")
        os.makedirs(extract_dir)
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)

        framework = detect_framework(extract_dir)
        site.framework = framework

        git_svc = GitService()
        git_svc.add_files(site.repo_path, extract_dir)

    db.commit()


@router.post("/{site_id}/commit", response_model=CommitOut)
def commit_site(
    site_id: str,
    payload: CommitRequest,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    site = _get_site_or_404(site_id, db, user)
    if not site.repo_path:
        raise HTTPException(status_code=400, detail="No repo to commit to")

    git_svc = GitService()
    commit  = git_svc.commit(site.repo_path, payload.message, user.email)
    return commit


@router.get("/{site_id}/history", response_model=list[CommitOut])
def get_history(
    site_id: str,
    db:   Session = Depends(get_db),
    user: User    = Depends(get_current_user),
):
    site = _get_site_or_404(site_id, db, user)
    if not site.repo_path:
        return []
    git_svc = GitService()
    return git_svc.get_history(site.repo_path)
