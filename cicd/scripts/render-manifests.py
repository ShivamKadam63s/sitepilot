#!/usr/bin/env python3
"""
Renders Jinja2 Kubernetes manifest templates for a tenant site deployment.
Called by Jenkinsfile.tenant during the 'Apply K8s manifests' stage.

Usage:
    python3 render-manifests.py \
        --site-slug mysite \
        --tenant-id abc12345 \
        --image-name localhost:5000/abc12345/mysite:a1b2c3 \
        --namespace abc12345 \
        --minikube-ip 192.168.64.10 \
        --output-dir /tmp/manifests-mysite
"""
import argparse
import os
import sys
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'kubernetes', 'templates'
)

TEMPLATES = [
    'site-deployment.yml.j2',
    'site-service.yml.j2',
    'site-ingress.yml.j2',
    'site-hpa.yml.j2',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site-slug',   required=True)
    parser.add_argument('--tenant-id',   required=True)
    parser.add_argument('--image-name',  required=True)
    parser.add_argument('--namespace',   required=True)
    parser.add_argument('--minikube-ip', required=True)
    parser.add_argument('--output-dir',  required=True)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
    )

    context = {
        'site_slug':   args.site_slug,
        'tenant_id':   args.tenant_id,
        'image_name':  args.image_name,
        'namespace':   args.namespace,
        'minikube_ip': args.minikube_ip,
    }

    for template_name in TEMPLATES:
        tmpl     = env.get_template(template_name)
        rendered = tmpl.render(**context)
        out_name = template_name.replace('.j2', '')
        out_path = os.path.join(args.output_dir, out_name)
        with open(out_path, 'w') as f:
            f.write(rendered)
        print(f"Rendered {out_path}")

    print(f"All manifests written to {args.output_dir}")


if __name__ == '__main__':
    main()
