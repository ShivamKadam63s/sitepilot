import os
import subprocess
import shutil
import tempfile
from app.core.config import get_settings

settings = get_settings()

# Maps detected framework → Dockerfile template filename
DOCKERFILE_TEMPLATES: dict[str, str] = {
    "react":   "react-app.Dockerfile",
    "nextjs":  "react-app.Dockerfile",
    "vue":     "react-app.Dockerfile",
    "flask":   "flask-app.Dockerfile",
    "fastapi": "fastapi-app.Dockerfile",
    "static":  "static-site.Dockerfile",
    "unknown": "static-site.Dockerfile",
}

TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "docker", "templates"
)


class DockerService:

    def _run(self, args: list[str], cwd: str | None = None) -> str:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"Docker command failed: {' '.join(args)}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result.stdout.strip()

    def _template_path(self, framework: str) -> str:
        filename = DOCKERFILE_TEMPLATES.get(framework, "static-site.Dockerfile")
        path = os.path.join(TEMPLATES_DIR, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dockerfile template not found: {path}")
        return path

    def build_and_push(
        self,
        source_dir: str,
        tenant_id:  str,
        site_slug:  str,
        image_tag:  str,
        framework:  str,
    ) -> str:
        """
        Build a Docker image for a tenant site and push to the local registry.
        Returns the full image reference  e.g. localhost:5000/abc123/mysite:a1b2c3d
        """
        image_name = (
            f"{settings.registry_url}/{tenant_id[:8]}/{site_slug}:{image_tag}"
        )

        with tempfile.TemporaryDirectory() as build_ctx:
            # Copy site files into build context
            shutil.copytree(source_dir, os.path.join(build_ctx, "site"),
                            dirs_exist_ok=True)

            # Copy the appropriate Dockerfile template
            template = self._template_path(framework)
            shutil.copy(template, os.path.join(build_ctx, "Dockerfile"))

            # Build
            self._run(
                ["docker", "build", "-t", image_name, "."],
                cwd=build_ctx,
            )

        # Push to local registry
        self._run(["docker", "push", image_name])

        return image_name

    def image_exists(self, image_name: str) -> bool:
        result = subprocess.run(
            ["docker", "image", "inspect", image_name],
            capture_output=True,
        )
        return result.returncode == 0
