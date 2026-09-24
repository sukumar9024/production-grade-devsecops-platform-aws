#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
environment="${1:?Specify dev, staging or prod}"
case "$environment" in dev|staging|prod) ;; *) exit 2 ;; esac
runtime_vars="${2:?Pass a private Ansible runtime YAML file}"
runtime_vars="$(python3 -c 'import pathlib,sys;print(pathlib.Path(sys.argv[1]).resolve())' "$runtime_vars")"
release_file="$PWD/reports/release-$environment.json"
cd infrastructure/ansible
if [ "${3:-}" = --rollback ]; then
  ansible-playbook -i "inventories/$environment/aws_ec2.yml" playbooks/rollback.yml -e "@$runtime_vars"
else
  ansible-playbook -i "inventories/$environment/aws_ec2.yml" playbooks/deploy.yml -e "@$runtime_vars" -e "@$release_file"
fi
