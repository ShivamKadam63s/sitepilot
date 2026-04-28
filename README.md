# SitePilot

A multi-tenant website deployment platform. Upload a site or point to a Git
repo — SitePilot detects the framework, builds a Docker image, and deploys it
to Kubernetes. Every site gets a live URL in minutes.

---

## Prerequisites

Install these on your Windows machine before starting.

| Tool | Version | Install |
|------|---------|---------|
| Node.js | 20+ | https://nodejs.org |
| Python | 3.11+ | https://python.org |
| Docker Desktop | latest | https://docker.com/products/docker-desktop |
| Git | latest | https://git-scm.com |
| Minikube | v1.32+ | https://minikube.sigs.k8s.io |
| kubectl | v1.29+ | https://kubernetes.io/docs/tasks/tools |
| Terraform | 1.6+ | https://developer.hashicorp.com/terraform |
| Ansible | 9+ | via WSL2: `pip install ansible` |
| Multipass | latest | https://multipass.run |

> **Windows users**: Ansible requires WSL2. All `make` commands work in Git
> Bash, WSL2, or PowerShell with GNU Make installed.

---

## Phase 1 — Verify prerequisites (Windows)

Open PowerShell or Git Bash and run each command:

```powershell
node  --version          # should print v20.x.x or higher
npm   --version          # should print 10.x.x or higher
python --version         # should print 3.11.x or higher
docker --version         # should print Docker version 24+
git   --version          # should print git version 2+
minikube version         # should print minikube version v1.32+
kubectl version --client # should print v1.29+
terraform --version      # should print Terraform v1.6+
```

If anything is missing, follow the install links in the table above.

---

## SitePilot Dev Environment (Recommended)

To avoid installing multiple tools on your host machine (especially **Ansible**, which requires WSL2 on Windows), we provide a pre-configured Ubuntu-based management container.

```bash
# 1. Build the environment image
docker build -t sitepilot-env ./docker/sitepilot-env

# 2. Run the environment container (mounts current directory and docker socket)
docker run -it --name sitepilot-manager \
  -v ${PWD}:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock \
  sitepilot-env
```

Inside this container, all tools (Terraform, Ansible, kubectl, Minikube, Node, Python) are pre-installed and ready to use for Phase 5 and Phase 6.

---

## Phase 2 — Project initialisation

```bash
# 1. Clone the repository
git clone <your-repo-url> sitepilot
cd sitepilot

# 2. Copy environment files
cp frontend/.env.example frontend/.env.development
cp backend/.env.example  backend/.env

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Install backend dependencies
cd backend
pip install -r requirements.txt -r requirements-dev.txt
cd ..
```

---

## Phase 3 — Start local development

```bash
# Start the full stack (PostgreSQL + Redis + API + Frontend)
docker compose up --build

# OR start services individually:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

Open http://localhost:3000 in your browser.

Default dev credentials (auto-seeded on first start):
- Email:    `admin@demo.com`
- Password: `password123`

---

## Phase 4 — Run tests

```bash
#Run it in project root directory
pytest tests/ -v --cov=app --cov-report=term-missing

# Frontend tests
cd frontend
npm run test

# Type check
npm run typecheck

# Lint
npm run lint
```

---

## Phase 5 — Kubernetes deployment (Minikube)

```bash
# Start Minikube
minikube start --driver=docker --cpus=4 --memory=6144

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Create namespaces
kubectl create namespace sitepilot-platform
kubectl create namespace tenants

# Apply platform manifests
kubectl apply -f kubernetes/platform/

# Check status
kubectl get pods -n sitepilot-platform

# Get Minikube IP (sites will be at {slug}.{ip}.nip.io)
minikube ip
```

---

## Phase 6 — Infrastructure with Terraform + Ansible

```bash
# One command provisions and configures all three VMs
bash infrastructure/scripts/bootstrap.sh

# To tear everything down
bash infrastructure/scripts/destroy.sh
```

---

## Project structure

```
sitepilot/
├── frontend/          React + TypeScript UI
├── backend/           FastAPI backend + services
├── kubernetes/        K8s manifests and Jinja2 templates
├── docker/            Compose file + Dockerfile templates
├── cicd/              Jenkinsfiles + SonarQube config
├── infrastructure/    Terraform + Ansible + scripts
├── monitoring/        Prometheus rules + Grafana dashboards
├── docs/              Architecture docs + runbooks
├── Makefile           Developer shortcuts
└── docker-compose.yml Local development stack
```

---

## Architecture

```
Browser → React frontend → FastAPI backend → PostgreSQL
                         ↓
                    Jenkins pipeline
                         ↓
              Docker build → Local registry
                         ↓
              kubectl apply → Minikube pod
                         ↓
              {slug}.{minikube-ip}.nip.io (live URL)
```

Infrastructure is provisioned by **Terraform** (Multipass VMs), configured
by **Ansible** (installs Docker, Jenkins, Minikube), and monitored by
**Prometheus + Grafana + Loki**.

---

## Useful commands

```bash
make dev              # start local stack
make test             # run all tests
make lint             # lint backend + frontend
make build            # build Docker images
make k8s-status       # show all platform pods
make minikube-dashboard  # open K8s dashboard in browser
make db-migrate       # run database migrations
make db-revision MSG="add users table"  # create new migration
```
