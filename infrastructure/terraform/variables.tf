variable "ci_cpus" {
  description = "vCPUs for the CI/CD VM (Jenkins + SonarQube)"
  type        = number
  default     = 2
}

variable "ci_memory" {
  description = "RAM for the CI/CD VM"
  type        = string
  default     = "4G"
}

variable "ci_disk" {
  description = "Disk for the CI/CD VM"
  type        = string
  default     = "20G"
}

variable "k8s_cpus" {
  description = "vCPUs for the Kubernetes VM (Minikube)"
  type        = number
  default     = 4
}

variable "k8s_memory" {
  description = "RAM for the Kubernetes VM"
  type        = string
  default     = "8G"
}

variable "k8s_disk" {
  description = "Disk for the Kubernetes VM"
  type        = string
  default     = "30G"
}

variable "tools_cpus" {
  description = "vCPUs for the tools VM (registry + monitoring)"
  type        = number
  default     = 2
}

variable "tools_memory" {
  description = "RAM for the tools VM"
  type        = string
  default     = "3G"
}

variable "tools_disk" {
  description = "Disk for the tools VM"
  type        = string
  default     = "15G"
}
