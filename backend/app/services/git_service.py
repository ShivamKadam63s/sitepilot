import os
import subprocess
import shutil
from datetime import datetime, timezone
from app.core.config import get_settings

settings = get_settings()


class GitService:

    def _run(self, args: list[str], cwd: str | None = None) -> str:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Git command failed: {' '.join(args)}\n{result.stderr}"
            )
        return result.stdout.strip()

    def _repo_path(self, tenant_id: str, slug: str) -> str:
        return os.path.join(settings.repos_base_path, tenant_id, f"{slug}.git")

    def init_repo(self, tenant_id: str, slug: str) -> str:
        """Initialise a bare Git repository and return its path."""
        path = self._repo_path(tenant_id, slug)
        os.makedirs(path, exist_ok=True)
        self._run(["git", "init", "--bare"], cwd=path)
        return path

    def add_files(self, repo_path: str, source_dir: str) -> None:
        """
        Copy files from source_dir into a temporary working tree,
        stage everything, and create an initial commit.
        """
        work_dir = repo_path.rstrip("/") + "_work"
        try:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
            self._run(["git", "clone", repo_path, work_dir])

            # Copy source files into work tree
            for item in os.listdir(source_dir):
                src = os.path.join(source_dir, item)
                dst = os.path.join(work_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

            self._run(["git", "add", "-A"], cwd=work_dir)
            self._run(
                ["git", "-c", "user.email=platform@sitepilot",
                 "-c", "user.name=SitePilot",
                 "commit", "-m", "Upload site files"],
                cwd=work_dir,
            )
            self._run(["git", "push", "origin", "main"], cwd=work_dir)
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)

    def commit(self, repo_path: str, message: str, author_email: str) -> dict:
        """Stage all changes and create a named commit."""
        work_dir = repo_path.rstrip("/") + "_work"
        try:
            if not os.path.exists(work_dir):
                self._run(["git", "clone", repo_path, work_dir])

            self._run(["git", "add", "-A"], cwd=work_dir)
            self._run(
                ["git", "-c", f"user.email={author_email}",
                 "-c", "user.name=SitePilot User",
                 "commit", "-m", message, "--allow-empty"],
                cwd=work_dir,
            )
            self._run(["git", "push", "origin", "main"], cwd=work_dir)

            full_hash  = self._run(["git", "rev-parse", "HEAD"], cwd=work_dir)
            short_hash = full_hash[:7]
            return {
                "hash":          full_hash,
                "short_hash":    short_hash,
                "message":       message,
                "timestamp":     datetime.now(timezone.utc).isoformat(),
                "deployment_id": None,
            }
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)

    def get_history(self, repo_path: str) -> list[dict]:
        """Return last 20 commits as dicts."""
        if not os.path.exists(repo_path):
            return []
        try:
            raw = self._run(
                ["git", "log", "--pretty=format:%H|%h|%s|%aI", "-n", "20"],
                cwd=repo_path,
            )
            if not raw:
                return []
            results = []
            for line in raw.splitlines():
                parts = line.split("|", 3)
                if len(parts) == 4:
                    results.append({
                        "hash":          parts[0],
                        "short_hash":    parts[1],
                        "message":       parts[2],
                        "timestamp":     parts[3],
                        "deployment_id": None,
                    })
            return results
        except RuntimeError:
            return []

    def checkout(self, repo_path: str, commit_hash: str, target_dir: str) -> None:
        """Checkout a specific commit into target_dir."""
        work_dir = repo_path.rstrip("/") + "_work"
        try:
            if not os.path.exists(work_dir):
                self._run(["git", "clone", repo_path, work_dir])
            self._run(["git", "checkout", commit_hash], cwd=work_dir)
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(work_dir, target_dir)
        finally:
            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
