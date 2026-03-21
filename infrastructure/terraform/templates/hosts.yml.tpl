all:
  children:
    ci_servers:
      hosts:
        sitepilot-ci:
          ansible_host: ${ci_ip}
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
    k8s_nodes:
      hosts:
        sitepilot-k8s:
          ansible_host: ${k8s_ip}
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
    tools_servers:
      hosts:
        sitepilot-tools:
          ansible_host: ${tools_ip}
          ansible_user: ubuntu
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
