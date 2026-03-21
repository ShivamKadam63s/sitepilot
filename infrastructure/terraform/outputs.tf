output "ci_ip" {
  description = "IP address of the CI/CD VM"
  value       = multipass_instance.ci.ipv4[0]
}

output "k8s_ip" {
  description = "IP address of the Kubernetes VM"
  value       = multipass_instance.k8s.ipv4[0]
}

output "tools_ip" {
  description = "IP address of the tools VM"
  value       = multipass_instance.tools.ipv4[0]
}

output "vm_summary" {
  description = "All VM IPs in one object"
  value = {
    ci    = multipass_instance.ci.ipv4[0]
    k8s   = multipass_instance.k8s.ipv4[0]
    tools = multipass_instance.tools.ipv4[0]
  }
}
