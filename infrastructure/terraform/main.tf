locals {
  # Cloud-init snippet installed on every VM
  common_packages = <<-EOF
    #cloud-config
    package_update: true
    packages:
      - curl
      - wget
      - git
      - python3
      - python3-pip
      - apt-transport-https
      - ca-certificates
      - gnupg
      - lsb-release
  EOF
}

# ── VM 1: CI/CD (Jenkins + SonarQube) ────────────────────────────────────────
resource "multipass_instance" "ci" {
  name   = "sitepilot-ci"
  cpus   = var.ci_cpus
  memory = var.ci_memory
  disk   = var.ci_disk
  image  = "22.04"

  cloudinit_file = local_file.ci_cloudinit.filename
}

resource "local_file" "ci_cloudinit" {
  filename = "${path.module}/cloud-init/ci.yml"
  content  = local.common_packages
}

# ── VM 2: Kubernetes (Minikube) ───────────────────────────────────────────────
resource "multipass_instance" "k8s" {
  name   = "sitepilot-k8s"
  cpus   = var.k8s_cpus
  memory = var.k8s_memory
  disk   = var.k8s_disk
  image  = "22.04"

  cloudinit_file = local_file.k8s_cloudinit.filename
}

resource "local_file" "k8s_cloudinit" {
  filename = "${path.module}/cloud-init/k8s.yml"
  content  = local.common_packages
}

# ── VM 3: Tools (Docker registry + monitoring) ────────────────────────────────
resource "multipass_instance" "tools" {
  name   = "sitepilot-tools"
  cpus   = var.tools_cpus
  memory = var.tools_memory
  disk   = var.tools_disk
  image  = "22.04"

  cloudinit_file = local_file.tools_cloudinit.filename
}

resource "local_file" "tools_cloudinit" {
  filename = "${path.module}/cloud-init/tools.yml"
  content  = local.common_packages
}

# ── Write Ansible inventory from Terraform outputs ────────────────────────────
resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../../ansible/inventory/hosts.yml"
  content  = templatefile("${path.module}/templates/hosts.yml.tpl", {
    ci_ip    = multipass_instance.ci.ipv4[0]
    k8s_ip   = multipass_instance.k8s.ipv4[0]
    tools_ip = multipass_instance.tools.ipv4[0]
  })
}
