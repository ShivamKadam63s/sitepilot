from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import get_settings
from app.api.routes import auth, sites, deployments, monitoring

settings = get_settings()

app = FastAPI(
    title       = "SitePilot API",
    description = "Multi-tenant site deployment platform",
    version     = "0.1.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.cors_origins_list,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Prometheus metrics (/metrics endpoint) ────────────────────────────────────
Instrumentator().instrument(app).expose(app)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(sites.router)
app.include_router(deployments.router)
app.include_router(monitoring.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "version": "0.1.0"}


# ── Startup: create DB tables (dev only) ─────────────────────────────────────
@app.on_event("startup")
def on_startup():
    if settings.app_env == "development":
        from app.core.database import engine, Base
        import app.models.models  # noqa: F401 — ensures models are registered
        Base.metadata.create_all(bind=engine)
        _seed_dev_data()


def _seed_dev_data() -> None:
    """Create a demo tenant + owner user if the DB is empty."""
    from app.core.database import SessionLocal
    from app.models.models import Tenant, User
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return  # already seeded

        tenant = Tenant(name="Demo Corp", plan="pro",
                        sites_allowed=10, storage_limit_mb=2048)
        db.add(tenant)
        db.flush()

        user = User(
            tenant_id       = tenant.id,
            email           = "admin@demo.com",
            name            = "Demo Admin",
            hashed_password = hash_password("password123"),
            role            = "owner",
        )
        db.add(user)
        db.commit()
        print("✓ Dev seed: admin@demo.com / password123")
    finally:
        db.close()
