#!/usr/bin/env bash
# destroy.sh — Tears down all SitePilot infrastructure VMs
# Usage: bash infrastructure/scripts/destroy.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TF_DIR="$ROOT/infrastructure/terraform"

echo ""
echo "============================================"
echo "  SitePilot Infrastructure Teardown"
echo "============================================"
echo ""
echo "WARNING: This will permanently delete all three VMs"
echo "  - sitepilot-ci    (Jenkins + SonarQube)"
echo "  - sitepilot-k8s   (Minikube)"
echo "  - sitepilot-tools (Registry + Monitoring)"
echo ""
read -r -p "Are you sure? Type 'yes' to confirm: " confirm

if [[ "$confirm" != "yes" ]]; then
  echo "Cancelled."
  exit 0
fi

echo ""
echo "Destroying VMs with Terraform..."
cd "$TF_DIR"
terraform destroy -auto-approve

echo ""
echo "All VMs have been destroyed."
echo "Run bootstrap.sh to recreate the environment."
