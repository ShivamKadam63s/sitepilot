import os
import tempfile
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import Deployment, Site, User
from app.services.git_service import GitService
from app.services.docker_service import DockerService
from app.services.k8s_service import K8sService
from app.services.detection_service import detect_framework


class DeploymentService:

    def __init__(self, db: Session):
        self.db         = db
        self.git_svc    = GitService()
        self.docker_svc = DockerService()
        self.k8s_svc    = K8sService()

    def _append_log(self, deployment: Deployment, line: str) -> None:
        deployment.logs = (deployment.logs or "") + line + "\n"
        self.db.flush()

    def _set_status(self, deployment: Deployment, status: str) -> None:
        deployment.status = status
        self.db.flush()

    def trigger(
        self,
        site:        Site,
        user:        User,
        commit_hash: str | None = None,
    ) -> Deployment:
        """
        Create a Deployment record and run the full pipeline synchronously.
        In production this would be handed off to a background worker (Celery/RQ),
        but for the prototype it runs inline so the status is visible immediately.
        """
        dep = Deployment(
            site_id         = site.id,
            triggered_by_id = user.id,
            status          = "pending",
            image_tag       = "",
            commit_hash     = commit_hash or "",
            commit_message  = "",
        )
        self.db.add(dep)
        self.db.flush()

        try:
            self._run_pipeline(dep, site, commit_hash)
        except Exception as exc:
            dep.status        = "failed"
            dep.error_message = str(exc)
            dep.completed_at  = datetime.now(timezone.utc)
            site.status       = "failed"
            self.db.commit()

        return dep

    def _run_pipeline(
        self,
        dep:         Deployment,
        site:        Site,
        commit_hash: str | None,
    ) -> None:
        site.status = "deploying"
        self.db.flush()

        with tempfile.TemporaryDirectory() as work_dir:

            # ── Stage 1: Checkout source ──────────────────────────────────────
            self._set_status(dep, "building")
            self._append_log(dep, "[1/4] Checking out source code...")

            if not site.repo_path:
                raise RuntimeError("Site has no repository. Upload files first.")

            if self.git_svc.is_empty(site.repo_path):
                raise RuntimeError("Repository is empty. Upload files or commit changes first.")

            target = os.path.join(work_dir, "source")
            hash_to_use = commit_hash or "HEAD"
            self.git_svc.checkout(site.repo_path, hash_to_use, target)

            # Resolve the actual commit hash
            actual_hash = self._resolve_hash(site.repo_path, hash_to_use)
            dep.commit_hash = actual_hash
            dep.image_tag   = actual_hash[:12]
            self.db.flush()

            self._append_log(dep, f"[1/4] Checked out commit {actual_hash[:7]}")

            # ── Stage 2: Detect framework ─────────────────────────────────────
            framework = detect_framework(target)
            site.framework = framework
            self._append_log(dep, f"[2/4] Detected framework: {framework}")

            # ── Stage 3: Build Docker image ────────────────────────────────────
            self._set_status(dep, "building")
            self._append_log(dep, "[3/4] Building Docker image...")

            image_name = self.docker_svc.build_and_push(
                source_dir = target,
                tenant_id  = site.tenant_id,
                site_slug  = site.slug,
                image_tag  = dep.image_tag,
                framework  = framework,
            )
            self._append_log(dep, f"[3/4] Image pushed: {image_name}")

            # ── Stage 4: Deploy to Kubernetes ─────────────────────────────────
            self._set_status(dep, "deploying")
            self._append_log(dep, "[4/4] Deploying to Kubernetes...")

            self.k8s_svc.ensure_namespace(site.tenant_id[:8])
            live_url = self.k8s_svc.deploy_site(
                tenant_id  = site.tenant_id,
                site_slug  = site.slug,
                image_name = image_name,
            )

            self._append_log(dep, f"[4/4] Deployment live at {live_url}")

        # ── Done ──────────────────────────────────────────────────────────────
        dep.status       = "live"
        dep.live_url     = live_url
        dep.completed_at = datetime.now(timezone.utc)
        site.status      = "live"
        site.live_url    = live_url
        self.db.commit()

    def rollback(self, original: Deployment, user: User) -> Deployment:
        """Re-deploy a previous deployment's image tag."""
        site = original.site

        new_dep = Deployment(
            site_id         = site.id,
            triggered_by_id = user.id,
            status          = "deploying",
            image_tag       = original.image_tag,
            commit_hash     = original.commit_hash,
            commit_message  = f"Rollback to {original.commit_hash[:7]}",
        )
        self.db.add(new_dep)
        self.db.flush()

        try:
            self._append_log(new_dep, f"[rollback] Restoring image {original.image_tag}...")
            live_url = self.k8s_svc.deploy_site(
                tenant_id  = site.tenant_id,
                site_slug  = site.slug,
                image_name = f"{self._registry_url()}/{site.tenant_id[:8]}/{site.slug}:{original.image_tag}",
            )
            new_dep.status       = "live"
            new_dep.live_url     = live_url
            new_dep.completed_at = datetime.now(timezone.utc)
            site.status          = "live"
            site.live_url        = live_url
            self._append_log(new_dep, f"[rollback] Live at {live_url}")
        except Exception as exc:
            new_dep.status        = "failed"
            new_dep.error_message = str(exc)
            new_dep.completed_at  = datetime.now(timezone.utc)

        self.db.commit()
        return new_dep

    def _resolve_hash(self, repo_path: str, ref: str) -> str:
        import subprocess
        r = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=repo_path, capture_output=True, text=True,
        )
        return r.stdout.strip() if r.returncode == 0 else ref

    def _registry_url(self) -> str:
        from app.core.config import get_settings
        return get_settings().registry_url
