import os
import subprocess
import tempfile
from jinja2 import Environment, FileSystemLoader
from app.core.config import get_settings

settings = get_settings()

TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "kubernetes", "templates"
)


class K8sService:

    def _run(self, args: list[str], input_text: str | None = None) -> str:
        result = subprocess.run(
            args,
            input=input_text,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"kubectl failed: {' '.join(args)}\n"
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
        return result.stdout.strip()

    def _render(self, template_name: str, context: dict) -> str:
        env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=False,
        )
        tmpl = env.get_template(template_name)
        return tmpl.render(**context)

    def _apply(self, manifest_yaml: str) -> None:
        self._run(["kubectl", "apply", "-f", "-"], input_text=manifest_yaml)

    def deploy_site(
        self,
        tenant_id:  str,
        site_slug:  str,
        image_name: str,
        namespace:  str = None,
    ) -> str:
        """
        Renders Deployment + Service + Ingress + HPA manifests for a tenant site
        and applies them. Returns the live URL.
        """
        ns = namespace or settings.k8s_namespace
        minikube_ip = self._get_minikube_ip()
        live_url    = f"http://{site_slug}.{minikube_ip}.nip.io"

        ctx = {
            "site_slug":  site_slug,
            "tenant_id":  tenant_id[:8],
            "image_name": image_name,
            "namespace":  ns,
            "live_url":   live_url,
        }

        for template in [
            "site-deployment.yml.j2",
            "site-service.yml.j2",
            "site-ingress.yml.j2",
            "site-hpa.yml.j2",
        ]:
            manifest = self._render(template, ctx)
            self._apply(manifest)

        # Wait for rollout (up to 3 minutes)
        self._run([
            "kubectl", "rollout", "status",
            f"deployment/{site_slug}",
            "-n", ns,
            "--timeout=180s",
        ])

        return live_url

    def rollback_site(self, site_slug: str, namespace: str = None) -> None:
        ns = namespace or settings.k8s_namespace
        self._run([
            "kubectl", "rollout", "undo",
            f"deployment/{site_slug}",
            "-n", ns,
        ])

    def delete_site(self, site_slug: str, namespace: str = None) -> None:
        ns = namespace or settings.k8s_namespace
        for resource in ["deployment", "service", "ingress", "hpa"]:
            try:
                self._run([
                    "kubectl", "delete", resource, site_slug,
                    "-n", ns, "--ignore-not-found",
                ])
            except RuntimeError:
                pass  # best-effort deletion

    def _get_minikube_ip(self) -> str:
        try:
            return self._run(["minikube", "ip"])
        except RuntimeError:
            return "127.0.0.1"

    def ensure_namespace(self, namespace: str) -> None:
        try:
            self._run(["kubectl", "get", "namespace", namespace])
        except RuntimeError:
            self._run(["kubectl", "create", "namespace", namespace])
