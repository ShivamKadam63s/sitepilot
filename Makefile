.PHONY: help dev dev-down test lint typecheck build infra destroy deploy clean

# ── Help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "SitePilot — available commands"
	@echo "--------------------------------"
	@echo "  make dev         Start full local stack (Docker Compose)"
	@echo "  make dev-down    Stop local stack"
	@echo "  make test        Run all tests (backend + frontend)"
	@echo "  make lint        Run all linters"
	@echo "  make typecheck   TypeScript type check"
	@echo "  make build       Build all Docker images"
	@echo "  make infra       Provision + configure all VMs (Terraform + Ansible)"
	@echo "  make destroy     Tear down all VMs"
	@echo "  make clean       Remove build artefacts"
	@echo ""

# ── Local development ─────────────────────────────────────────────────────────
dev:
	docker compose up --build

dev-down:
	docker compose down

dev-logs:
	docker compose logs -f api frontend

# ── Testing ───────────────────────────────────────────────────────────────────
test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && \
	  pip install -q -r requirements.txt -r requirements-dev.txt && \
	  pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm ci && npm run test

# ── Linting ───────────────────────────────────────────────────────────────────
lint: lint-backend lint-frontend

lint-backend:
	cd backend && \
	  pip install -q flake8 black isort && \
	  flake8 app/ --max-line-length=100 --exclude=alembic/ && \
	  black --check app/ && \
	  isort --check-only app/

lint-frontend:
	cd frontend && npm run lint

typecheck:
	cd frontend && npm run typecheck

# ── Build ─────────────────────────────────────────────────────────────────────
build:
	docker build -t localhost:5000/sitepilot/api:local ./backend
	docker build -t localhost:5000/sitepilot/frontend:local ./frontend

# ── Infrastructure ────────────────────────────────────────────────────────────
infra:
	bash infrastructure/scripts/bootstrap.sh

destroy:
	bash infrastructure/scripts/destroy.sh

# ── Kubernetes helpers ────────────────────────────────────────────────────────
k8s-apply:
	kubectl apply -f kubernetes/platform/

k8s-status:
	kubectl get pods -n sitepilot-platform

k8s-logs-api:
	kubectl logs -l app=sitepilot-api -n sitepilot-platform -f

minikube-dashboard:
	minikube dashboard

# ── Database migrations ───────────────────────────────────────────────────────
db-migrate:
	cd backend && alembic upgrade head

db-rollback:
	cd backend && alembic downgrade -1

db-revision:
	cd backend && alembic revision --autogenerate -m "$(MSG)"

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/coverage backend/coverage.xml backend/test.db
	docker system prune -f 2>/dev/null || true
