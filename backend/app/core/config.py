from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql://sitepilot:sitepilot@localhost:5432/sitepilot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "insecure-dev-key-change-in-production"
    access_token_expire_minutes: int = 60

    # Kubernetes
    k8s_namespace: str = "tenants"
    k8s_in_cluster: bool = False
    kubeconfig: str = "/root/.kube/config"

    # Docker
    registry_url: str = "localhost:5000"

    # Jenkins
    jenkins_url: str = "http://localhost:8080"
    jenkins_user: str = "admin"
    jenkins_token: str = "changeme"

    # Repos
    repos_base_path: str = "/data/repos"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
