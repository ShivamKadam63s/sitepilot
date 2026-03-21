#!/usr/bin/env bash
# bootstrap.sh — One command to stand up the entire SitePilot infrastructure
# Usage: bash infrastructure/scripts/bootstrap.sh
# Requires: terraform, ansible, multipass (all installed on host machine)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF_DIR="$ROOT/infrastructure/terraform"
ANSIBLE_DIR="$ROOT/infrastructure/ansible"

echo ""
echo "============================================"
echo "  SitePilot Infrastructure Bootstrap"
echo "============================================"
echo ""

# ── Step 1: Check prerequisites ───────────────────────────────────────────────
echo "[1/5] Checking prerequisites..."
for cmd in terraform ansible multipass; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' is not installed. Please install it first."
    exit 1
  fi
done
echo "  All prerequisites found."

# ── Step 2: Terraform — provision VMs ────────────────────────────────────────
echo ""
echo "[2/5] Provisioning VMs with Terraform..."
cd "$TF_DIR"

terraform init -upgrade
terraform apply -auto-approve

echo "  VMs provisioned."

# ── Step 3: Wait for VMs to be reachable ─────────────────────────────────────
echo ""
echo "[3/5] Waiting for VMs to be SSH-ready..."
sleep 20

CI_IP=$(terraform output -raw ci_ip)
K8S_IP=$(terraform output -raw k8s_ip)
TOOLS_IP=$(terraform output -raw tools_ip)

for ip in "$CI_IP" "$K8S_IP" "$TOOLS_IP"; do
  echo "  Waiting for $ip..."
  until ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
        ubuntu@"$ip" "echo ready" &>/dev/null; do
    sleep 5
  done
  echo "  $ip is ready."
done

# ── Step 4: Ansible — configure VMs ──────────────────────────────────────────
echo ""
echo "[4/5] Configuring VMs with Ansible..."
cd "$ANSIBLE_DIR"

ansible-playbook playbooks/site.yml -v

# ── Step 5: Print summary ─────────────────────────────────────────────────────
echo ""
echo "[5/5] Done!"
echo ""
echo "============================================"
echo "  Infrastructure is ready"
echo "============================================"
echo ""
echo "  CI/CD VM:     $CI_IP"
echo "    Jenkins:    http://$CI_IP:8080"
echo "    SonarQube:  http://$CI_IP:9000"
echo ""
echo "  K8s VM:       $K8S_IP"
echo "    Minikube dashboard: SSH in and run 'minikube dashboard'"
echo ""
echo "  Tools VM:     $TOOLS_IP"
echo "    Registry:   http://$TOOLS_IP:5000"
echo "    Grafana:    http://$TOOLS_IP:3001  (admin/admin)"
echo "    Prometheus: http://$TOOLS_IP:9090"
echo ""
echo "  Next step: Start local dev environment with:"
echo "    cd $ROOT && make dev"
echo ""
